from celery import Celery
import os
import logging
from datetime import datetime
from bson import ObjectId

from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from utils.document_processor import document_processor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    'sentino_ai',
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=['celery_app']
)

# Celery configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)

# Task routing
celery_app.conf.task_routes = {
    'celery_app.process_document_task': {'queue': 'document_processing'},
    'celery_app.generate_embeddings_task': {'queue': 'embedding_generation'},
}

@celery_app.task(bind=True, name='celery_app.process_document_task')
def process_document_task(self, document_id, file_path, user_id, filename):
    """Background task for processing documents"""
    try:
        from pymongo import MongoClient
        from config import MONGODB_URI
        
        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Starting document processing', 'progress': 10}
        )
        
        # Connect to MongoDB
        client = MongoClient(MONGODB_URI)
        db = client.sentino_ai
        
        logger.info(f"Processing document {document_id} for user {user_id}")
        
        # Read the file from disk
        with open(file_path, 'rb') as file:
            # Create a file-like object for the processor
            class FileWrapper:
                def __init__(self, file_path, filename):
                    self.file_path = file_path
                    self.filename = filename
                    self._content = None
                
                def read(self):
                    if self._content is None:
                        with open(self.file_path, 'rb') as f:
                            self._content = f.read()
                    return self._content
                
                def seek(self, pos, whence=0):
                    pass  # For compatibility
                
                def tell(self):
                    return len(self.read()) if self._content else 0
            
            file_wrapper = FileWrapper(file_path, filename)
            
            # Update progress
            self.update_state(
                state='PROCESSING',
                meta={'status': 'Extracting text from document', 'progress': 30}
            )
            
            # Process the document
            document_data = document_processor.process_document(file_wrapper, user_id)
            
            # Update progress
            self.update_state(
                state='PROCESSING',
                meta={'status': 'Generating embeddings', 'progress': 70}
            )
            
            # Save to database
            document_data['_id'] = ObjectId(document_id)
            document_data['created_at'] = datetime.utcnow()
            document_data['updated_at'] = datetime.utcnow()
            
            # Insert or update document
            db.document_context.replace_one(
                {'_id': ObjectId(document_id)},
                document_data,
                upsert=True
            )
            
            # Clean up temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update progress
            self.update_state(
                state='SUCCESS',
                meta={'status': 'Document processed successfully', 'progress': 100}
            )
            
            logger.info(f"Document {document_id} processed successfully")
            
            return {
                'status': 'completed',
                'document_id': document_id,
                'total_chunks': document_data['total_chunks'],
                'total_tokens': document_data['total_tokens']
            }
            
    except Exception as e:
        logger.error(f"Error processing document {document_id}: {str(e)}")
        
        # Update task status with error
        self.update_state(
            state='FAILURE',
            meta={'status': f'Error: {str(e)}', 'progress': 0}
        )
        
        # Clean up file on error
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
        except:
            pass
        
        raise e

@celery_app.task(bind=True, name='celery_app.generate_embeddings_task')
def generate_embeddings_task(self, chunks, document_id):
    """Background task for generating embeddings for existing chunks"""
    try:
        from pymongo import MongoClient
        from config import MONGODB_URI
        
        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Generating embeddings for chunks', 'progress': 10}
        )
        
        # Generate embeddings
        chunks_with_embeddings = document_processor.generate_embeddings(chunks)
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Saving embeddings to database', 'progress': 80}
        )
        
        # Update database
        client = MongoClient(MONGODB_URI)
        db = client.sentino_ai
        
        db.document_context.update_one(
            {'_id': ObjectId(document_id)},
            {
                '$set': {
                    'chunks': chunks_with_embeddings,
                    'embedding_processed': True,
                    'updated_at': datetime.utcnow()
                }
            }
        )
        
        self.update_state(
            state='SUCCESS',
            meta={'status': 'Embeddings generated successfully', 'progress': 100}
        )
        
        return {
            'status': 'completed',
            'document_id': document_id,
            'chunks_processed': len(chunks_with_embeddings)
        }
        
    except Exception as e:
        logger.error(f"Error generating embeddings for document {document_id}: {str(e)}")
        
        self.update_state(
            state='FAILURE',
            meta={'status': f'Error: {str(e)}', 'progress': 0}
        )
        
        raise e

@celery_app.task(name='celery_app.cleanup_temp_files')
def cleanup_temp_files():
    """Periodic task to clean up temporary files"""
    try:
        temp_dir = 'temp_uploads'
        if not os.path.exists(temp_dir):
            return
        
        cutoff_time = datetime.now().timestamp() - 3600  # 1 hour ago
        
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path) and os.path.getctime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up temporary file: {filename}")
                except Exception as e:
                    logger.error(f"Error cleaning up file {filename}: {str(e)}")
                    
    except Exception as e:
        logger.error(f"Error in cleanup task: {str(e)}")

# Periodic tasks
celery_app.conf.beat_schedule = {
    'cleanup-temp-files': {
        'task': 'celery_app.cleanup_temp_files',
        'schedule': 3600.0,  # Run every hour
    },
}

if __name__ == '__main__':
    celery_app.start() 