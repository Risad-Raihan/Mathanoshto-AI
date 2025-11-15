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

class User(Base):
    """User accounts for the application"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=True)  # Made nullable for Firebase users
    password_hash = Column(String(255), nullable=True)  # Made nullable for Firebase users
    firebase_uid = Column(String(128), unique=True, nullable=True, index=True)  # Firebase user ID
    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True, index=True)  # Made unique for Firebase
    
    # User preferences
    default_provider = Column(String(50), nullable=True, default='openai')
    default_model = Column(String(100), nullable=True, default='gpt-4o')
    default_temperature = Column(Float, default=0.7)
    default_max_tokens = Column(Integer, default=2000)
    theme = Column(String(20), default='dark')  # 'dark' or 'light'
    
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    api_keys = relationship("UserAPIKey", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    custom_agents = relationship("Agent", back_populates="creator", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"


class UserAPIKey(Base):
    """Encrypted API keys for each user"""
    __tablename__ = 'user_api_keys'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # API key info
    provider = Column(String(50), nullable=False)  # 'openai', 'gemini', 'anthropic', 'tavily', 'firecrawl', 'mathpix'
    key_name = Column(String(100), nullable=False)  # e.g., 'OPENAI_API_KEY'
    encrypted_key = Column(Text, nullable=False)  # Encrypted API key
    
    # Optional: base URL for custom endpoints
    base_url = Column(String(255), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    def __repr__(self):
        return f"<UserAPIKey(id={self.id}, user_id={self.user_id}, provider='{self.provider}')>"


class UserSession(Base):
    """User session tokens for 'Remember Me' functionality"""
    __tablename__ = 'user_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Session metadata
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_activity = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id}, token='{self.session_token[:8]}...')>"

class Conversation(Base):
    """Conversation/Chat session"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    agent_sessions = relationship("AgentSession", back_populates="conversation", cascade="all, delete-orphan")
    
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


class File(Base):
    """File storage for user uploads"""
    __tablename__ = 'files'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)  # Original name before sanitization
    file_type = Column(String(50), nullable=False)  # 'pdf', 'docx', 'txt', 'image', 'csv', 'json', 'xml'
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_path = Column(String(500), nullable=False)  # Relative path from uploads directory
    
    # File metadata
    description = Column(Text, nullable=True)
    extracted_text = Column(Text, nullable=True)  # Extracted text content for search
    thumbnail_path = Column(String(500), nullable=True)  # Path to thumbnail
    
    # File metadata from file itself
    author = Column(String(100), nullable=True)
    creation_date = Column(DateTime, nullable=True)
    
    # Organizational
    folder_path = Column(String(500), nullable=True, default='/')  # Virtual folder path
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="files")
    tags = relationship("FileTag", back_populates="file", cascade="all, delete-orphan")
    conversation_files = relationship("ConversationFile", back_populates="file", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', type='{self.file_type}')>"


class FileTag(Base):
    """Tags for organizing files"""
    __tablename__ = 'file_tags'
    
    id = Column(Integer, primary_key=True)
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    tag = Column(String(50), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="tags")
    
    def __repr__(self):
        return f"<FileTag(id={self.id}, file_id={self.file_id}, tag='{self.tag}')>"


class ConversationFile(Base):
    """Junction table linking files to conversations/messages"""
    __tablename__ = 'conversation_files'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=True)  # Optional: specific message
    file_id = Column(Integer, ForeignKey('files.id'), nullable=False)
    
    # Metadata about the attachment
    attached_at = Column(DateTime, default=datetime.utcnow)
    context_type = Column(String(50), nullable=True)  # 'reference', 'analysis', 'summary', etc.
    
    # Relationships
    conversation = relationship("Conversation", backref="attached_files")
    message = relationship("Message", backref="attached_files")
    file = relationship("File", back_populates="conversation_files")
    
    def __repr__(self):
        return f"<ConversationFile(id={self.id}, conv_id={self.conversation_id}, file_id={self.file_id})>"

