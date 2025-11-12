"""
Agent Models for Custom Personas System
Allows users to interact with specialized AI agents for different tasks
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from typing import Dict, List, Optional
from backend.database.models import Base


class Agent(Base):
    """
    Agent model - represents a specialized AI persona/agent
    """
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    emoji = Column(String(10), default="🤖")
    description = Column(Text, nullable=False)
    system_prompt = Column(Text, nullable=False)
    
    # Agent settings
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=2000)
    top_p = Column(Float, default=1.0)
    
    # Agent characteristics
    tone = Column(String(50), default="professional")  # professional, casual, technical, creative, etc.
    expertise_level = Column(String(50), default="expert")  # beginner, intermediate, expert
    response_format = Column(String(50), default="markdown")  # markdown, code, diagram, etc.
    
    # Tool permissions (JSON array of tool names)
    allowed_tools = Column(JSON, default=list)  # e.g., ["web_search", "code_execution", "diagram_generator"]
    
    # Metadata
    category = Column(String(50), nullable=False, index=True)  # research, development, product, data, documentation, etc.
    tags = Column(JSON, default=list)  # searchable tags
    
    # Versioning and tracking
    version = Column(String(20), default="1.0")
    is_system = Column(Boolean, default=False)  # System-provided vs user-created
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)  # Can be shared in marketplace
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # User relationship (if custom agent)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator = relationship("User", back_populates="custom_agents")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    versions = relationship("AgentVersion", back_populates="agent", cascade="all, delete-orphan")
    sessions = relationship("AgentSession", back_populates="agent", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict:
        """Convert agent to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "emoji": self.emoji,
            "description": self.description,
            "system_prompt": self.system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "tone": self.tone,
            "expertise_level": self.expertise_level,
            "response_format": self.response_format,
            "allowed_tools": self.allowed_tools or [],
            "category": self.category,
            "tags": self.tags or [],
            "version": self.version,
            "is_system": self.is_system,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "usage_count": self.usage_count,
            "rating": self.rating,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class AgentVersion(Base):
    """
    Agent version tracking - keep history of agent changes
    """
    __tablename__ = "agent_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    version = Column(String(20), nullable=False)
    
    # Snapshot of agent at this version
    system_prompt = Column(Text, nullable=False)
    settings = Column(JSON, nullable=False)  # temperature, max_tokens, etc.
    
    # Change tracking
    change_summary = Column(Text)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="versions")
    
    def to_dict(self) -> Dict:
        """Convert version to dictionary"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "version": self.version,
            "system_prompt": self.system_prompt,
            "settings": self.settings,
            "change_summary": self.change_summary,
            "changed_by": self.changed_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class AgentSession(Base):
    """
    Track which agent is used in which conversation
    """
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Session tracking
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)
    message_count = Column(Integer, default=0)
    
    # Feedback
    rating = Column(Integer, nullable=True)  # 1-5
    feedback = Column(Text, nullable=True)
    
    # Relationships
    agent = relationship("Agent", back_populates="sessions")
    conversation = relationship("Conversation", back_populates="agent_sessions")
    user = relationship("User")
    
    def to_dict(self) -> Dict:
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "message_count": self.message_count,
            "rating": self.rating,
            "feedback": self.feedback
        }

