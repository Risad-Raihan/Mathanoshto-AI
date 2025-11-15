"""
Firebase Authentication utilities for backend verification
"""
import firebase_admin
from firebase_admin import credentials, auth
from typing import Optional, Dict
import os
from pathlib import Path
from backend.config.settings import settings


# Initialize Firebase Admin SDK
_firebase_app = None


def initialize_firebase():
    """
    Initialize Firebase Admin SDK
    Can be called multiple times safely (idempotent)
    """
    global _firebase_app
    
    if _firebase_app is not None:
        return _firebase_app
    
    if not settings.use_firebase_auth:
        print("⚠️  Firebase Authentication is disabled in settings")
        return None
    
    try:
        # Check if Firebase is already initialized
        if len(firebase_admin._apps) > 0:
            _firebase_app = firebase_admin.get_app()
            return _firebase_app
        
        # Try to initialize with credentials file
        if settings.firebase_credentials_path:
            cred_path = Path(settings.firebase_credentials_path)
            if cred_path.exists():
                cred = credentials.Certificate(str(cred_path))
                _firebase_app = firebase_admin.initialize_app(cred)
                print("✓ Firebase initialized with credentials file")
                return _firebase_app
        
        # Try environment variable for credentials path
        env_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if env_cred_path and Path(env_cred_path).exists():
            cred = credentials.Certificate(env_cred_path)
            _firebase_app = firebase_admin.initialize_app(cred)
            print("✓ Firebase initialized with environment credentials")
            return _firebase_app
        
        # Try default location
        default_cred_path = Path("firebase-credentials.json")
        if default_cred_path.exists():
            cred = credentials.Certificate(str(default_cred_path))
            _firebase_app = firebase_admin.initialize_app(cred)
            print("✓ Firebase initialized with default credentials file")
            return _firebase_app
        
        # Try to use Application Default Credentials (for Google Cloud environments)
        try:
            _firebase_app = firebase_admin.initialize_app()
            print("✓ Firebase initialized with Application Default Credentials")
            return _firebase_app
        except Exception:
            pass
        
        # If all else fails, print warning but don't crash
        print("⚠️  Firebase credentials not found. Firebase Authentication will not work.")
        print("   Set FIREBASE_CREDENTIALS_PATH or place firebase-credentials.json in project root")
        return None
        
    except Exception as e:
        print(f"⚠️  Failed to initialize Firebase: {e}")
        print("   Firebase Authentication will not work")
        return None


def verify_firebase_token(id_token: str) -> Optional[Dict]:
    """
    Verify a Firebase ID token and return user information
    
    Args:
        id_token: Firebase ID token from client
        
    Returns:
        Dictionary with user info (uid, email, name) or None if invalid
    """
    if not settings.use_firebase_auth:
        return None
    
    try:
        # Ensure Firebase is initialized
        initialize_firebase()
        
        if _firebase_app is None:
            return None
        
        # Verify the token
        decoded_token = auth.verify_id_token(id_token)
        
        return {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email'),
            'name': decoded_token.get('name'),
            'email_verified': decoded_token.get('email_verified', False),
            'picture': decoded_token.get('picture'),
            'firebase_claims': decoded_token
        }
    except auth.InvalidIdTokenError:
        print("Invalid Firebase ID token")
        return None
    except auth.ExpiredIdTokenError:
        print("Expired Firebase ID token")
        return None
    except Exception as e:
        print(f"Error verifying Firebase token: {e}")
        return None


def get_firebase_user(uid: str) -> Optional[Dict]:
    """
    Get Firebase user information by UID
    
    Args:
        uid: Firebase user UID
        
    Returns:
        Dictionary with user info or None if not found
    """
    if not settings.use_firebase_auth:
        return None
    
    try:
        initialize_firebase()
        
        if _firebase_app is None:
            return None
        
        user = auth.get_user(uid)
        
        return {
            'uid': user.uid,
            'email': user.email,
            'name': user.display_name,
            'email_verified': user.email_verified,
            'picture': user.photo_url,
            'disabled': user.disabled
        }
    except auth.UserNotFoundError:
        return None
    except Exception as e:
        print(f"Error getting Firebase user: {e}")
        return None


def create_firebase_user(email: str, password: str, display_name: Optional[str] = None) -> Optional[Dict]:
    """
    Create a new Firebase user (admin function)
    
    Args:
        email: User email
        password: User password
        display_name: Optional display name
        
    Returns:
        Dictionary with created user info or None if failed
    """
    if not settings.use_firebase_auth:
        return None
    
    try:
        initialize_firebase()
        
        if _firebase_app is None:
            return None
        
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            email_verified=False
        )
        
        return {
            'uid': user.uid,
            'email': user.email,
            'name': user.display_name
        }
    except Exception as e:
        print(f"Error creating Firebase user: {e}")
        return None


def delete_firebase_user(uid: str) -> bool:
    """
    Delete a Firebase user (admin function)
    
    Args:
        uid: Firebase user UID
        
    Returns:
        True if successful, False otherwise
    """
    if not settings.use_firebase_auth:
        return False
    
    try:
        initialize_firebase()
        
        if _firebase_app is None:
            return False
        
        auth.delete_user(uid)
        return True
    except Exception as e:
        print(f"Error deleting Firebase user: {e}")
        return False

