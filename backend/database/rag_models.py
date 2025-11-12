"""
RAG Database Models
Stores document chunks, embeddings, citations, and retrieval metrics
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, List, Optional
from backend.database.models import Base


class DocumentChunk(Base):
    """
    Stores document chunks with embeddings
    """
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Chunk content
    content = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False)  # Order in document
    total_chunks = Column(Integer, nullable=False)  # Total chunks in document
    
    # Position in original document
    start_char = Column(Integer, nullable=False)
    end_char = Column(Integer, nullable=False)
    
    # Chunk metadata
    chunk_size = Column(Integer, nullable=False)  # Character count
    token_count = Column(Integer, nullable=True)  # Estimated token count
    strategy = Column(String(50), nullable=False)  # Chunking strategy used
    
    # Content metadata
    header = Column(String(500), nullable=True)  # Section header if available
    page_number = Column(Integer, nullable=True)  # Page number if available
    chunk_type = Column(String(50), nullable=True)  # paragraph, code, table, etc.
    language = Column(String(50), nullable=True)  # Programming language for code
    
    # Embedding
    embedding = Column(LargeBinary, nullable=True)  # Stored as bytes (numpy array)
    embedding_model = Column(String(100), nullable=True)
    embedding_dim = Column(Integer, nullable=True)
    
    # Quality metrics
    importance_score = Column(Float, default=0.5)  # How important is this chunk
    relevance_score = Column(Float, default=0.0)  # Relevance to query (updated on retrieval)
    retrieval_count = Column(Integer, default=0)  # How many times retrieved
    
    # Additional metadata (JSON)
    meta_data = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    file = relationship("File", backref="chunks")
    user = relationship("User")
    citations = relationship("ChunkCitation", back_populates="chunk", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "file_id": self.file_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
            "start_char": self.start_char,
            "end_char": self.end_char,
            "chunk_size": self.chunk_size,
            "token_count": self.token_count,
            "strategy": self.strategy,
            "header": self.header,
            "page_number": self.page_number,
            "chunk_type": self.chunk_type,
            "importance_score": self.importance_score,
            "relevance_score": self.relevance_score,
            "retrieval_count": self.retrieval_count,
            "embedding_model": self.embedding_model,
            "embedding_dim": self.embedding_dim,
            "meta_data": self.meta_data,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class ChunkCitation(Base):
    """
    Tracks which chunks were used in generating responses
    Citations link chunks to messages for traceability
    """
    __tablename__ = "chunk_citations"
    
    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(Integer, ForeignKey("document_chunks.id"), nullable=False, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Citation details
    relevance_score = Column(Float, nullable=False)  # How relevant was this chunk
    rank = Column(Integer, nullable=False)  # Ranking in retrieval results
    was_used = Column(Boolean, default=True)  # Was it actually used in the response
    
    # Context
    query = Column(Text, nullable=False)  # The query that retrieved this chunk
    retrieval_method = Column(String(50), nullable=False)  # semantic, keyword, hybrid
    
    # Citation format
    citation_text = Column(String(500), nullable=True)  # "[Doc1, p.5]"
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    chunk = relationship("DocumentChunk", back_populates="citations")
    message = relationship("Message", backref="chunk_citations")
    conversation = relationship("Conversation")
    user = relationship("User")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "chunk_id": self.chunk_id,
            "message_id": self.message_id,
            "relevance_score": self.relevance_score,
            "rank": self.rank,
            "was_used": self.was_used,
            "query": self.query,
            "retrieval_method": self.retrieval_method,
            "citation_text": self.citation_text,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class RAGConfiguration(Base):
    """
    Stores user's RAG configuration preferences
    """
    __tablename__ = "rag_configurations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # RAG settings
    is_enabled = Column(Boolean, default=True)
    chunk_size = Column(Integer, default=1000)
    chunk_overlap = Column(Integer, default=200)
    chunking_strategy = Column(String(50), default="recursive")
    
    # Retrieval settings
    top_k = Column(Integer, default=5)  # Number of chunks to retrieve
    min_similarity = Column(Float, default=0.5)  # Minimum similarity threshold
    retrieval_mode = Column(String(50), default="hybrid")  # semantic, keyword, hybrid
    
    # Hybrid search weights
    semantic_weight = Column(Float, default=0.7)
    keyword_weight = Column(Float, default=0.3)
    
    # Re-ranking
    use_reranking = Column(Boolean, default=True)
    reranking_model = Column(String(100), default="cross-encoder")
    
    # Citations
    show_citations = Column(Boolean, default=True)
    citation_format = Column(String(50), default="inline")  # inline, footer, numbered
    
    # Context optimization
    use_compression = Column(Boolean, default=False)
    use_query_expansion = Column(Boolean, default=False)
    use_mmr = Column(Boolean, default=True)  # Maximum Marginal Relevance
    mmr_lambda = Column(Float, default=0.5)  # Diversity vs relevance trade-off
    
    # File filtering
    selected_file_ids = Column(JSON, default=list)  # Empty = all files
    excluded_file_ids = Column(JSON, default=list)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="rag_config")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "is_enabled": self.is_enabled,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "chunking_strategy": self.chunking_strategy,
            "top_k": self.top_k,
            "min_similarity": self.min_similarity,
            "retrieval_mode": self.retrieval_mode,
            "semantic_weight": self.semantic_weight,
            "keyword_weight": self.keyword_weight,
            "use_reranking": self.use_reranking,
            "show_citations": self.show_citations,
            "citation_format": self.citation_format,
            "use_compression": self.use_compression,
            "use_query_expansion": self.use_query_expansion,
            "use_mmr": self.use_mmr,
            "mmr_lambda": self.mmr_lambda,
            "selected_file_ids": self.selected_file_ids,
            "excluded_file_ids": self.excluded_file_ids
        }


class RAGMetrics(Base):
    """
    Tracks RAG system performance metrics
    """
    __tablename__ = "rag_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True, index=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    
    # Query info
    query = Column(Text, nullable=False)
    query_length = Column(Integer, nullable=False)
    
    # Retrieval metrics
    chunks_retrieved = Column(Integer, nullable=False)
    retrieval_time_ms = Column(Integer, nullable=False)
    retrieval_method = Column(String(50), nullable=False)
    
    # Quality metrics
    avg_relevance_score = Column(Float, nullable=True)
    max_relevance_score = Column(Float, nullable=True)
    min_relevance_score = Column(Float, nullable=True)
    
    # Coverage
    files_covered = Column(Integer, nullable=True)  # How many files contributed chunks
    unique_chunks = Column(Integer, nullable=True)
    
    # Generation metrics
    generation_time_ms = Column(Integer, nullable=True)
    total_tokens = Column(Integer, nullable=True)
    citations_generated = Column(Integer, nullable=True)
    
    # User feedback
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    was_helpful = Column(Boolean, nullable=True)
    feedback_text = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User")
    conversation = relationship("Conversation")
    message = relationship("Message")
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "query": self.query,
            "chunks_retrieved": self.chunks_retrieved,
            "retrieval_time_ms": self.retrieval_time_ms,
            "retrieval_method": self.retrieval_method,
            "avg_relevance_score": self.avg_relevance_score,
            "files_covered": self.files_covered,
            "generation_time_ms": self.generation_time_ms,
            "citations_generated": self.citations_generated,
            "user_rating": self.user_rating,
            "was_helpful": self.was_helpful,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

