import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json

from utils.document_processor import document_processor
from config import GEMINI_API_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RAGSystem:
    """Retrieval Augmented Generation system for document chat"""
    
    def __init__(self):
        self.document_processor = document_processor
        self.conversation_memory = {}  # Store conversation context
        
    def prepare_context(self, relevant_chunks: List[Dict], max_context_length: int = 4000) -> str:
        """Prepare context from relevant document chunks"""
        context_parts = []
        current_length = 0
        
        # Sort chunks by similarity score (highest first)
        sorted_chunks = sorted(
            relevant_chunks, 
            key=lambda x: x.get('similarity_score', 0), 
            reverse=True
        )
        
        for chunk in sorted_chunks:
            chunk_text = chunk.get('text', '')
            chunk_length = len(chunk_text)
            
            # Check if adding this chunk would exceed max length
            if current_length + chunk_length > max_context_length:
                # If we haven't added any chunks yet, add this one truncated
                if not context_parts:
                    remaining_space = max_context_length - current_length
                    truncated_text = chunk_text[:remaining_space]
                    context_parts.append(f"Document excerpt: {truncated_text}...")
                break
            
            context_parts.append(f"Document excerpt: {chunk_text}")
            current_length += chunk_length
        
        return "\n\n".join(context_parts)
    
    def create_system_prompt(self, context: str) -> str:
        """Create system prompt for document chat"""
        return f"""You are an AI assistant that helps users understand and analyze documents. You have access to the following document content:

{context}

Instructions:
1. Answer questions based on the provided document content
2. If the answer is not in the document, clearly state that
3. Provide specific quotes or references when possible
4. Be concise but comprehensive in your responses
5. If asked about something not in the document, suggest what the user might want to ask instead
6. Maintain a helpful and professional tone

Always base your responses on the document content provided above."""
    
    def format_conversation_history(self, conversation_history: List[Dict], max_history: int = 5) -> str:
        """Format recent conversation history for context"""
        if not conversation_history:
            return ""
        
        # Get recent messages (excluding current query)
        recent_messages = conversation_history[-max_history:] if len(conversation_history) > max_history else conversation_history
        
        formatted_history = []
        for message in recent_messages:
            role = message.get('role', 'user')
            content = message.get('content', '')
            timestamp = message.get('timestamp', '')
            
            if role == 'user':
                formatted_history.append(f"User: {content}")
            elif role == 'assistant':
                formatted_history.append(f"Assistant: {content}")
        
        if formatted_history:
            return "Previous conversation:\n" + "\n".join(formatted_history) + "\n\n"
        
        return ""
    
    def generate_response(self, query: str, document_chunks: List[Dict], 
                         conversation_history: List[Dict] = None) -> Dict:
        """Generate response using RAG approach"""
        try:
            # Find relevant chunks
            relevant_chunks = self.document_processor.search_similar_chunks(
                query=query,
                chunks=document_chunks,
                top_k=5
            )
            
            if not relevant_chunks:
                return {
                    'response': "I couldn't find relevant information in the document to answer your question. Could you please rephrase your question or ask about a different topic from the document?",
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Prepare context from relevant chunks
            context = self.prepare_context(relevant_chunks)
            
            # Create system prompt
            system_prompt = self.create_system_prompt(context)
            
            # Format conversation history
            history_text = ""
            if conversation_history:
                history_text = self.format_conversation_history(conversation_history)
            
            # Create the final prompt
            full_prompt = f"{system_prompt}\n\n{history_text}User question: {query}\n\nPlease provide a helpful response based on the document content:"
            
            # Generate response using the existing query_gemini function
            from app import query_gemini
            ai_response = query_gemini(full_prompt)
            
            if not ai_response:
                return {
                    'response': "I'm sorry, I encountered an error while processing your question. Please try again.",
                    'sources': [],
                    'confidence': 0.0
                }
            
            # Calculate confidence based on similarity scores
            avg_similarity = sum(chunk.get('similarity_score', 0) for chunk in relevant_chunks) / len(relevant_chunks)
            confidence = min(avg_similarity * 100, 95)  # Cap at 95%
            
            # Prepare source information
            sources = []
            for chunk in relevant_chunks[:3]:  # Top 3 sources
                sources.append({
                    'chunk_id': chunk.get('id'),
                    'text_preview': chunk.get('text', '')[:200] + "..." if len(chunk.get('text', '')) > 200 else chunk.get('text', ''),
                    'similarity_score': chunk.get('similarity_score', 0),
                    'token_count': chunk.get('token_count', 0)
                })
            
            return {
                'response': ai_response,
                'sources': sources,
                'confidence': confidence,
                'relevant_chunks_count': len(relevant_chunks)
            }
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return {
                'response': "I'm sorry, I encountered an error while processing your question. Please try again.",
                'sources': [],
                'confidence': 0.0
            }
    
    def store_conversation_message(self, document_id: str, role: str, content: str, 
                                 sources: List[Dict] = None) -> Dict:
        """Store conversation message"""
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.utcnow().isoformat(),
            'sources': sources or []
        }
        
        # Initialize conversation if it doesn't exist
        if document_id not in self.conversation_memory:
            self.conversation_memory[document_id] = []
        
        # Add message to conversation
        self.conversation_memory[document_id].append(message)
        
        # Keep only last 20 messages to prevent memory issues
        if len(self.conversation_memory[document_id]) > 20:
            self.conversation_memory[document_id] = self.conversation_memory[document_id][-20:]
        
        return message
    
    def get_conversation_history(self, document_id: str) -> List[Dict]:
        """Get conversation history for a document"""
        return self.conversation_memory.get(document_id, [])
    
    def clear_conversation_history(self, document_id: str):
        """Clear conversation history for a document"""
        if document_id in self.conversation_memory:
            del self.conversation_memory[document_id]
    
    def suggest_questions(self, document_chunks: List[Dict], limit: int = 5) -> List[str]:
        """Suggest relevant questions based on document content"""
        try:
            if not document_chunks:
                return []
            
            # Sample content from different chunks
            sample_texts = []
            for i, chunk in enumerate(document_chunks):
                if i >= 10:  # Don't process too many chunks
                    break
                text = chunk.get('text', '')[:300]  # First 300 chars
                if text:
                    sample_texts.append(text)
            
            if not sample_texts:
                return []
            
            # Create prompt for question generation
            content_sample = "\n\n".join(sample_texts)
            prompt = f"""Based on the following document content, suggest {limit} relevant questions that a user might want to ask about this document. The questions should be specific and answerable from the content provided.

Document content:
{content_sample}

Please provide {limit} questions, one per line, without numbering or bullet points:"""
            
            # Generate suggestions using the existing query_gemini function
            from app import query_gemini
            response = query_gemini(prompt)
            
            if response:
                # Parse the response into individual questions
                questions = [q.strip() for q in response.split('\n') if q.strip()]
                # Filter out empty questions and take only the requested number
                questions = [q for q in questions if len(q) > 10][:limit]
                return questions
            
            return []
            
        except Exception as e:
            logger.error(f"Error generating question suggestions: {str(e)}")
            return []
    
    def summarize_document(self, document_chunks: List[Dict], max_length: int = 500) -> str:
        """Generate a summary of the document"""
        try:
            if not document_chunks:
                return "No content available to summarize."
            
            # Take first few chunks for summary (usually contains introduction/overview)
            summary_chunks = document_chunks[:5]
            content_for_summary = "\n\n".join([chunk.get('text', '') for chunk in summary_chunks])
            
            # Limit content length for summary
            if len(content_for_summary) > 3000:
                content_for_summary = content_for_summary[:3000] + "..."
            
            prompt = f"""Please provide a concise summary of the following document content in approximately {max_length} characters or less. Focus on the main topics, key findings, and overall purpose of the document.

Document content:
{content_for_summary}

Summary:"""
            
            # Generate summary using the existing query_gemini function
            from app import query_gemini
            summary = query_gemini(prompt)
            
            return summary if summary else "Unable to generate summary."
            
        except Exception as e:
            logger.error(f"Error generating document summary: {str(e)}")
            return "Error generating summary."
    
    def analyze_document_topics(self, document_chunks: List[Dict]) -> List[str]:
        """Extract main topics from the document"""
        try:
            if not document_chunks:
                return []
            
            # Combine text from chunks for topic analysis
            all_text = " ".join([chunk.get('text', '') for chunk in document_chunks[:10]])
            
            # Limit text length
            if len(all_text) > 2000:
                all_text = all_text[:2000]
            
            prompt = f"""Analyze the following text and identify the main topics or themes. Return a list of 5-8 key topics, each as a short phrase (2-4 words).

Text:
{all_text}

Main topics (one per line):"""
            
            # Generate topics using the existing query_gemini function
            from app import query_gemini
            response = query_gemini(prompt)
            
            if response:
                topics = [topic.strip() for topic in response.split('\n') if topic.strip()]
                # Clean up topics and return top ones
                clean_topics = [topic for topic in topics if len(topic) > 3 and len(topic) < 50]
                return clean_topics[:8]
            
            return []
            
        except Exception as e:
            logger.error(f"Error analyzing document topics: {str(e)}")
            return []

# Create global RAG system instance
rag_system = RAGSystem() 