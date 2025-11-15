"""
Firebase REST API Authentication Helper
Allows signup and login using Firebase REST API without Web SDK
"""
import requests
import json
import os
from typing import Optional, Dict
from backend.config.settings import settings
from pathlib import Path


# Firebase REST API endpoints
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


def get_firebase_api_key() -> Optional[str]:
    """
    Get Firebase Web API Key from settings or environment
    
    Returns:
        Firebase Web API Key or None
    """
    # Try settings first
    if hasattr(settings, 'firebase_web_api_key') and settings.firebase_web_api_key:
        return settings.firebase_web_api_key
    
    # Try environment variable
    api_key = os.getenv("FIREBASE_WEB_API_KEY")
    if api_key:
        return api_key
    
    return None


def signup_with_email_password(email: str, password: str, display_name: Optional[str] = None) -> Optional[Dict]:
    """
    Sign up a new user with email/password using Firebase REST API
    
    Args:
        email: User email
        password: User password
        display_name: Optional display name
        
    Returns:
        Dictionary with idToken, email, localId, etc. or None if failed
    """
    api_key = get_firebase_api_key()
    if not api_key:
        raise ValueError("Firebase Web API Key not configured. Set FIREBASE_WEB_API_KEY environment variable.")
    
    url = f"{FIREBASE_AUTH_URL}:signUp?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    if display_name:
        payload["displayName"] = display_name
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_data = e.response.json() if e.response else {}
        error_message = error_data.get("error", {}).get("message", str(e))
        raise Exception(f"Firebase signup failed: {error_message}")
    except Exception as e:
        raise Exception(f"Firebase signup error: {str(e)}")


def signin_with_email_password(email: str, password: str) -> Optional[Dict]:
    """
    Sign in with email/password using Firebase REST API
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Dictionary with idToken, email, localId, etc. or None if failed
    """
    api_key = get_firebase_api_key()
    if not api_key:
        raise ValueError("Firebase Web API Key not configured. Set FIREBASE_WEB_API_KEY environment variable.")
    
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_data = e.response.json() if e.response else {}
        error_message = error_data.get("error", {}).get("message", str(e))
        raise Exception(f"Firebase signin failed: {error_message}")
    except Exception as e:
        raise Exception(f"Firebase signin error: {str(e)}")

