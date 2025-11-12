#!/usr/bin/env python3
"""
Memory System Setup Script
Initializes database tables and verifies installation
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def main():
    print("🧠 Setting up Memory System...")
    print("=" * 50)
    
    # Step 1: Check dependencies
    print("\n1️⃣  Checking dependencies...")
    try:
        import chromadb
        import sentence_transformers
        import torch
        print("   ✅ All dependencies installed")
    except ImportError as e:
        print(f"   ❌ Missing dependency: {e}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    # Step 2: Initialize database tables
    print("\n2️⃣  Initializing database tables...")
    try:
        from backend.database.memory_operations import init_memory_tables
        init_memory_tables()
        print("   ✅ Memory tables created")
    except Exception as e:
        print(f"   ❌ Error creating tables: {e}")
        return False
    
    # Step 3: Test embedding model
    print("\n3️⃣  Testing embedding model...")
    try:
        from backend.core.memory_manager import MemoryEmbedder
        embedder = MemoryEmbedder()
        test_embedding = embedder.generate_embedding("Test embedding")
        if test_embedding:
            print(f"   ✅ Embedding model loaded ({len(test_embedding)} dimensions)")
        else:
            print("   ⚠️  Embedding model not loaded (will use OpenAI fallback)")
    except Exception as e:
        print(f"   ⚠️  Warning: {e}")
        print("   You can still use the system with OpenAI embeddings")
    
    # Step 4: Initialize ChromaDB
    print("\n4️⃣  Initializing vector database...")
    try:
        from backend.core.memory_manager import VectorStore
        vector_store = VectorStore()
        print("   ✅ ChromaDB initialized")
    except Exception as e:
        print(f"   ❌ Error initializing ChromaDB: {e}")
        return False
    
    # Step 5: Verify setup
    print("\n5️⃣  Verifying setup...")
    try:
        from backend.database.operations import get_db
        from backend.core.memory_manager import get_memory_manager
        
        # Get a database session to test
        db = get_db()
        try:
            memory_manager = get_memory_manager(db)
            print("   ✅ Memory manager ready")
        finally:
            db.close()
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Success!
    print("\n" + "=" * 50)
    print("✨ Memory System Setup Complete! ✨")
    print("=" * 50)
    print("\n📖 Next steps:")
    print("   1. Start the app: streamlit run frontend/streamlit/app.py")
    print("   2. Log in to your account")
    print("   3. Click the 🧠 icon to access Memory System")
    print("   4. Read the guide: docs/MEMORY_SYSTEM_GUIDE.md")
    print("\n🎉 Your AI now has long-term memory!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

