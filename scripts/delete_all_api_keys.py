#!/usr/bin/env python3
"""
Script to delete all API keys from the database
Run this script to clear all existing API keys before testing the duplicate key feature
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.user_operations import UserAPIKeyDB
from backend.database.operations import get_db
from backend.database.models import UserAPIKey

def delete_all_api_keys():
    """Delete all API keys from the database"""
    db = get_db()
    try:
        count = db.query(UserAPIKey).count()
        print(f"Found {count} API key(s) in the database")
        
        if count > 0:
            db.query(UserAPIKey).delete()
            db.commit()
            print(f"✅ Successfully deleted {count} API key(s)")
        else:
            print("ℹ️  No API keys found in the database")
    except Exception as e:
        db.rollback()
        print(f"❌ Error deleting API keys: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("🗑️  Deleting all API keys from the database...")
    print("=" * 50)
    
    try:
        delete_all_api_keys()
        print("=" * 50)
        print("✅ Done!")
    except Exception as e:
        print("=" * 50)
        print(f"❌ Failed: {str(e)}")
        sys.exit(1)

