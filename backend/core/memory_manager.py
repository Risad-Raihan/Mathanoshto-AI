"""
Memory Manager - Core system for long-term context memory
Handles embedding generation, vector search, and memory management
"""
import os
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Embedding models
from sentence_transformers import SentenceTransformer
import chromadb

# Database
from sqlalchemy.orm import Session
from backend.database.memory_models import Memory, MemoryVersion, MemoryRelationship, MemoryAccess
from backend.database.operations import get_db

# LLM for memory extraction
from backend.providers.base import BaseLLMProvider


class MemoryEmbedder:
    """
    Handles embedding generation for memories
    Uses sentence-transformers for local embeddings with OpenAI as fallback
    """
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initialize embedder
        
        Args:
            model_name: Sentence transformer model name
                       Default: 'all-MiniLM-L6-v2' (384 dimensions, fast, good quality)
                       Other options: 'all-mpnet-base-v2' (768 dim, slower, better quality)
        """
        self.model_name = model_name
        self.model = None
        self.embedding_dim = 384  # Default for MiniLM
        self._initialize_model()
    
    def _initialize_model(self):
        """Lazy load the embedding model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            print(f"✅ Loaded embedding model: {self.model_name} ({self.embedding_dim} dimensions)")
        except Exception as e:
            print(f"⚠️ Failed to load sentence-transformers model: {e}")
            print("Memory system will use fallback (OpenAI embeddings)")
            self.model = None
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for text
        
        Args:
            text: Text to embed
        
        Returns:
            List of floats representing the embedding vector
        """
        if not text or not text.strip():
            return None
        
        try:
            if self.model:
                # Use local sentence-transformers
                embedding = self.model.encode(text, convert_to_numpy=True)
                return embedding.tolist()
            else:
                # Fallback to OpenAI embeddings
                return self._generate_openai_embedding(text)
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def _generate_openai_embedding(self, text: str) -> Optional[List[float]]:
        """
        Fallback to OpenAI embeddings API
        
        Args:
            text: Text to embed
        
        Returns:
            Embedding vector or None
        """
        try:
            import openai
            
            # Get API key from environment
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return None
            
            client = openai.OpenAI(api_key=api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            print(f"OpenAI embedding fallback failed: {e}")
            return None
    
    def batch_generate_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts efficiently
        
        Args:
            texts: List of texts to embed
        
        Returns:
            List of embedding vectors
        """
        if not self.model:
            # Process one by one with fallback
            return [self.generate_embedding(text) for text in texts]
        
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=len(texts) > 10)
            return [emb.tolist() for emb in embeddings]
        except Exception as e:
            print(f"Batch embedding error: {e}")
            return [self.generate_embedding(text) for text in texts]
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score (0-1, higher = more similar)
        """
        try:
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Cosine similarity
            similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            
            # Normalize to 0-1
            return float((similarity + 1) / 2)
        
        except Exception as e:
            print(f"Similarity computation error: {e}")
            return 0.0


class VectorStore:
    """
    ChromaDB vector store for semantic search
    """
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        """
        Initialize ChromaDB vector store
        
        Args:
            persist_directory: Directory to persist the vector database
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client (new API)
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Create or get collection
        self.collection = self.client.get_or_create_collection(
            name="memories",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        print(f"✅ ChromaDB initialized at {self.persist_directory}")
    
    def add_memory(
        self,
        memory_id: int,
        embedding: List[float],
        content: str,
        metadata: Dict
    ):
        """
        Add a memory to the vector store
        
        Args:
            memory_id: Memory ID from database
            embedding: Embedding vector
            content: Memory content text
            metadata: Additional metadata
        """
        try:
            self.collection.add(
                ids=[str(memory_id)],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Error adding memory to vector store: {e}")
    
    def search_similar(
        self,
        query_embedding: List[float],
        n_results: int = 10,
        where_filter: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar memories
        
        Args:
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where_filter: Optional metadata filter
        
        Returns:
            List of similar memories with scores
        """
        try:
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter
            )
            
            # Format results
            memories = []
            for i in range(len(results['ids'][0])):
                memories.append({
                    'id': int(results['ids'][0][i]),
                    'distance': results['distances'][0][i],
                    'similarity': 1 - results['distances'][0][i],  # Convert distance to similarity
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i]
                })
            
            return memories
        
        except Exception as e:
            print(f"Vector search error: {e}")
            return []
    
    def delete_memory(self, memory_id: int):
        """Delete a memory from vector store"""
        try:
            self.collection.delete(ids=[str(memory_id)])
        except Exception as e:
            print(f"Error deleting memory from vector store: {e}")
    
    def update_memory(
        self,
        memory_id: int,
        embedding: List[float],
        content: str,
        metadata: Dict
    ):
        """Update a memory in vector store"""
        try:
            self.collection.update(
                ids=[str(memory_id)],
                embeddings=[embedding],
                documents=[content],
                metadatas=[metadata]
            )
        except Exception as e:
            print(f"Error updating memory in vector store: {e}")


class MemoryManager:
    """
    Main memory management system
    Handles creation, retrieval, and lifecycle of memories
    """
    
    def __init__(
        self,
        db: Session,
        embedder: Optional[MemoryEmbedder] = None,
        vector_store: Optional[VectorStore] = None
    ):
        """
        Initialize memory manager
        
        Args:
            db: Database session
            embedder: Memory embedder instance
            vector_store: Vector store instance
        """
        self.db = db
        self.embedder = embedder or MemoryEmbedder()
        self.vector_store = vector_store or VectorStore()
    
    def create_memory(
        self,
        user_id: int,
        content: str,
        memory_type: str,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        importance_score: float = 0.5,
        source_type: str = 'manual',
        source_id: Optional[str] = None,
        confidence: float = 1.0,
        meta_data: Optional[Dict] = None,
        is_pinned: bool = False
    ) -> Optional[Memory]:
        """
        Create a new memory
        
        Args:
            user_id: User ID
            content: Memory content text
            memory_type: Type of memory (personal_info, preference, fact, etc.)
            category: Optional subcategory
            tags: List of tags
            importance_score: Importance score (0-1)
            source_type: How memory was created
            source_id: Reference to source
            confidence: Confidence in memory (0-1)
            meta_data: Additional metadata
            is_pinned: Whether to always include in context
        
        Returns:
            Created Memory object or None
        """
        try:
            # Generate embedding
            embedding = self.embedder.generate_embedding(content)
            if not embedding:
                print("Failed to generate embedding")
                return None
            
            # Create memory object
            memory = Memory(
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                category=category,
                tags=tags or [],
                embedding=embedding,
                embedding_model=self.embedder.model_name,
                importance_score=importance_score,
                source_type=source_type,
                source_id=source_id,
                confidence=confidence,
                meta_data=meta_data or {},
                is_pinned=is_pinned
            )
            
            # Save to database
            self.db.add(memory)
            self.db.commit()
            self.db.refresh(memory)
            
            # Add to vector store
            self.vector_store.add_memory(
                memory_id=memory.id,
                embedding=embedding,
                content=content,
                metadata={
                    'user_id': int(user_id),  # Ensure integer for consistent filtering
                    'memory_type': memory_type,
                    'category': category or '',
                    'importance': importance_score,
                    'created_at': memory.created_at.isoformat()
                }
            )
            
            print(f"✅ Created memory #{memory.id} for user {user_id}")
            return memory
        
        except Exception as e:
            print(f"Error creating memory: {e}")
            self.db.rollback()
            return None
    
    def search_memories(
        self,
        user_id: int,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.5,
        include_inactive: bool = False
    ) -> List[Tuple[Memory, float]]:
        """
        Search for relevant memories using semantic search
        
        Args:
            user_id: User ID
            query: Search query
            memory_types: Filter by memory types
            limit: Maximum results
            min_similarity: Minimum similarity threshold
            include_inactive: Include inactive memories
        
        Returns:
            List of (Memory, similarity_score) tuples
        """
        try:
            # Generate query embedding
            query_embedding = self.embedder.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Build metadata filter
            where_filter = {'user_id': user_id}
            
            # Search vector store
            similar_memories = self.vector_store.search_similar(
                query_embedding=query_embedding,
                n_results=limit * 2,  # Get more than needed for filtering
                where_filter={'user_id': user_id}  # Keep as integer to match stored type
            )
            
            # Fetch full memory objects and apply filters
            results = []
            for mem_result in similar_memories:
                if mem_result['similarity'] < min_similarity:
                    continue
                
                # Get memory from database
                memory = self.db.query(Memory).filter(
                    Memory.id == mem_result['id']
                ).first()
                
                if not memory:
                    continue
                
                # Apply filters
                if not include_inactive and not memory.is_active:
                    continue
                
                if memory_types and memory.memory_type not in memory_types:
                    continue
                
                # Update access tracking
                memory.access_count += 1
                memory.last_accessed = datetime.utcnow()
                
                results.append((memory, mem_result['similarity']))
                
                if len(results) >= limit:
                    break
            
            self.db.commit()
            
            return results
        
        except Exception as e:
            print(f"Error searching memories: {e}")
            return []
    
    def get_pinned_memories(self, user_id: int) -> List[Memory]:
        """Get all pinned memories for a user"""
        return self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_pinned == True,
            Memory.is_active == True
        ).all()
    
    def get_memories_by_type(
        self,
        user_id: int,
        memory_type: str,
        limit: int = 50
    ) -> List[Memory]:
        """Get memories by type"""
        return self.db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.memory_type == memory_type,
            Memory.is_active == True
        ).order_by(Memory.importance_score.desc()).limit(limit).all()
    
    def update_memory(
        self,
        memory_id: int,
        content: Optional[str] = None,
        importance_score: Optional[float] = None,
        tags: Optional[List[str]] = None,
        is_pinned: Optional[bool] = None,
        is_verified: Optional[bool] = None
    ) -> Optional[Memory]:
        """Update an existing memory"""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if not memory:
                return None
            
            # Create version before updating
            version = MemoryVersion(
                memory_id=memory.id,
                version_number=len(memory.versions) + 1,
                content=memory.content,
                change_reason="Updated",
                changed_by="user"
            )
            self.db.add(version)
            
            # Update fields
            if content is not None:
                memory.content = content
                # Regenerate embedding
                embedding = self.embedder.generate_embedding(content)
                if embedding:
                    memory.embedding = embedding
                    # Update vector store
                    self.vector_store.update_memory(
                        memory_id=memory.id,
                        embedding=embedding,
                        content=content,
                        metadata={
                            'user_id': int(memory.user_id),  # Ensure integer
                            'memory_type': memory.memory_type,
                            'importance': memory.importance_score
                        }
                    )
            
            if importance_score is not None:
                memory.importance_score = importance_score
            
            if tags is not None:
                memory.tags = tags
            
            if is_pinned is not None:
                memory.is_pinned = is_pinned
            
            if is_verified is not None:
                memory.is_verified = is_verified
            
            memory.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(memory)
            
            return memory
        
        except Exception as e:
            print(f"Error updating memory: {e}")
            self.db.rollback()
            return None
    
    def delete_memory(self, memory_id: int, soft_delete: bool = True):
        """Delete a memory (soft or hard)"""
        try:
            memory = self.db.query(Memory).filter(Memory.id == memory_id).first()
            if not memory:
                return False
            
            if soft_delete:
                memory.is_active = False
                self.db.commit()
            else:
                # Hard delete
                self.vector_store.delete_memory(memory_id)
                self.db.delete(memory)
                self.db.commit()
            
            return True
        
        except Exception as e:
            print(f"Error deleting memory: {e}")
            self.db.rollback()
            return False
    
    def calculate_importance_decay(self, memory: Memory) -> float:
        """
        Calculate decayed importance based on age and access patterns
        
        Args:
            memory: Memory object
        
        Returns:
            Decayed importance score
        """
        # Age decay (memories older than 30 days start to decay)
        age_days = (datetime.utcnow() - memory.created_at).days
        age_decay = 1.0 if age_days < 30 else max(0.5, 1.0 - (age_days - 30) / 365)
        
        # Access frequency boost (recently accessed memories are more important)
        days_since_access = (datetime.utcnow() - memory.last_accessed).days if memory.last_accessed else age_days
        access_boost = 1.0 if days_since_access < 7 else max(0.8, 1.0 - days_since_access / 90)
        
        # Access count boost (frequently accessed memories are more important)
        access_count_boost = min(1.5, 1.0 + memory.access_count / 20)
        
        # Calculate final score
        base_importance = memory.importance_score
        decayed_importance = base_importance * age_decay * access_boost * access_count_boost
        
        return min(1.0, decayed_importance)


def get_memory_manager(db: Session) -> MemoryManager:
    """Get memory manager instance (creates new instance each time for thread safety)"""
    return MemoryManager(db)

