import hashlib
import random
from PIL import Image, ImageDraw
import io
import os
from werkzeug.utils import secure_filename
import logging

# Get the absolute path for the upload folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads', 'avatars')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
AVATAR_SIZE = (200, 200)
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
COLORS = [
    '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
    '#D4A5A5', '#9B59B6', '#3498DB', '#1ABC9C', '#F1C40F'
]

def ensure_upload_folder():
    """Ensure the upload folder exists"""
    try:
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Failed to create upload folder: {e}")
        return False

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_random_avatar(username, size=AVATAR_SIZE):
    """Generate a random avatar based on username"""
    try:
        # Create a hash of the username for consistent colors
        hash_object = hashlib.md5(username.encode())
        hash_hex = hash_object.hexdigest()
        
        # Use hash to select consistent colors
        background_color = COLORS[int(hash_hex[0], 16) % len(COLORS)]
        
        # Create new image with background color
        img = Image.new('RGB', size, background_color)
        draw = ImageDraw.Draw(img)
        
        # Get initials from username
        initials = username[0].upper() if username else '?'
        
        # Calculate font size (approximately 50% of avatar size)
        font_size = int(min(size) * 0.5)
        
        # Calculate text position to center it
        text_width = font_size * 0.6  # Approximate width of one character
        text_height = font_size * 0.7  # Approximate height of one character
        x = (size[0] - text_width) / 2
        y = (size[1] - text_height) / 2
        
        # Draw text
        draw.text((x, y), initials, fill='white', font_size=font_size)
        
        # Convert to bytes
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        
        return img_byte_arr
    except Exception as e:
        logging.error(f"Failed to generate random avatar: {e}")
        return None

def cleanup_old_avatar(username):
    """Remove old avatar files for the user"""
    try:
        # List all files in the upload directory
        for filename in os.listdir(UPLOAD_FOLDER):
            # If file belongs to user
            if filename.startswith(f"{username}_profile."):
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    os.remove(filepath)
                except Exception as e:
                    logging.warning(f"Failed to remove old avatar file {filepath}: {e}")
    except Exception as e:
        logging.error(f"Failed to cleanup old avatars: {e}")

def save_profile_picture(file, username):
    """Save uploaded profile picture"""
    try:
        # Ensure upload folder exists
        if not ensure_upload_folder():
            logging.error("Failed to ensure upload folder exists")
            return None
            
        if not file:
            logging.error("No file provided")
            return None
            
        if not file.filename:
            logging.error("No filename in uploaded file")
            return None
            
        # Check file size
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size > MAX_FILE_SIZE:
            logging.error(f"File size {size} exceeds maximum allowed size {MAX_FILE_SIZE}")
            return None
            
        if not allowed_file(file.filename):
            logging.error(f"File type not allowed: {file.filename}")
            return None
            
        try:
            # Try to open the image to verify it's valid
            img = Image.open(file)
            img.verify()
            file.seek(0)
            
            # Reopen image after verify (verify closes the file)
            img = Image.open(file)
            img = img.convert('RGB')  # Convert to RGB mode
            
            # Create a secure filename with original extension
            ext = file.filename.rsplit('.', 1)[1].lower()
            filename = secure_filename(f"{username}_profile.{ext}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            
            # Remove old avatar files
            cleanup_old_avatar(username)
            
            # Resize image keeping aspect ratio
            img.thumbnail(AVATAR_SIZE)
            
            # Save the processed image
            img.save(filepath, quality=85, optimize=True)
            
            return filename
            
        except Exception as e:
            logging.error(f"Failed to process image: {e}")
            return None
            
    except Exception as e:
        logging.error(f"Failed to save profile picture: {e}")
        return None

def get_avatar_url(user):
    """Get the avatar URL for a user"""
    try:
        if user.profile_picture:
            avatar_path = os.path.join(UPLOAD_FOLDER, user.profile_picture)
            if os.path.exists(avatar_path):
                return f'/static/uploads/avatars/{user.profile_picture}'
        return None  # Will use generated avatar if None
    except Exception as e:
        logging.error(f"Failed to get avatar URL: {e}")
        return None 