# Firebase Authentication Setup Guide

This guide explains how to set up Firebase Authentication for the Mathanoshto AI application.

## Overview

The application now supports **Firebase Authentication** using a hybrid approach:
- **Firebase** handles user authentication (sign-in, sign-up, password reset)
- **Your SQLite/PostgreSQL database** stores user preferences, API keys, conversations, and app-specific data
- Users are linked via `firebase_uid` in your database

## Benefits

✅ **Cross-platform**: Works for web (Streamlit) and Android apps  
✅ **Secure**: Firebase handles password hashing, token management, OAuth providers  
✅ **Scalable**: No need to manage authentication infrastructure  
✅ **User-friendly**: Supports Google Sign-In, email/password, phone auth, etc.  
✅ **Persistent**: User accounts persist across Docker container restarts  

## Setup Steps

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or select an existing project
3. Follow the setup wizard

### 2. Enable Authentication

1. In Firebase Console, go to **Authentication** → **Get Started**
2. Enable **Email/Password** authentication (and any other providers you want)
3. Optionally enable:
   - Google Sign-In
   - Phone Authentication
   - Other OAuth providers

### 3. Get Service Account Credentials

1. In Firebase Console, go to **Project Settings** (gear icon)
2. Go to **Service Accounts** tab
3. Click **Generate New Private Key**
4. Save the JSON file as `firebase-credentials.json` in your project root

**⚠️ Important**: Add `firebase-credentials.json` to `.gitignore` to keep it secure!

### 4. Configure Environment Variables

Add to your `.env` file (or set environment variables):

```bash
# Firebase Configuration
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
USE_FIREBASE_AUTH=true
```

Or place `firebase-credentials.json` in the project root (it will be auto-detected).

### 5. Install Dependencies

The Firebase Admin SDK is already in `requirements.txt`. Install it:

```bash
pip install -r requirements.txt
```

Or if using Docker:

```bash
docker-compose build
```

### 6. Database Migration

The database schema has been updated to support Firebase. Existing users will continue to work with username/password.

To check your users:

```bash
python scripts/migrate_to_firebase.py
```

## Usage

### For Web (Streamlit)

1. **Get Firebase ID Token**:
   - Users can get their Firebase ID token from:
     - Firebase Console (for testing)
     - Your Android app (automatically)
     - A custom web component (future enhancement)

2. **Sign In**:
   - Go to the login page
   - Click "🔥 Sign in with Firebase Token"
   - Paste your Firebase ID token
   - Click "Sign In with Firebase"

3. **Legacy Login** (still supported):
   - Username/password login still works for existing users
   - New users created via Firebase will be automatically linked

### For Android App

1. Use Firebase Android SDK to authenticate users
2. Get the Firebase ID token: `FirebaseAuth.getInstance().getCurrentUser().getIdToken()`
3. Send the token to your backend API
4. Backend verifies token and creates/gets user in database

### API Endpoint (for Android)

You can create an API endpoint that accepts Firebase tokens:

```python
# Example API endpoint (add to your backend)
@app.post("/api/auth/firebase")
def authenticate_firebase(token: str):
    user = UserDB.authenticate_with_firebase(token)
    if user:
        return {"success": True, "user_id": user.id}
    return {"success": False, "error": "Invalid token"}
```

## Configuration Options

In `backend/config/settings.py`:

- `use_firebase_auth`: Enable/disable Firebase Authentication (default: `True`)
- `firebase_credentials_path`: Path to Firebase service account JSON file
- `firebase_project_id`: Firebase project ID (optional, auto-detected from credentials)

## Migration Strategy

### Existing Users

- **Legacy users** (username/password) continue to work
- When a user logs in with Firebase token using the **same email**, they are automatically linked
- After linking, they can use either authentication method

### New Users

- **Recommended**: Sign up through Firebase (Android app or Firebase Console)
- Then sign in with Firebase token
- Legacy signup (username/password) still works but is not recommended for new users

## Troubleshooting

### Firebase Not Initialized

**Error**: `Firebase credentials not found`

**Solution**:
1. Ensure `firebase-credentials.json` exists in project root
2. Or set `FIREBASE_CREDENTIALS_PATH` environment variable
3. Check file permissions

### Invalid Token Error

**Error**: `Invalid Firebase ID token`

**Solution**:
1. Ensure token is not expired (Firebase tokens expire after 1 hour)
2. Verify Firebase project is correctly configured
3. Check that Authentication is enabled in Firebase Console

### Database Migration Issues

**Error**: `Column 'firebase_uid' does not exist`

**Solution**:
1. The database schema auto-updates on first run
2. If issues persist, delete `data/chat_history.db` and restart (⚠️ This deletes all data!)

## Security Notes

1. **Never commit** `firebase-credentials.json` to git
2. Use environment variables for production
3. Firebase tokens expire after 1 hour - implement token refresh
4. Use HTTPS in production
5. Validate tokens on every request

## Next Steps

1. ✅ Set up Firebase project
2. ✅ Add credentials file
3. ✅ Test authentication
4. 🔄 Build Android app with Firebase SDK
5. 🔄 Create API endpoints for mobile app
6. 🔄 Add token refresh mechanism

## Support

For issues or questions:
- Check Firebase Console for authentication logs
- Review `backend/auth/firebase_auth.py` for implementation details
- Check `scripts/migrate_to_firebase.py` for user migration info

