from datetime import datetime
from flask_login import UserMixin
from bson.objectid import ObjectId
from pymongo.collection import Collection
from typing import Dict, List, Optional, Any

class User(UserMixin):
    """User model for authentication and data storage"""
    
    def __init__(self, user_data: Dict[str, Any]):
        if user_data is None:
            user_data = {}
        self._id = user_data.get('_id', None)
        self.email = user_data.get('email', '')
        self.username = user_data.get('username', '')
        self.name = user_data.get('name', '')
        self.picture = user_data.get('picture', '')
        self.provider = user_data.get('provider', '')  # google, apple, github
        self.provider_id = user_data.get('provider_id', '')
        self.created_at = user_data.get('created_at', datetime.utcnow())
        self.last_login = user_data.get('last_login', datetime.utcnow())
        self.preferences = user_data.get('preferences', {})
    
    def get_id(self):
        return str(self._id)
    
    @classmethod
    def get_by_id(cls, db, user_id):
        try:
            if db is None:
                print("Warning: Database connection not available in get_by_id")
                return None
            user_data = db.users.find_one({'_id': ObjectId(user_id)})
            return cls(user_data) if user_data else None
        except Exception as e:
            print(f"Error in get_by_id: {e}")
            return None
    
    @classmethod
    def get_by_email(cls, db, email):
        try:
            if db is None:
                print("Warning: Database connection not available in get_by_email")
                return None
            user_data = db.users.find_one({'email': email})
            return cls(user_data) if user_data else None
        except Exception as e:
            print(f"Error in get_by_email: {e}")
            return None
    
    @classmethod
    def get_by_provider_id(cls, db, provider, provider_id):
        try:
            if db is None:
                print("Warning: Database connection not available in get_by_provider_id")
                return None
            user_data = db.users.find_one({'provider': provider, 'provider_id': provider_id})
            return cls(user_data) if user_data else None
        except Exception as e:
            print(f"Error in get_by_provider_id: {e}")
            return None

    def save(self, db):
        """Save or update user in the database"""
        try:
            if db is None:
                print("Warning: Database connection not available in user save")
                return self
                
            if not self._id:
                user_data = {
                    'email': self.email,
                    'username': self.username,
                    'name': self.name,
                    'picture': self.picture,
                    'provider': self.provider,
                    'provider_id': self.provider_id,
                    'created_at': datetime.utcnow(),
                    'last_login': datetime.utcnow(),
                    'preferences': self.preferences
                }
                result = db.users.insert_one(user_data)
                self._id = result.inserted_id
            else:
                db.users.update_one(
                    {'_id': self._id},
                    {'$set': {
                        'email': self.email,
                        'username': self.username,
                        'name': self.name,
                        'picture': self.picture,
                        'last_login': datetime.utcnow(),
                        'preferences': self.preferences
                    }}
                )
            return self
        except Exception as e:
            print(f"Error saving user: {e}")
            return self

class SearchHistory:
    """Model for tracking user search history"""
    
    @staticmethod
    def add_search(db, user_id, query, search_type, results_count=0, papers=None):
        """Add a search to user's history"""
        try:
            if db is None:
                print("Warning: Database connection not available in add_search")
                return
                
            search_data = {
                'user_id': ObjectId(user_id),
                'query': query,
                'search_type': search_type,  # 'quick', 'deep', 'academic'
                'timestamp': datetime.utcnow(),
                'results_count': results_count,
                'papers': papers or []
            }
            db.search_history.insert_one(search_data)
        except Exception as e:
            print(f"Error adding search history: {e}")
    
    @staticmethod
    def get_user_history(db, user_id, limit=20):
        """Get a user's search history, most recent first"""
        try:
            if db is None:
                print("Warning: Database connection not available in get_user_history")
                return []
                
            cursor = db.search_history.find({'user_id': ObjectId(user_id)})
            return list(cursor.sort('timestamp', -1).limit(limit))
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []
    
    @staticmethod
    def clear_history(db, user_id):
        """Clear a user's search history"""
        try:
            if db is None:
                print("Warning: Database connection not available in clear_history")
                return
                
            db.search_history.delete_many({'user_id': ObjectId(user_id)})
        except Exception as e:
            print(f"Error clearing history: {e}")

class Favorite:
    """Model for user's favorite searches and results"""
    
    @staticmethod
    def add_favorite(db, user_id, name, query, search_type, result=None, paper=None):
        """Add a search or paper to favorites"""
        try:
            if db is None:
                print("Warning: Database connection not available in add_favorite")
                return
                
            favorite_data = {
                'user_id': ObjectId(user_id),
                'name': name,
                'query': query,
                'search_type': search_type,
                'timestamp': datetime.utcnow(),
                'result': result,
                'paper': paper
            }
            db.favorites.insert_one(favorite_data)
        except Exception as e:
            print(f"Error adding favorite: {e}")
    
    @staticmethod
    def get_favorites(db, user_id):
        """Get a user's favorites"""
        try:
            if db is None:
                print("Warning: Database connection not available in get_favorites")
                return []
                
            return list(db.favorites.find({'user_id': ObjectId(user_id)}))
        except Exception as e:
            print(f"Error getting favorites: {e}")
            return []
    
    @staticmethod
    def remove_favorite(db, favorite_id):
        """Remove a favorite"""
        try:
            if db is None:
                print("Warning: Database connection not available in remove_favorite")
                return
                
            db.favorites.delete_one({'_id': ObjectId(favorite_id)})
        except Exception as e:
            print(f"Error removing favorite: {e}")

class Recommendation:
    """Model for generating personalized recommendations"""
    
    @staticmethod
    def get_recommendations(db, user_id, limit=5):
        """Generate recommendations based on user's search history"""
        try:
            if db is None:
                print("Warning: Database connection not available in get_recommendations")
                return []
            
            # Get user's recent searches
            recent_searches = list(db.search_history.find(
                {'user_id': ObjectId(user_id)}
            ).sort('timestamp', -1).limit(20))
            
            # If no search history, return empty recommendations
            if not recent_searches:
                return []
            
            # Extract topics from searches
            topics = {}
            for search in recent_searches:
                words = search['query'].lower().split()
                for word in words:
                    if len(word) > 3:  # Only consider significant words
                        topics[word] = topics.get(word, 0) + 1
            
            # Find most frequent topics
            sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
            top_topics = [topic for topic, count in sorted_topics[:3]]
            
            # Find similar searches from other users
            recommendations = []
            if top_topics:
                # Simple regex search for similar topics
                for topic in top_topics:
                    similar_searches = list(db.search_history.find({
                        'user_id': {'$ne': ObjectId(user_id)},
                        'query': {'$regex': topic, '$options': 'i'}
                    }).sort('timestamp', -1).limit(2))
                    
                    for search in similar_searches:
                        if search['query'] not in [s.get('query') for s in recommendations]:
                            recommendations.append({
                                'query': search['query'],
                                'search_type': search['search_type'],
                                'based_on': topic
                            })
                            
                            if len(recommendations) >= limit:
                                break
                
            return recommendations[:limit]
        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return [] 