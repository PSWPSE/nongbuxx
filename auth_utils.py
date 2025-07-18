import os
import secrets
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from flask_jwt_extended import create_access_token, create_refresh_token
import re
from email_validator import validate_email, EmailNotValidError

def generate_tokens(user_id):
    """Generate access and refresh tokens for a user"""
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)
    return {
        'access_token': access_token,
        'refresh_token': refresh_token
    }

def validate_password_strength(password):
    """
    Validate password strength
    Requirements:
    - At least 8 characters
    - Contains uppercase and lowercase letters
    - Contains at least one number
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "비밀번호는 최소 8자 이상이어야 합니다."
    
    if not re.search(r'[A-Z]', password):
        return False, "비밀번호는 대문자를 포함해야 합니다."
    
    if not re.search(r'[a-z]', password):
        return False, "비밀번호는 소문자를 포함해야 합니다."
    
    if not re.search(r'[0-9]', password):
        return False, "비밀번호는 숫자를 포함해야 합니다."
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "비밀번호는 특수문자를 포함해야 합니다."
    
    return True, "비밀번호가 유효합니다."

def validate_email_format(email):
    """Validate email format"""
    try:
        validated = validate_email(email)
        return True, validated.email
    except EmailNotValidError as e:
        return False, str(e)

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return secrets.token_urlsafe(32)

class ApiKeyEncryption:
    """Handle API key encryption and decryption"""
    
    def __init__(self, encryption_key=None):
        if encryption_key:
            # Ensure the key is 32 bytes (Fernet requirement)
            key = encryption_key.encode()[:32].ljust(32, b'0')
            self.cipher = Fernet(Fernet.generate_key() if len(key) != 32 else key)
        else:
            # Generate a new key if none provided
            self.cipher = Fernet(Fernet.generate_key())
    
    def encrypt(self, api_key):
        """Encrypt an API key"""
        return self.cipher.encrypt(api_key.encode()).decode()
    
    def decrypt(self, encrypted_key):
        """Decrypt an API key"""
        return self.cipher.decrypt(encrypted_key.encode()).decode()

def create_api_key_encryptor():
    """Create an API key encryptor with the app's encryption key"""
    encryption_key = os.getenv('ENCRYPTION_KEY', 'dev-encryption-key-32-chars-long')
    return ApiKeyEncryption(encryption_key)

def is_token_expired(expires_at):
    """Check if a token has expired"""
    return datetime.utcnow() > expires_at

def generate_username_from_email(email):
    """Generate a unique username from email"""
    # Take the part before @ and remove special characters
    base_username = email.split('@')[0]
    base_username = re.sub(r'[^a-zA-Z0-9]', '', base_username)
    
    # Add random suffix to ensure uniqueness
    suffix = secrets.token_hex(3)
    return f"{base_username}_{suffix}" 