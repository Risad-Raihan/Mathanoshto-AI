# Firebase Web API Key Setup

To enable Firebase email/password signup and login directly in the web app, you need to add your Firebase Web API Key.

## How to Get Firebase Web API Key

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **Mathanoshto-AI**
3. Click the **gear icon** (⚙️) → **Project settings**
4. Go to the **General** tab
5. Scroll down to **Your apps** section
6. Look for **Web API Key** (it's a long string like `AIzaSy...`)
7. Copy this key

## Add to Your Environment

### Option 1: Add to .env file

Create or edit `.env` file in project root:

```bash
FIREBASE_WEB_API_KEY=your-api-key-here
```

### Option 2: Set Environment Variable

```bash
export FIREBASE_WEB_API_KEY=your-api-key-here
```

### Option 3: Add to docker-compose.yml

Add to the `environment` section:

```yaml
environment:
  - FIREBASE_WEB_API_KEY=your-api-key-here
```

## After Adding the Key

Once you add the Firebase Web API Key:

✅ **Sign Up Tab**: Users can create accounts with email/password directly  
✅ **Sign In Tab**: Users can login with email/password directly  
✅ **No token pasting needed**: Everything works seamlessly  

The app will automatically detect the key and enable Firebase REST API authentication.

## Security Note

The Web API Key is safe to expose in client-side code (it's public). However, Firebase has security rules that protect your backend. The key is used for authentication only, not for accessing your database or admin functions.

