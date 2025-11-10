"""
Authentication utilities for password hashing and API key encryption
"""
import bcrypt
from cryptography.fernet import Fernet
from typing import Optional
import os
import base64


# Generate or load encryption key for API keys
def get_encryption_key() -> bytes:
    """
    Get or generate encryption key for API keys
    In production, this should be stored securely (e.g., environment variable)
    """
    key_file = "encryption.key"
    
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        # Generate new key
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key


# Initialize Fernet cipher
_encryption_key = get_encryption_key()
_cipher = Fernet(_encryption_key)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt
    
    Args:
        password: Plain text password
        
    Returns:
        Hashed password as string
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        password: Plain text password to verify
        hashed: Hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for storage
    
    Args:
        api_key: Plain text API key
        
    Returns:
        Encrypted API key as string
    """
    encrypted = _cipher.encrypt(api_key.encode('utf-8'))
    return base64.b64encode(encrypted).decode('utf-8')


def decrypt_api_key(encrypted_key: str) -> Optional[str]:
    """
    Decrypt an API key
    
    Args:
        encrypted_key: Encrypted API key
        
    Returns:
        Decrypted API key or None if decryption fails
    """
    try:
        encrypted_bytes = base64.b64decode(encrypted_key.encode('utf-8'))
        decrypted = _cipher.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    except Exception as e:
        print(f"Failed to decrypt API key: {e}")
        return None

