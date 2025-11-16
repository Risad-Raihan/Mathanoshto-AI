"""
Firebase REST API Authentication
Direct email/password authentication using Firebase REST API
"""
import requests
import json
import os
from typing import Optional, Dict
from backend.config.settings import settings


FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts"


def get_firebase_api_key() -> Optional[str]:
    """Get Firebase Web API Key from settings or environment"""
    if hasattr(settings, 'firebase_web_api_key') and settings.firebase_web_api_key:
        return settings.firebase_web_api_key
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
        Dictionary with user info and tokens, or None if failed
    """
    api_key = get_firebase_api_key()
    if not api_key:
        raise Exception("Firebase Web API Key not configured. Please set FIREBASE_WEB_API_KEY in environment.")
    
    url = f"{FIREBASE_AUTH_URL}:signUp?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        # Update display name if provided
        if display_name and 'idToken' in data:
            update_profile_url = f"{FIREBASE_AUTH_URL}:update?key={api_key}"
            update_payload = {
                "idToken": data['idToken'],
                "displayName": display_name,
                "returnSecureToken": True
            }
            update_response = requests.post(update_profile_url, headers=headers, json=update_payload)
            if update_response.status_code == 200:
                data = update_response.json()  # Get updated data with display name
                
        return data
    except requests.exceptions.HTTPError as e:
        error_data = e.response.json().get('error', {})
        error_message = error_data.get('message', str(e))
        raise Exception(error_message)
    except Exception as e:
        raise Exception(f"Firebase signup failed: {e}")


def signin_with_email_password(email: str, password: str) -> Optional[Dict]:
    """
    Sign in with email/password using Firebase REST API
    
    Args:
        email: User email
        password: User password
        
    Returns:
        Dictionary with user info and tokens, or None if failed
    """
    api_key = get_firebase_api_key()
    if not api_key:
        raise Exception("Firebase Web API Key not configured. Please set FIREBASE_WEB_API_KEY in environment.")
    
    url = f"{FIREBASE_AUTH_URL}:signInWithPassword?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        error_data = e.response.json().get('error', {})
        error_message = error_data.get('message', str(e))
        raise Exception(error_message)
    except Exception as e:
        raise Exception(f"Firebase signin failed: {e}")

