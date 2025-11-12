"""
Conversation Insights System Setup Script
Initializes database tables for smart features
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.database.operations import init_database, get_db, engine
from backend.database.conversation_insights_models import (
    ConversationSummary,
    ConversationInsight,
    ConversationSuggestion,
    ConversationExport,
    UserPromptLibrary
)
from backend.database.models import Base
from sqlalchemy import inspect
import traceback


def setup_conversation_insights():
    """Initialize the Conversation Insights system"""
    print("🧠 Setting up Conversation Insights System...")
    print("=" * 60)
    
    try:
        # Step 1: Initialize database
        print("\n📦 Step 1: Initializing database...")
        init_database()
        print("✅ Database initialized")
        
        # Step 2: Verify Insights tables
        print("\n🔍 Step 2: Verifying Conversation Insights tables...")
        inspector = inspect(engine)
        
        required_tables = [
            'conversation_summaries',
            'conversation_insights',
            'conversation_suggestions',
            'conversation_exports',
            'user_prompt_library'
        ]
        
        existing_tables = inspector.get_table_names()
        
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing - creating...")
                Base.metadata.create_all(bind=engine, tables=[
                    Base.metadata.tables.get(table)
                ])
                print(f"   ✅ Table '{table}' created")
        
        # Step 3: Verify all tables were created
        print("\n📊 Step 3: Final verification...")
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        insights_tables = [t for t in all_tables if t in required_tables]
        print(f"   ✅ {len(insights_tables)}/{len(required_tables)} Insights tables verified")
        
        # Step 4: Summary
        print("\n" + "=" * 60)
        print("✅ Conversation Insights System setup complete!")
        print("\n📋 Features enabled:")
        print("   • Conversation Summarization (multi-level)")
        print("   • Conversation Continuation Suggestions")
        print("   • Smart Prompt Suggestions")
        print("   • Automatic Follow-up Questions")
        print("   • Conversation Insights & Analytics")
        print("   • AI-Powered Export System")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during setup: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = setup_conversation_insights()
    sys.exit(0 if success else 1)

