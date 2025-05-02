from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from utils.avatar import save_profile_picture, generate_random_avatar, get_avatar_url
import os

profile = Blueprint('profile', __name__)

@profile.route('/profile/avatar', methods=['GET'])
@login_required
def get_avatar():
    """Get user's avatar - returns generated avatar if no profile picture exists"""
    avatar_url = get_avatar_url(current_user)
    
    if avatar_url:
        return jsonify({'avatar_url': avatar_url})
    
    # Generate and return random avatar
    avatar_bytes = generate_random_avatar(current_user.username)
    return send_file(
        avatar_bytes,
        mimetype='image/png',
        as_attachment=False,
        download_name=f'{current_user.username}_avatar.png'
    )

@profile.route('/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload a new profile picture"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # Save the new profile picture
        filename = save_profile_picture(file, current_user.username)
        if filename:
            # Remove old profile picture if it exists
            if current_user.profile_picture:
                old_file = os.path.join('static/uploads/avatars', current_user.profile_picture)
                if os.path.exists(old_file):
                    os.remove(old_file)
            
            # Update user's profile picture
            current_user.set_profile_picture(filename)
            return jsonify({
                'message': 'Profile picture updated successfully',
                'avatar_url': get_avatar_url(current_user)
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@profile.route('/profile/avatar', methods=['DELETE'])
@login_required
def remove_avatar():
    """Remove the current profile picture"""
    try:
        if current_user.profile_picture:
            # Remove the file
            file_path = os.path.join('static/uploads/avatars', current_user.profile_picture)
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # Update user record
            current_user.remove_profile_picture()
            
            return jsonify({'message': 'Profile picture removed successfully'})
        
        return jsonify({'message': 'No profile picture to remove'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 