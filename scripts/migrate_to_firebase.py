#!/usr/bin/env python3
"""
Migration script for existing users to Firebase Authentication
This script helps migrate existing username/password users to Firebase
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from backend.database.operations import init_database, get_db
from backend.database.models import User
from backend.config.settings import settings


def migrate_existing_users():
    """
    Display information about existing users and their migration status
    """
    print("=" * 60)
    print("Firebase Migration Helper")
    print("=" * 60)
    print()
    
    # Initialize database
    init_database()
    
    db = get_db()
    try:
        # Get all users
        users = db.query(User).all()
        
        if not users:
            print("No users found in database.")
            return
        
        print(f"Found {len(users)} user(s) in database:\n")
        
        firebase_users = 0
        legacy_users = 0
        
        for user in users:
            if user.firebase_uid:
                firebase_users += 1
                status = "✅ Firebase User"
            else:
                legacy_users += 1
                status = "🔐 Legacy User (username/password)"
            
            print(f"  User ID: {user.id}")
            print(f"    Username: {user.username or 'N/A'}")
            print(f"    Email: {user.email or 'N/A'}")
            print(f"    Full Name: {user.full_name or 'N/A'}")
            print(f"    Status: {status}")
            print(f"    Firebase UID: {user.firebase_uid or 'Not set'}")
            print()
        
        print("=" * 60)
        print(f"Summary:")
        print(f"  Firebase Users: {firebase_users}")
        print(f"  Legacy Users: {legacy_users}")
        print(f"  Total Users: {len(users)}")
        print()
        print("Note: Legacy users can still login with username/password.")
        print("      They will be automatically linked to Firebase when they")
        print("      first login with a Firebase token (same email).")
        print("=" * 60)
        
    finally:
        db.close()


if __name__ == "__main__":
    migrate_existing_users()

