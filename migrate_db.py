"""
Database migration script to add user_id to existing tables
"""
import sqlite3
import os

DB_PATH = "chat_history.db"

def migrate_database():
    """Migrate existing database to new schema with user_id"""
    
    if not os.path.exists(DB_PATH):
        print("❌ Database not found. Run init_database() first.")
        return
    
    print("🔄 Starting database migration...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if user_id column already exists
        cursor.execute("PRAGMA table_info(conversations)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' in columns:
            print("✅ Database already migrated!")
            return
        
        print("📝 Backing up existing data...")
        
        # Backup conversations
        cursor.execute("SELECT * FROM conversations")
        conversations = cursor.fetchall()
        
        # Backup messages
        cursor.execute("SELECT * FROM messages")
        messages = cursor.fetchall()
        
        print(f"   Found {len(conversations)} conversations and {len(messages)} messages")
        
        # Drop old tables
        print("🗑️  Dropping old tables...")
        cursor.execute("DROP TABLE IF EXISTS tool_calls")
        cursor.execute("DROP TABLE IF EXISTS attachments")
        cursor.execute("DROP TABLE IF EXISTS messages")
        cursor.execute("DROP TABLE IF EXISTS conversations")
        
        # Commit the drops
        conn.commit()
        
        print("✅ Old tables dropped. Reinitializing with new schema...")
        
        # Close connection
        conn.close()
        
        # Reinitialize database with new schema
        from backend.database.operations import init_database
        init_database()
        
        print("✅ Database migrated successfully!")
        print("\n⚠️  IMPORTANT: All old conversations have been deleted.")
        print("   This is because we need to assign them to users.")
        print("   Run: python init_users.py to create user accounts")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE MIGRATION SCRIPT")
    print("=" * 60)
    print("\nThis will delete all existing conversations!")
    print("(They need to be assigned to users)")
    
    response = input("\nContinue? (yes/no): ").lower()
    
    if response == 'yes':
        migrate_database()
    else:
        print("❌ Migration cancelled")

