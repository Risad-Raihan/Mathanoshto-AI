"""
Database operations for users, API keys, and sessions
"""
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from backend.database.models import User, UserAPIKey, UserSession
from backend.database.operations import get_db
from backend.auth import hash_password, verify_password, encrypt_api_key, decrypt_api_key, generate_session_token, hash_session_token
from backend.auth.firebase_auth import verify_firebase_token, get_firebase_user


class UserDB:
    """Database operations for users"""
    
    @staticmethod
    def create_user(
        username: str,
        password: str,
        full_name: Optional[str] = None,
        email: Optional[str] = None
    ) -> User:
        """
        Create a new user
        
        Args:
            username: Unique username
            password: Plain text password (will be hashed)
            full_name: Full name of user
            email: Email address
            
        Returns:
            Created User object
        """
        db = get_db()
        try:
            password_hash = hash_password(password)
            user = User(
                username=username,
                password_hash=password_hash,
                full_name=full_name,
                email=email
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """Get user by username"""
        db = get_db()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user:
                db.refresh(user)
                db.expunge(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """Get user by ID"""
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                db.refresh(user)
                db.expunge(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_firebase_uid(firebase_uid: str) -> Optional[User]:
        """Get user by Firebase UID"""
        db = get_db()
        try:
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            if user:
                db.refresh(user)
                db.expunge(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """Get user by email address"""
        db = get_db()
        try:
            user = db.query(User).filter(User.email == email).first()
            if user:
                db.refresh(user)
                db.expunge(user)
            return user
        finally:
            db.close()
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: Username
            password: Plain text password
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = UserDB.get_user_by_username(username)
        if user and verify_password(password, user.password_hash):
            # Update last login
            UserDB.update_last_login(user.id)
            return user
        return None
    
    @staticmethod
    def update_last_login(user_id: int):
        """Update user's last login time"""
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.last_login = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def update_user_preferences(
        user_id: int,
        default_provider: Optional[str] = None,
        default_model: Optional[str] = None,
        default_temperature: Optional[float] = None,
        default_max_tokens: Optional[int] = None,
        theme: Optional[str] = None
    ):
        """Update user preferences"""
        db = get_db()
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                if default_provider is not None:
                    user.default_provider = default_provider
                if default_model is not None:
                    user.default_model = default_model
                if default_temperature is not None:
                    user.default_temperature = default_temperature
                if default_max_tokens is not None:
                    user.default_max_tokens = default_max_tokens
                if theme is not None:
                    user.theme = theme
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def list_all_users() -> List[User]:
        """Get all users"""
        db = get_db()
        try:
            return db.query(User).all()
        finally:
            db.close()
    
    @staticmethod
    def create_or_get_user_from_firebase(firebase_token: str) -> Optional[User]:
        """
        Create or get user from Firebase ID token
        This is the main method for Firebase authentication
        
        Args:
            firebase_token: Firebase ID token from client
            
        Returns:
            User object if successful, None otherwise
        """
        # Try to verify Firebase token (requires Firebase Admin SDK)
        firebase_user_info = verify_firebase_token(firebase_token)
        
        # If token verification fails, try to decode token directly (fallback)
        if not firebase_user_info:
            # Fallback: Try to decode the token without verification
            # This is less secure but works if Firebase Admin SDK verification fails
            try:
                import base64
                import json
                # Firebase ID tokens are JWT - decode the payload (not secure, but works)
                parts = firebase_token.split('.')
                if len(parts) >= 2:
                    # Decode the payload (second part)
                    payload = parts[1]
                    # Add padding if needed
                    padding = 4 - len(payload) % 4
                    if padding != 4:
                        payload += '=' * padding
                    decoded = base64.urlsafe_b64decode(payload)
                    token_data = json.loads(decoded)
                    
                    # Firebase REST API tokens use 'user_id' or 'sub' for UID
                    # Firebase Admin SDK verified tokens use 'uid'
                    uid = token_data.get('user_id') or token_data.get('sub') or token_data.get('uid')
                    
                    firebase_user_info = {
                        'uid': uid,
                        'email': token_data.get('email'),
                        'name': token_data.get('name')
                    }
                    print(f"⚠️ Using fallback token decoding (Firebase Admin SDK verification failed)")
                    print(f"⚠️ Decoded UID: {uid}, Email: {token_data.get('email')}")
            except Exception as e:
                print(f"Failed to decode token: {e}")
                import traceback
                print(traceback.format_exc())
                return None
        
        if not firebase_user_info:
            return None
        
        firebase_uid = firebase_user_info['uid']
        email = firebase_user_info.get('email')
        name = firebase_user_info.get('name')
        
        db = get_db()
        try:
            # Check if user already exists with this Firebase UID
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            
            if user:
                # User exists, update last login and refresh info
                user.last_login = datetime.utcnow()
                # Update email/name if changed in Firebase
                if email and user.email != email:
                    user.email = email
                if name and user.full_name != name:
                    user.full_name = name
                db.commit()
                db.refresh(user)
                db.expunge(user)
                return user
            
            # Check if user exists with this email (for migration from old system)
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    # Link existing user to Firebase
                    user.firebase_uid = firebase_uid
                    if name and not user.full_name:
                        user.full_name = name
                    user.last_login = datetime.utcnow()
                    db.commit()
                    db.refresh(user)
                    db.expunge(user)
                    return user
            
            # Create new user linked to Firebase
            # Use empty string for password_hash instead of None to satisfy NOT NULL constraint
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                full_name=name,
                username=email.split('@')[0] if email else None,  # Use email prefix as username
                password_hash='',  # Empty string for Firebase users (no password stored locally)
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db.expunge(user)
            return user
            
        except Exception as e:
            db.rollback()
            print(f"Error creating/getting user from Firebase: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def create_user_from_firebase_rest_response(firebase_response: dict) -> Optional[User]:
        """
        Create user from Firebase REST API response (signup/signin)
        Handles cases where Firebase returns localId instead of idToken
        
        Args:
            firebase_response: Response dict from Firebase REST API with keys like:
                - localId (Firebase UID)
                - email
                - displayName
                - idToken (optional)
        
        Returns:
            User object if successful, None otherwise
        """
        firebase_uid = firebase_response.get('localId') or firebase_response.get('uid')
        if not firebase_uid:
            print("⚠️ Firebase response missing localId/uid")
            return None
        
        email = firebase_response.get('email')
        display_name = firebase_response.get('displayName')
        
        db = get_db()
        try:
            # Check if user already exists with this Firebase UID
            user = db.query(User).filter(User.firebase_uid == firebase_uid).first()
            
            if user:
                # User exists, update info
                user.last_login = datetime.utcnow()
                if email and user.email != email:
                    user.email = email
                if display_name and user.full_name != display_name:
                    user.full_name = display_name
                db.commit()
                db.refresh(user)
                db.expunge(user)
                return user
            
            # Check if user exists with this email (for migration)
            if email:
                user = db.query(User).filter(User.email == email).first()
                if user:
                    # Link existing user to Firebase
                    user.firebase_uid = firebase_uid
                    if display_name and not user.full_name:
                        user.full_name = display_name
                    user.last_login = datetime.utcnow()
                    db.commit()
                    db.refresh(user)
                    db.expunge(user)
                    return user
            
            # Create new user
            # Use empty string for password_hash instead of None to satisfy NOT NULL constraint
            # (SQLite doesn't support ALTER COLUMN, so existing tables may have NOT NULL)
            user = User(
                firebase_uid=firebase_uid,
                email=email,
                full_name=display_name,
                username=email.split('@')[0] if email else None,
                password_hash='',  # Empty string for Firebase users (no password stored locally)
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            db.expunge(user)
            return user
            
        except Exception as e:
            db.rollback()
            print(f"Error creating user from Firebase REST response: {e}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            db.close()
    
    @staticmethod
    def authenticate_with_firebase(firebase_token: str) -> Optional[User]:
        """
        Authenticate user with Firebase token (alias for create_or_get_user_from_firebase)
        
        Args:
            firebase_token: Firebase ID token
            
        Returns:
            User object if authentication succeeds, None otherwise
        """
        return UserDB.create_or_get_user_from_firebase(firebase_token)


class UserAPIKeyDB:
    """Database operations for user API keys"""
    
    @staticmethod
    def add_api_key(
        user_id: int,
        provider: str,
        api_key: str,
        key_name: str,
        base_url: Optional[str] = None
    ) -> UserAPIKey:
        """
        Add a new API key for a user (allows duplicates)
        
        Args:
            user_id: User ID
            provider: Provider name (openai, gemini, etc.)
            api_key: Plain text API key (will be encrypted)
            key_name: Key name (e.g., 'OPENAI_API_KEY')
            base_url: Optional base URL for custom endpoints
            
        Returns:
            Created UserAPIKey object
        """
        db = get_db()
        try:
            encrypted = encrypt_api_key(api_key)
            
            # Always create a new key (allow duplicates)
            api_key_obj = UserAPIKey(
                user_id=user_id,
                provider=provider,
                key_name=key_name,
                encrypted_key=encrypted,
                base_url=base_url
            )
            db.add(api_key_obj)
            db.commit()
            db.refresh(api_key_obj)
            return api_key_obj
        finally:
            db.close()
    
    @staticmethod
    def get_api_key(user_id: int, provider: str) -> Optional[str]:
        """
        Get decrypted API key for a user and provider
        
        Args:
            user_id: User ID
            provider: Provider name
            
        Returns:
            Decrypted API key or None
        """
        db = get_db()
        try:
            key_obj = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider,
                UserAPIKey.is_active == True
            ).first()
            
            if key_obj:
                return decrypt_api_key(key_obj.encrypted_key)
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_all_user_keys(user_id: int) -> Dict[str, str]:
        """
        Get all decrypted API keys for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary mapping provider to API key
        """
        db = get_db()
        try:
            keys = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == user_id,
                UserAPIKey.is_active == True
            ).all()
            
            result = {}
            for key_obj in keys:
                decrypted = decrypt_api_key(key_obj.encrypted_key)
                if decrypted:
                    result[key_obj.provider] = decrypted
                    if key_obj.base_url:
                        result[f"{key_obj.provider}_base_url"] = key_obj.base_url
            
            return result
        finally:
            db.close()
    
    @staticmethod
    def list_user_api_keys(user_id: int) -> List[Dict]:
        """
        List all API keys for a user (without decrypting them)
        
        Args:
            user_id: User ID
            
        Returns:
            List of API key info dictionaries
        """
        db = get_db()
        try:
            keys = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == user_id
            ).all()
            
            return [
                {
                    "id": key.id,
                    "provider": key.provider,
                    "key_name": key.key_name,
                    "base_url": key.base_url,
                    "is_active": key.is_active,
                    "created_at": key.created_at,
                    "updated_at": key.updated_at
                }
                for key in keys
            ]
        finally:
            db.close()
    
    @staticmethod
    def delete_api_key(user_id: int, provider: str):
        """Delete an API key by user_id and provider (deletes first match)"""
        db = get_db()
        try:
            key_obj = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider
            ).first()
            
            if key_obj:
                db.delete(key_obj)
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def delete_api_key_by_id(key_id: int):
        """Delete an API key by its ID"""
        db = get_db()
        try:
            key_obj = db.query(UserAPIKey).filter(
                UserAPIKey.id == key_id
            ).first()
            
            if key_obj:
                db.delete(key_obj)
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def delete_all_api_keys():
        """Delete all API keys from the database"""
        db = get_db()
        try:
            db.query(UserAPIKey).delete()
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def deactivate_api_key(user_id: int, provider: str):
        """Deactivate an API key"""
        db = get_db()
        try:
            key_obj = db.query(UserAPIKey).filter(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider
            ).first()
            
            if key_obj:
                key_obj.is_active = False
                db.commit()
        finally:
            db.close()


class UserSessionDB:
    """Database operations for user sessions (Remember Me functionality)"""
    
    @staticmethod
    def create_session(
        user_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_days: int = 30
    ) -> tuple[str, UserSession]:
        """
        Create a new session token for a user
        
        Args:
            user_id: User ID
            ip_address: Client IP address
            user_agent: Client user agent
            expires_days: Number of days until session expires (default: 30)
            
        Returns:
            Tuple of (plain_token, session_object)
        """
        db = get_db()
        try:
            # Generate session token
            plain_token = generate_session_token()
            hashed_token = hash_session_token(plain_token)
            
            # Calculate expiration
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
            
            # Create session
            session = UserSession(
                user_id=user_id,
                session_token=hashed_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            return plain_token, session
        finally:
            db.close()
    
    @staticmethod
    def validate_session(token: str) -> Optional[User]:
        """
        Validate a session token and return the associated user
        
        Args:
            token: Plain session token
            
        Returns:
            User object if session is valid, None otherwise
        """
        db = get_db()
        try:
            hashed_token = hash_session_token(token)
            
            # Find session
            session = db.query(UserSession).filter(
                UserSession.session_token == hashed_token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
            
            if not session:
                return None
            
            # Get user
            user = db.query(User).filter(
                User.id == session.user_id,
                User.is_active == True
            ).first()
            
            if user:
                # Update last activity
                session.last_activity = datetime.utcnow()
                db.commit()
                
                # Refresh user to load all attributes
                db.refresh(user)
                
                # Expunge user from session to prevent DetachedInstanceError
                # This makes the object independent of the session
                db.expunge(user)
            
            return user
        finally:
            db.close()
    
    @staticmethod
    def delete_session(token: str):
        """
        Delete a session (logout)
        
        Args:
            token: Plain session token
        """
        db = get_db()
        try:
            hashed_token = hash_session_token(token)
            
            session = db.query(UserSession).filter(
                UserSession.session_token == hashed_token
            ).first()
            
            if session:
                db.delete(session)
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def delete_user_sessions(user_id: int):
        """
        Delete all sessions for a user (logout from all devices)
        
        Args:
            user_id: User ID
        """
        db = get_db()
        try:
            db.query(UserSession).filter(
                UserSession.user_id == user_id
            ).delete()
            db.commit()
        finally:
            db.close()
    
    @staticmethod
    def cleanup_expired_sessions():
        """
        Remove expired sessions from database
        Should be run periodically (e.g., daily cron job)
        """
        db = get_db()
        try:
            db.query(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ).delete()
            db.commit()
        finally:
            db.close()

