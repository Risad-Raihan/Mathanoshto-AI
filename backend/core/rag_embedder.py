"""
RAG Embedding System with Caching
Generates and caches embeddings for document chunks
"""

from typing import List, Optional, Dict, Union
import numpy as np
from pathlib import Path
import json
import hashlib
from datetime import datetime


class RAGEmbedder:
    """
    Embedding system for RAG with caching support
    Reuses the existing memory system's embedder when possible
    """
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        use_openai: bool = False,
        openai_model: str = "text-embedding-3-small",
        cache_dir: str = "data/rag_embeddings"
    ):
        """
        Initialize embedder
        
        Args:
            model_name: SentenceTransformer model name
            use_openai: Use OpenAI embeddings instead
            openai_model: OpenAI embedding model
            cache_dir: Directory for caching embeddings
        """
        self.model_name = model_name
        self.use_openai = use_openai
        self.openai_model = openai_model
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = None
        self.embedding_dim = None
        
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        if self.use_openai:
            # Use OpenAI embeddings
            try:
                import openai
                from backend.config import config
                
                openai.api_key = config.OPENAI_API_KEY
                self.embedding_dim = 1536  # text-embedding-3-small dimension
                
                print(f"✅ Using OpenAI embeddings: {self.openai_model}")
            except Exception as e:
                print(f"❌ Failed to initialize OpenAI embeddings: {e}")
                print("   Falling back to local model...")
                self.use_openai = False
                self._initialize_local_model()
        else:
            self._initialize_local_model()
    
    def _initialize_local_model(self):
        """Initialize local sentence-transformers model"""
        try:
            from sentence_transformers import SentenceTransformer
            
            self.model = SentenceTransformer(self.model_name)
            self.embedding_dim = self.model.get_sentence_embedding_dimension()
            
            print(f"✅ Loaded embedding model: {self.model_name} ({self.embedding_dim} dimensions)")
        except Exception as e:
            print(f"❌ Failed to load embedding model: {e}")
            raise
    
    def embed_text(self, text: str, use_cache: bool = True) -> Optional[np.ndarray]:
        """
        Generate embedding for a single text
        
        Args:
            text: Text to embed
            use_cache: Use cached embedding if available
        
        Returns:
            Embedding vector
        """
        if not text or not text.strip():
            return None
        
        # Check cache
        if use_cache:
            cached = self._get_cached_embedding(text)
            if cached is not None:
                return cached
        
        # Generate embedding
        try:
            if self.use_openai:
                embedding = self._embed_with_openai(text)
            else:
                embedding = self._embed_with_local(text)
            
            # Cache the embedding
            if use_cache and embedding is not None:
                self._cache_embedding(text, embedding)
            
            return embedding
        
        except Exception as e:
            print(f"Error generating embedding: {e}")
            return None
    
    def embed_batch(
        self,
        texts: List[str],
        use_cache: bool = True,
        show_progress: bool = False
    ) -> List[Optional[np.ndarray]]:
        """
        Generate embeddings for multiple texts (batch processing)
        
        Args:
            texts: List of texts to embed
            use_cache: Use cached embeddings if available
            show_progress: Show progress bar
        
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            if not text or not text.strip():
                embeddings.append(None)
                continue
            
            if use_cache:
                cached = self._get_cached_embedding(text)
                if cached is not None:
                    embeddings.append(cached)
                    continue
            
            # Need to embed this text
            embeddings.append(None)  # Placeholder
            texts_to_embed.append(text)
            indices_to_embed.append(i)
        
        # Batch embed uncached texts
        if texts_to_embed:
            try:
                if self.use_openai:
                    # OpenAI batch (max 2048 per request)
                    batch_size = 2048
                    new_embeddings = []
                    
                    for i in range(0, len(texts_to_embed), batch_size):
                        batch = texts_to_embed[i:i + batch_size]
                        batch_embs = self._embed_batch_openai(batch)
                        new_embeddings.extend(batch_embs)
                else:
                    # Local batch
                    new_embeddings = self._embed_batch_local(texts_to_embed, show_progress)
                
                # Insert embeddings and cache them
                for idx, embedding in zip(indices_to_embed, new_embeddings):
                    embeddings[idx] = embedding
                    if use_cache and embedding is not None:
                        self._cache_embedding(texts[idx], embedding)
            
            except Exception as e:
                print(f"Error in batch embedding: {e}")
        
        return embeddings
    
    def _embed_with_local(self, text: str) -> np.ndarray:
        """Embed with local model"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def _embed_batch_local(self, texts: List[str], show_progress: bool = False) -> List[np.ndarray]:
        """Batch embed with local model"""
        return self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress
        )
    
    def _embed_with_openai(self, text: str) -> np.ndarray:
        """Embed with OpenAI"""
        import openai
        
        response = openai.embeddings.create(
            model=self.openai_model,
            input=text
        )
        
        return np.array(response.data[0].embedding)
    
    def _embed_batch_openai(self, texts: List[str]) -> List[np.ndarray]:
        """Batch embed with OpenAI"""
        import openai
        
        response = openai.embeddings.create(
            model=self.openai_model,
            input=texts
        )
        
        return [np.array(item.embedding) for item in response.data]
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text"""
        # Use hash of text + model name
        content = f"{self.model_name}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def _get_cached_embedding(self, text: str) -> Optional[np.ndarray]:
        """Get cached embedding if available"""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.npy"
        
        if cache_file.exists():
            try:
                return np.load(cache_file)
            except Exception as e:
                print(f"Error loading cached embedding: {e}")
                return None
        
        return None
    
    def _cache_embedding(self, text: str, embedding: np.ndarray):
        """Cache an embedding"""
        cache_key = self._get_cache_key(text)
        cache_file = self.cache_dir / f"{cache_key}.npy"
        
        try:
            np.save(cache_file, embedding)
            
            # Also save metadata
            meta_file = self.cache_dir / f"{cache_key}.json"
            metadata = {
                "model": self.model_name,
                "text_length": len(text),
                "cached_at": datetime.utcnow().isoformat(),
                "embedding_dim": len(embedding)
            }
            with open(meta_file, 'w') as f:
                json.dump(metadata, f)
        
        except Exception as e:
            print(f"Error caching embedding: {e}")
    
    def clear_cache(self):
        """Clear embedding cache"""
        import shutil
        
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print(f"✅ Cleared embedding cache: {self.cache_dir}")
    
    def get_cache_stats(self) -> Dict:
        """Get statistics about the cache"""
        if not self.cache_dir.exists():
            return {"cached_embeddings": 0, "cache_size_mb": 0}
        
        npy_files = list(self.cache_dir.glob("*.npy"))
        total_size = sum(f.stat().st_size for f in npy_files)
        
        return {
            "cached_embeddings": len(npy_files),
            "cache_size_mb": round(total_size / (1024 * 1024), 2),
            "cache_dir": str(self.cache_dir)
        }


# Convenience functions
def embed_chunks(chunks: List, use_cache: bool = True, show_progress: bool = False) -> List:
    """
    Embed a list of chunks (from rag_chunker)
    
    Args:
        chunks: List of Chunk objects
        use_cache: Use embedding cache
        show_progress: Show progress bar
    
    Returns:
        Chunks with embeddings added
    """
    embedder = RAGEmbedder()
    
    texts = [chunk.content for chunk in chunks]
    embeddings = embedder.embed_batch(texts, use_cache=use_cache, show_progress=show_progress)
    
    # Add embeddings to chunks
    for chunk, embedding in zip(chunks, embeddings):
        chunk.metadata['embedding'] = embedding
        chunk.metadata['embedding_model'] = embedder.model_name
        chunk.metadata['embedding_dim'] = embedder.embedding_dim
    
    return chunks


def compute_similarity(embedding1: np.ndarray, embedding2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings
    
    Args:
        embedding1: First embedding
        embedding2: Second embedding
    
    Returns:
        Similarity score (0-1)
    """
    if embedding1 is None or embedding2 is None:
        return 0.0
    
    # Cosine similarity
    dot_product = np.dot(embedding1, embedding2)
    norm1 = np.linalg.norm(embedding1)
    norm2 = np.linalg.norm(embedding2)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    similarity = dot_product / (norm1 * norm2)
    
    # Ensure in range [0, 1]
    return float(max(0.0, min(1.0, (similarity + 1) / 2)))


def find_similar_chunks(
    query_embedding: np.ndarray,
    chunk_embeddings: List[np.ndarray],
    top_k: int = 5
) -> List[tuple]:
    """
    Find most similar chunks to a query
    
    Args:
        query_embedding: Query embedding
        chunk_embeddings: List of chunk embeddings
        top_k: Number of top results
    
    Returns:
        List of (index, similarity_score) tuples
    """
    similarities = []
    
    for i, chunk_emb in enumerate(chunk_embeddings):
        if chunk_emb is not None:
            similarity = compute_similarity(query_embedding, chunk_emb)
            similarities.append((i, similarity))
    
    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x[1], reverse=True)
    
    return similarities[:top_k]

