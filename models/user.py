from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.password_hash = user_data.get('password_hash')
        self.profile_picture = user_data.get('profile_picture')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.last_login = user_data.get('last_login')
        self.provider = user_data.get('provider', 'local')
        self.two_factor_enabled = user_data.get('two_factor_enabled', False)
        self.two_factor_secret = user_data.get('two_factor_secret')
        self.preferences = user_data.get('preferences', {})

    def get_id(self):
        return self.id

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username': self.username,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'created_at': self.created_at,
            'last_login': self.last_login,
            'provider': self.provider,
            'two_factor_enabled': self.two_factor_enabled,
            'preferences': self.preferences
        } 