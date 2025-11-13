import os
import pyotp
import qrcode
import io
import base64
import secrets
import string
import hashlib
from typing import Tuple, List, Dict, Optional
from datetime import datetime, timedelta
import logging

# Import config with fallback to environment variables
try:
    from config import TOTP_ISSUER_NAME, SECRET_KEY
except ImportError:
    # Fallback to environment variables for deployment
    TOTP_ISSUER_NAME = os.getenv('TOTP_ISSUER_NAME', 'Sentino AI')
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityManager:
    """Comprehensive security manager for 2FA and security features"""
    
    def __init__(self):
        self.issuer_name = TOTP_ISSUER_NAME
        
    def generate_totp_secret(self) -> str:
        """Generate a new TOTP secret key"""
        return pyotp.random_base32()
    
    def generate_totp_uri(self, secret: str, user_email: str) -> str:
        """Generate TOTP URI for QR code"""
        totp = pyotp.TOTP(secret)
        return totp.provisioning_uri(
            name=user_email,
            issuer_name=self.issuer_name
        )
    
    def generate_qr_code(self, totp_uri: str) -> str:
        """Generate QR code image as base64 string"""
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(totp_uri)
            qr.make(fit=True)
            
            # Create QR code image
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            img_base64 = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/png;base64,{img_base64}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {str(e)}")
            raise e
    
    def verify_totp_code(self, secret: str, code: str) -> bool:
        """Verify TOTP code"""
        try:
            totp = pyotp.TOTP(secret)
            # Allow 1 window before and after for clock skew
            return totp.verify(code, valid_window=1)
        except Exception as e:
            logger.error(f"Error verifying TOTP code: {str(e)}")
            return False
    
    def generate_backup_codes(self, count: int = 10) -> List[str]:
        """Generate backup codes for 2FA recovery"""
        backup_codes = []
        for _ in range(count):
            # Generate 8-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            # Format as XXXX-XXXX for readability
            formatted_code = f"{code[:4]}-{code[4:]}"
            backup_codes.append(formatted_code)
        
        return backup_codes
    
    def hash_backup_codes(self, backup_codes: List[str]) -> List[str]:
        """Hash backup codes for secure storage"""
        hashed_codes = []
        for code in backup_codes:
            # Remove formatting and hash
            clean_code = code.replace('-', '').upper()
            hashed = hashlib.sha256((clean_code + SECRET_KEY).encode()).hexdigest()
            hashed_codes.append(hashed)
        
        return hashed_codes
    
    def verify_backup_code(self, provided_code: str, hashed_codes: List[str]) -> Tuple[bool, str]:
        """Verify backup code and return the hash if valid"""
        try:
            # Clean and normalize the provided code
            clean_code = provided_code.replace('-', '').replace(' ', '').upper()
            if len(clean_code) != 8:
                return False, ""
            
            # Hash the provided code
            provided_hash = hashlib.sha256((clean_code + SECRET_KEY).encode()).hexdigest()
            
            # Check if it matches any of the stored hashes
            if provided_hash in hashed_codes:
                return True, provided_hash
            
            return False, ""
            
        except Exception as e:
            logger.error(f"Error verifying backup code: {str(e)}")
            return False, ""
    
    def setup_2fa_for_user(self, user_email: str) -> Dict:
        """Complete 2FA setup for a user"""
        try:
            # Generate secret and backup codes
            secret = self.generate_totp_secret()
            backup_codes = self.generate_backup_codes()
            hashed_backup_codes = self.hash_backup_codes(backup_codes)
            
            # Generate QR code
            totp_uri = self.generate_totp_uri(secret, user_email)
            qr_code = self.generate_qr_code(totp_uri)
            
            return {
                'secret': secret,
                'qr_code': qr_code,
                'backup_codes': backup_codes,
                'hashed_backup_codes': hashed_backup_codes,
                'totp_uri': totp_uri
            }
            
        except Exception as e:
            logger.error(f"Error setting up 2FA for user {user_email}: {str(e)}")
            raise e
    
    def generate_session_token(self, length: int = 32) -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(length)
    
    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(16)
        
        # Use PBKDF2 with SHA256
        hashed = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        )
        
        return hashed.hex(), salt
    
    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """Verify password against hash"""
        try:
            test_hash, _ = self.hash_password(password, salt)
            return secrets.compare_digest(test_hash, hashed_password)
        except Exception as e:
            logger.error(f"Error verifying password: {str(e)}")
            return False
    
    def check_password_strength(self, password: str) -> Dict:
        """Check password strength and return score with feedback"""
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 25
        else:
            feedback.append("Password should be at least 8 characters long")
        
        # Uppercase check
        if any(c.isupper() for c in password):
            score += 25
        else:
            feedback.append("Password should contain at least one uppercase letter")
        
        # Lowercase check
        if any(c.islower() for c in password):
            score += 10
        
        # Number check
        if any(c.isdigit() for c in password):
            score += 25
        else:
            feedback.append("Password should contain at least one number")
        
        # Special character check
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if any(c in special_chars for c in password):
            score += 25
        else:
            feedback.append("Password should contain at least one special character")
        
        # Additional length bonus
        if len(password) >= 12:
            score += 10
        
        # Determine strength level
        if score >= 90:
            strength = "Very Strong"
        elif score >= 70:
            strength = "Strong"
        elif score >= 50:
            strength = "Moderate"
        elif score >= 30:
            strength = "Weak"
        else:
            strength = "Very Weak"
        
        return {
            'score': min(score, 100),
            'strength': strength,
            'feedback': feedback
        }
    
    def detect_suspicious_activity(self, user_login_history: List[Dict]) -> Dict:
        """Detect suspicious login activity patterns"""
        if not user_login_history:
            return {'suspicious': False, 'reasons': []}
        
        suspicious = False
        reasons = []
        
        # Sort by timestamp (most recent first)
        sorted_history = sorted(
            user_login_history,
            key=lambda x: x.get('timestamp', datetime.min),
            reverse=True
        )
        
        recent_logins = sorted_history[:10]  # Check last 10 logins
        
        # Check for multiple failed attempts
        failed_attempts = [login for login in recent_logins if not login.get('success', False)]
        if len(failed_attempts) >= 5:
            suspicious = True
            reasons.append("Multiple failed login attempts detected")
        
        # Check for logins from different countries/IPs
        unique_ips = set(login.get('ip_address', '') for login in recent_logins)
        if len(unique_ips) > 3:
            suspicious = True
            reasons.append("Logins from multiple IP addresses detected")
        
        # Check for unusual login times (e.g., outside normal hours)
        unusual_times = []
        for login in recent_logins:
            timestamp = login.get('timestamp')
            if timestamp and isinstance(timestamp, datetime):
                hour = timestamp.hour
                if hour < 6 or hour > 23:  # Between 11 PM and 6 AM
                    unusual_times.append(timestamp)
        
        if len(unusual_times) >= 3:
            suspicious = True
            reasons.append("Multiple logins at unusual times detected")
        
        # Check for rapid successive logins
        rapid_logins = 0
        for i in range(len(recent_logins) - 1):
            current = recent_logins[i].get('timestamp')
            next_login = recent_logins[i + 1].get('timestamp')
            if current and next_login and isinstance(current, datetime) and isinstance(next_login, datetime):
                time_diff = abs((current - next_login).total_seconds())
                if time_diff < 60:  # Less than 1 minute apart
                    rapid_logins += 1
        
        if rapid_logins >= 3:
            suspicious = True
            reasons.append("Rapid successive login attempts detected")
        
        return {
            'suspicious': suspicious,
            'reasons': reasons,
            'confidence': min(len(reasons) * 25, 100)  # Confidence score out of 100
        }
    
    def generate_rate_limit_key(self, identifier: str, action: str) -> str:
        """Generate key for rate limiting"""
        return f"rate_limit:{action}:{identifier}"
    
    def is_rate_limited(self, redis_client, identifier: str, action: str, 
                       limit: int, window_seconds: int) -> Tuple[bool, int]:
        """Check if action is rate limited"""
        try:
            key = self.generate_rate_limit_key(identifier, action)
            current_count = redis_client.get(key)
            
            if current_count is None:
                # First request in window
                redis_client.setex(key, window_seconds, 1)
                return False, limit - 1
            
            current_count = int(current_count)
            if current_count >= limit:
                # Rate limit exceeded
                ttl = redis_client.ttl(key)
                return True, ttl
            
            # Increment counter
            redis_client.incr(key)
            return False, limit - (current_count + 1)
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # Allow request if Redis is down
            return False, limit

# Create global security manager instance
security_manager = SecurityManager() 