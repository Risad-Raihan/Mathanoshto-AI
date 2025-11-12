"""
Setup script for AI Agent System
Initializes database tables and loads pre-defined agents
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.database.operations import init_database, get_db
from backend.core.agent_manager import get_agent_manager
from backend.database.agent_models import Agent, AgentVersion, AgentSession
from backend.database.memory_models import Memory, MemoryVersion, MemoryRelationship  # Import memory models
from backend.database.models import Base
from sqlalchemy import create_engine, inspect
import traceback


def setup_agent_system():
    """Initialize the agent system"""
    print("🤖 Setting up AI Agent System...")
    print("=" * 60)
    
    try:
        # Step 1: Initialize database (creates tables if they don't exist)
        print("\n📦 Step 1: Initializing database...")
        init_database()
        print("✅ Database initialized")
        
        # Step 2: Verify agent tables exist
        print("\n🔍 Step 2: Verifying agent tables...")
        from backend.database.operations import engine
        inspector = inspect(engine)
        
        required_tables = ['agents', 'agent_versions', 'agent_sessions']
        existing_tables = inspector.get_table_names()
        
        for table in required_tables:
            if table in existing_tables:
                print(f"   ✅ Table '{table}' exists")
            else:
                print(f"   ❌ Table '{table}' missing - creating...")
                # Create missing tables
                Base.metadata.create_all(bind=engine, tables=[
                    Base.metadata.tables.get(table)
                ])
                print(f"   ✅ Table '{table}' created")
        
        # Step 3: Initialize pre-defined agents
        print("\n🎭 Step 3: Loading pre-defined agents...")
        db = get_db()
        agent_manager = get_agent_manager(db)
        
        # Check how many system agents already exist
        existing_agents = agent_manager.get_all_agents(is_active=True, include_custom=False)
        existing_system_agents = [a for a in existing_agents if a.is_system]
        
        if len(existing_system_agents) >= 10:
            print(f"   ℹ️  {len(existing_system_agents)} system agents already exist")
            print("   ⏭️  Skipping initialization (agents already loaded)")
        else:
            print("   📝 Loading 10 pre-defined agents...")
            created_agents = agent_manager.initialize_system_agents()
            print(f"   ✅ Loaded {len(created_agents)} agents successfully")
        
        # Step 4: Display agent summary
        print("\n📊 Step 4: Agent Summary...")
        all_agents = agent_manager.get_all_agents(is_active=True, include_custom=True, user_id=None)
        system_agents = [a for a in all_agents if a.is_system]
        
        print(f"   Total Active Agents: {len(all_agents)}")
        print(f"   System Agents: {len(system_agents)}")
        
        # List all system agents
        print("\n   📋 Available System Agents:")
        for agent in system_agents:
            print(f"      {agent.emoji} {agent.name} ({agent.category})")
        
        db.close()
        
        # Step 5: Test agent retrieval
        print("\n🧪 Step 5: Testing agent system...")
        db = get_db()
        agent_manager = get_agent_manager(db)
        
        # Test getting an agent by name
        test_agent = agent_manager.get_agent_by_name("Research Agent")
        if test_agent:
            print(f"   ✅ Successfully retrieved '{test_agent.name}'")
            print(f"      Temperature: {test_agent.temperature}")
            print(f"      Max Tokens: {test_agent.max_tokens}")
            print(f"      Tools: {', '.join(test_agent.allowed_tools[:3])}...")
        else:
            print("   ❌ Failed to retrieve test agent")
        
        db.close()
        
        print("\n" + "=" * 60)
        print("✨ Agent System Setup Complete!")
        print("\n🎉 You can now:")
        print("   1. Select agents from the sidebar in the Streamlit app")
        print("   2. Create custom agents in the Agent Manager")
        print("   3. Use specialized agents for different tasks")
        print("\n💡 To start the app, run: streamlit run frontend/streamlit/app.py")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error during setup: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        print("\n" + "=" * 60)
        return False


if __name__ == "__main__":
    success = setup_agent_system()
    sys.exit(0 if success else 1)

