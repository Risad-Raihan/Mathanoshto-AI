#!/usr/bin/env python3
"""
Database migration script to add File Management tables (Phase 3)
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database.operations import init_database, engine
from backend.database.models import Base, File, FileTag, ConversationFile
from sqlalchemy import inspect


def check_table_exists(table_name: str) -> bool:
    """Check if a table exists in the database"""
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()


def migrate_file_tables():
    """Add file management tables to the database"""
    print("=" * 60)
    print("Phase 3: File Management System - Database Migration")
    print("=" * 60)
    print()
    
    # Check existing tables
    existing_tables = {
        'files': check_table_exists('files'),
        'file_tags': check_table_exists('file_tags'),
        'conversation_files': check_table_exists('conversation_files')
    }
    
    print("Checking existing tables...")
    for table, exists in existing_tables.items():
        status = "✓ EXISTS" if exists else "✗ MISSING"
        print(f"  {table}: {status}")
    
    print()
    
    # If all tables exist, ask for confirmation to recreate
    if all(existing_tables.values()):
        print("⚠️  All file management tables already exist!")
        response = input("Do you want to recreate them? This will DROP existing tables! (yes/no): ")
        if response.lower() != 'yes':
            print("Migration cancelled.")
            return
        
        print("\nDropping existing file management tables...")
        File.__table__.drop(engine, checkfirst=True)
        FileTag.__table__.drop(engine, checkfirst=True)
        ConversationFile.__table__.drop(engine, checkfirst=True)
        print("✓ Tables dropped")
    
    # Create new tables
    print("\nCreating file management tables...")
    try:
        # Create only the file-related tables
        File.__table__.create(engine, checkfirst=True)
        print("✓ Created 'files' table")
        
        FileTag.__table__.create(engine, checkfirst=True)
        print("✓ Created 'file_tags' table")
        
        ConversationFile.__table__.create(engine, checkfirst=True)
        print("✓ Created 'conversation_files' table")
        
        print("\n" + "=" * 60)
        print("✅ Migration completed successfully!")
        print("=" * 60)
        print("\nNew tables created:")
        print("  1. files - Main file storage table")
        print("  2. file_tags - Tags for organizing files")
        print("  3. conversation_files - Links files to conversations/messages")
        print("\nYou can now use the file management features!")
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def verify_migration():
    """Verify that migration was successful"""
    print("\nVerifying migration...")
    
    try:
        from sqlalchemy import text
        
        with engine.connect() as conn:
            # Check files table
            result = conn.execute(text("SELECT COUNT(*) FROM files"))
            file_count = result.scalar()
            print(f"✓ Files table accessible (contains {file_count} records)")
            
            # Check file_tags table
            result = conn.execute(text("SELECT COUNT(*) FROM file_tags"))
            tag_count = result.scalar()
            print(f"✓ File tags table accessible (contains {tag_count} records)")
            
            # Check conversation_files table
            result = conn.execute(text("SELECT COUNT(*) FROM conversation_files"))
            conv_file_count = result.scalar()
            print(f"✓ Conversation files table accessible (contains {conv_file_count} records)")
        
        print("\n✅ All tables verified successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Verification failed: {str(e)}")
        return False


if __name__ == "__main__":
    print()
    migrate_file_tables()
    print()
    verify_migration()
    print()

