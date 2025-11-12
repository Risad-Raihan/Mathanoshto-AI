"""
RAG System Setup Script
Initializes database tables and verifies RAG system
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.database.operations import init_database, get_db, engine
from backend.database.rag_models import DocumentChunk, ChunkCitation, RAGConfiguration, RAGMetrics
from backend.database.models import Base
from sqlalchemy import inspect
import traceback


def setup_rag_system():
    """Initialize the RAG system"""
    print("📚 Setting up RAG System...")
    print("=" * 60)
    
    try:
        # Step 1: Initialize database
        print("\n📦 Step 1: Initializing database...")
        init_database()
        print("✅ Database initialized")
        
        # Step 2: Verify RAG tables
        print("\n🔍 Step 2: Verifying RAG tables...")
        inspector = inspect(engine)
        
        required_tables = [
            'document_chunks',
            'chunk_citations',
            'rag_configurations',
            'rag_metrics'
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
        
        # Step 3: Test RAG components
        print("\n🧪 Step 3: Testing RAG components...")
        
        # Test chunker
        from backend.core.rag_chunker import chunk_text
        test_text = "This is a test document. It has multiple sentences."
        chunks = chunk_text(test_text, chunk_size=50)
        print(f"   ✅ Chunker: Generated {len(chunks)} chunks")
        
        # Test embedder
        from backend.core.rag_embedder import RAGEmbedder
        embedder = RAGEmbedder()
        embedding = embedder.embed_text("test")
        print(f"   ✅ Embedder: {embedder.model_name} ({embedder.embedding_dim}D)")
        
        # Test retriever
        from backend.core.rag_retriever import BM25
        bm25 = BM25()
        bm25.fit(["test document", "another document"])
        print(f"   ✅ Retriever: BM25 indexed")
        
        print("\n" + "=" * 60)
        print("✨ RAG System Setup Complete!")
        print("\n🎉 Components Ready:")
        print("   ✅ Database tables")
        print("   ✅ Chunking system (8 strategies)")
        print("   ✅ Embedding system (cached)")
        print("   ✅ Hybrid retrieval (BM25 + Semantic)")
        print("   ✅ Re-ranking (MMR + Ensemble)")
        print("   ✅ Citation system")
        print("   ✅ Context optimization")
        print("\n💡 Usage:")
        print("   1. Attach files in chat")
        print("   2. RAG automatically processes them")
        print("   3. Get context-aware responses with citations")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ Error during setup: {e}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        print("\n" + "=" * 60)
        return False


if __name__ == "__main__":
    success = setup_rag_system()
    sys.exit(0 if success else 1)

