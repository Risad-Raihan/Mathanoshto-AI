"""
Memory System Database Models
Implements long-term context memory with embeddings and semantic search
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.models import Base


class Memory(Base):
    """
    Memory storage with embeddings for semantic search
    Stores important facts, preferences, and context from conversations
    """
    __tablename__ = 'memories'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Memory content
    content = Column(Text, nullable=False)  # The actual memory text
    summary = Column(Text)  # Optional condensed version for old memories
    
    # Memory classification
    memory_type = Column(String(50), nullable=False, index=True)
    # Types: 'personal_info', 'preference', 'fact', 'task', 'goal', 'conversation_summary', 'skill', 'relationship'
    
    category = Column(String(100))  # Subcategory for organization
    tags = Column(JSON, default=list)  # List of tags for filtering
    
    # Vector embedding (stored as JSON array)
    embedding = Column(JSON)  # Vector embedding for semantic search
    embedding_model = Column(String(100))  # Model used for embedding
    
    # Importance and relevance
    importance_score = Column(Float, default=0.5)  # 0-1, higher = more important
    access_count = Column(Integer, default=0)  # How many times retrieved
    last_accessed = Column(DateTime)  # Last retrieval time
    
    # Source tracking
    source_type = Column(String(50))  # 'conversation', 'manual', 'imported', 'inferred'
    source_id = Column(String(255))  # Reference to conversation_id or message_id
    confidence = Column(Float, default=1.0)  # Confidence in the memory (0-1)
    
    # Memory lifecycle
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)  # Optional expiration
    is_active = Column(Boolean, default=True, index=True)  # Soft delete
    
    # Privacy and control
    privacy_level = Column(String(20), default='private')  # 'private', 'shared', 'public'
    is_verified = Column(Boolean, default=False)  # User has confirmed this memory
    is_pinned = Column(Boolean, default=False)  # Always include in context
    
    # Metadata
    meta_data = Column(JSON, default=dict)  # Additional flexible data
    # Can store: location, entities, dates, emotions, related_memories, etc.
    
    # Relationships
    user = relationship("User", back_populates="memories")
    versions = relationship("MemoryVersion", back_populates="memory", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_user_type', 'user_id', 'memory_type'),
        Index('idx_user_active', 'user_id', 'is_active'),
        Index('idx_importance', 'importance_score'),
        Index('idx_created', 'created_at'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'content': self.content,
            'summary': self.summary,
            'memory_type': self.memory_type,
            'category': self.category,
            'tags': self.tags,
            'importance_score': self.importance_score,
            'access_count': self.access_count,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'source_type': self.source_type,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_verified': self.is_verified,
            'is_pinned': self.is_pinned,
            'meta_data': self.meta_data
        }


class MemoryVersion(Base):
    """
    Version history for memories
    Tracks changes over time
    """
    __tablename__ = 'memory_versions'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey('memories.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Version data
    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    change_reason = Column(String(255))  # Why was it changed
    changed_by = Column(String(50))  # 'user', 'system', 'ai'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    memory = relationship("Memory", back_populates="versions")


class MemoryRelationship(Base):
    """
    Relationships between memories
    Allows building knowledge graphs
    """
    __tablename__ = 'memory_relationships'
    
    id = Column(Integer, primary_key=True)
    from_memory_id = Column(Integer, ForeignKey('memories.id', ondelete='CASCADE'), nullable=False)
    to_memory_id = Column(Integer, ForeignKey('memories.id', ondelete='CASCADE'), nullable=False)
    
    relationship_type = Column(String(50), nullable=False)
    # Types: 'related_to', 'contradicts', 'supports', 'supersedes', 'derived_from', 'part_of'
    
    strength = Column(Float, default=1.0)  # Strength of relationship (0-1)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_from_memory', 'from_memory_id'),
        Index('idx_to_memory', 'to_memory_id'),
    )


class MemoryAccess(Base):
    """
    Track when memories are accessed for analytics
    """
    __tablename__ = 'memory_access_log'
    
    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey('memories.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    
    access_type = Column(String(50))  # 'retrieval', 'injection', 'view', 'edit'
    context = Column(String(255))  # What triggered the access
    relevance_score = Column(Float)  # How relevant was it to the query
    
    accessed_at = Column(DateTime, default=datetime.utcnow, index=True)


# Update User model to include memory relationship
# This should be added to backend/database/models.py
"""
Add to User class in models.py:
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
"""

