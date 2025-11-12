"""
Conversation Insights Database Models
Stores conversation summaries, insights, suggestions, and analytics
"""

from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.database.models import Base


class ConversationSummary(Base):
    """
    Stores multi-level summaries of conversations
    """
    __tablename__ = 'conversation_summaries'
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, unique=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Multi-level summaries
    short_summary = Column(String(500), nullable=True)  # 1-2 sentences
    medium_summary = Column(Text, nullable=True)  # 1 paragraph
    detailed_summary = Column(Text, nullable=True)  # Full summary
    
    # Key information extraction
    key_points = Column(JSON, default=list)  # List of main points
    decisions_made = Column(JSON, default=list)  # List of decisions
    action_items = Column(JSON, default=list)  # List of action items
    questions_asked = Column(JSON, default=list)  # Important questions
    
    # Metadata
    message_count = Column(Integer, default=0)
    generation_method = Column(String(50), default='auto')  # auto, manual
    model_used = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Quality metrics
    confidence_score = Column(Float, default=0.8)  # 0-1
    user_rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Relationships
    conversation = relationship("Conversation", backref="summary")
    user = relationship("User")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'short_summary': self.short_summary,
            'medium_summary': self.medium_summary,
            'detailed_summary': self.detailed_summary,
            'key_points': self.key_points,
            'decisions_made': self.decisions_made,
            'action_items': self.action_items,
            'questions_asked': self.questions_asked,
            'message_count': self.message_count,
            'confidence_score': self.confidence_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class ConversationInsight(Base):
    """
    Stores extracted insights, topics, and entities from conversations
    """
    __tablename__ = 'conversation_insights'
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Topic analysis
    main_topics = Column(JSON, default=list)  # List of main topics with scores
    topic_clusters = Column(JSON, default=dict)  # Grouped topics
    
    # Entity extraction
    entities = Column(JSON, default=dict)  # {type: [entities]} - people, products, places, etc.
    
    # Conversation characteristics
    conversation_type = Column(String(50), nullable=True)  # exploratory, problem-solving, informational, creative
    complexity_level = Column(String(20), nullable=True)  # simple, intermediate, complex
    
    # Knowledge graph
    relationships = Column(JSON, default=list)  # [{from: X, to: Y, relation: Z}]
    
    # Statistics
    total_messages = Column(Integer, default=0)
    user_messages = Column(Integer, default=0)
    assistant_messages = Column(Integer, default=0)
    avg_message_length = Column(Float, default=0.0)
    
    # Time tracking
    conversation_duration_minutes = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", backref="insights")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_insight_user_conversation', 'user_id', 'conversation_id'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'main_topics': self.main_topics,
            'topic_clusters': self.topic_clusters,
            'entities': self.entities,
            'conversation_type': self.conversation_type,
            'complexity_level': self.complexity_level,
            'relationships': self.relationships,
            'total_messages': self.total_messages,
            'user_messages': self.user_messages,
            'assistant_messages': self.assistant_messages,
            'avg_message_length': self.avg_message_length,
            'conversation_duration_minutes': self.conversation_duration_minutes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConversationSuggestion(Base):
    """
    Stores conversation continuation suggestions and smart prompts
    """
    __tablename__ = 'conversation_suggestions'
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Suggestion details
    suggestion_type = Column(String(50), nullable=False, index=True)  # continuation, prompt, followup
    suggestion_text = Column(Text, nullable=False)
    suggestion_category = Column(String(100), nullable=True)  # clarification, expansion, related, deep-dive
    
    # Context
    context_messages = Column(JSON, default=list)  # IDs of messages used for context
    relevance_score = Column(Float, default=0.5)  # 0-1
    
    # Ranking and priority
    rank = Column(Integer, default=0)
    priority = Column(String(20), default='medium')  # low, medium, high
    
    # Usage tracking
    was_used = Column(Boolean, default=False)
    used_at = Column(DateTime, nullable=True)
    user_feedback = Column(String(20), nullable=True)  # helpful, not_helpful, ignore
    
    # Metadata
    generation_reason = Column(Text, nullable=True)  # Why this suggestion was generated
    model_used = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    expires_at = Column(DateTime, nullable=True)  # Suggestions can expire
    
    # Relationships
    conversation = relationship("Conversation")
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_suggestion_user_type', 'user_id', 'suggestion_type'),
        Index('idx_suggestion_conversation_active', 'conversation_id', 'was_used'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'suggestion_type': self.suggestion_type,
            'suggestion_text': self.suggestion_text,
            'suggestion_category': self.suggestion_category,
            'relevance_score': self.relevance_score,
            'rank': self.rank,
            'priority': self.priority,
            'was_used': self.was_used,
            'generation_reason': self.generation_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class ConversationExport(Base):
    """
    Stores conversation export metadata and templates
    """
    __tablename__ = 'conversation_exports'
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Export details
    export_format = Column(String(20), nullable=False)  # markdown, pdf, json, html
    template_type = Column(String(50), default='standard')  # standard, business, technical, meeting_notes
    
    # Content
    executive_summary = Column(Text, nullable=True)
    structured_content = Column(JSON, default=dict)  # Organized sections
    citations = Column(JSON, default=list)  # Message references
    
    # File information
    file_path = Column(String(500), nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    
    # Export settings
    include_timestamps = Column(Boolean, default=True)
    include_metadata = Column(Boolean, default=True)
    include_citations = Column(Boolean, default=True)
    privacy_mode = Column(Boolean, default=False)  # Redact sensitive info
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    accessed_at = Column(DateTime, nullable=True)  # Last download
    
    # Relationships
    conversation = relationship("Conversation")
    user = relationship("User")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'export_format': self.export_format,
            'template_type': self.template_type,
            'executive_summary': self.executive_summary,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'include_timestamps': self.include_timestamps,
            'include_metadata': self.include_metadata,
            'privacy_mode': self.privacy_mode,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class UserPromptLibrary(Base):
    """
    Stores user's custom prompts and successful prompt patterns
    """
    __tablename__ = 'user_prompt_library'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Prompt details
    prompt_text = Column(Text, nullable=False)
    prompt_title = Column(String(200), nullable=True)
    prompt_category = Column(String(100), nullable=True)
    
    # Context
    tags = Column(JSON, default=list)
    agent_type = Column(String(100), nullable=True)  # Which agent this works well with
    complexity_level = Column(String(20), default='intermediate')
    
    # Usage statistics
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)  # 0-1 based on user feedback
    last_used = Column(DateTime, nullable=True)
    
    # Source
    is_custom = Column(Boolean, default=True)  # User created vs auto-generated
    source_conversation_id = Column(Integer, ForeignKey('conversations.id', ondelete='SET NULL'), nullable=True)
    
    # Metadata
    is_favorite = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)  # Share with community
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    
    # Indexes
    __table_args__ = (
        Index('idx_prompt_user_category', 'user_id', 'prompt_category'),
        Index('idx_prompt_user_favorite', 'user_id', 'is_favorite'),
    )
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'prompt_text': self.prompt_text,
            'prompt_title': self.prompt_title,
            'prompt_category': self.prompt_category,
            'tags': self.tags,
            'agent_type': self.agent_type,
            'complexity_level': self.complexity_level,
            'usage_count': self.usage_count,
            'success_rate': self.success_rate,
            'is_favorite': self.is_favorite,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

