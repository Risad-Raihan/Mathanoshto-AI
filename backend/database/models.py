"""
Database models for storing conversations, messages, and attachments
"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, 
    DateTime, ForeignKey, Boolean, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    """Conversation/Chat session"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"

class Message(Base):
    """Individual message in a conversation"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    
    # Model info
    model = Column(String(100), nullable=True)  # Which model generated this (for assistant messages)
    provider = Column(String(50), nullable=True)  # Which provider (openai, gemini, etc.)
    
    # Token usage
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    finish_reason = Column(String(50), nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    attachments = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', content='{self.content[:30]}...')>"

class Attachment(Base):
    """File attachments (images, PDFs, etc.)"""
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    
    # File info
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'image', 'pdf', 'text'
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_path = Column(String(500), nullable=True)  # Path to stored file
    file_data = Column(LargeBinary, nullable=True)  # Or store inline for small files
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}')>"

class ToolCall(Base):
    """Function/tool calls made during conversation"""
    __tablename__ = 'tool_calls'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    
    # Tool info
    tool_name = Column(String(100), nullable=False)  # e.g., 'tavily_search'
    tool_input = Column(Text, nullable=False)  # JSON string of input arguments
    tool_output = Column(Text, nullable=True)  # JSON string of output
    
    # Status
    status = Column(String(20), default='pending')  # 'pending', 'success', 'error'
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="tool_calls")
    
    def __repr__(self):
        return f"<ToolCall(id={self.id}, tool='{self.tool_name}', status='{self.status}')>"

