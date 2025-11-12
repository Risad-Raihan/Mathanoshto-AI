"""
Database operations for conversations and messages
"""
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime

from backend.database.models import Base, Conversation, Message, Attachment, ToolCall
from backend.config.settings import settings

# Import all models to ensure they're registered with SQLAlchemy
try:
    from backend.database.memory_models import Memory, MemoryVersion, MemoryRelationship, MemoryAccess
except ImportError:
    pass  # Memory system may not be set up yet

try:
    from backend.database.agent_models import Agent, AgentVersion, AgentSession
except ImportError:
    pass  # Agent system may not be set up yet

try:
    from backend.database.rag_models import DocumentChunk, ChunkCitation, RAGConfiguration, RAGMetrics
except ImportError:
    pass  # RAG system may not be set up yet

try:
    from backend.database.conversation_insights_models import (
        ConversationSummary, ConversationInsight, ConversationSuggestion,
        ConversationExport, UserPromptLibrary
    )
except ImportError:
    pass  # Insights system may not be set up yet

# Create engine and session
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller manage

class ConversationDB:
    """Database operations for conversations"""
    
    @staticmethod
    def create_conversation(user_id: int, title: str = "New Conversation") -> Conversation:
        """Create a new conversation for a user"""
        db = get_db()
        try:
            conversation = Conversation(user_id=user_id, title=title)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        finally:
            db.close()
    
    @staticmethod
    def get_conversation(conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID"""
        db = get_db()
        try:
            return db.query(Conversation).filter(Conversation.id == conversation_id).first()
        finally:
            db.close()
    
    @staticmethod
    def list_conversations(user_id: int, limit: int = 50, include_archived: bool = False) -> List[Conversation]:
        """List all conversations for a user"""
        db = get_db()
        try:
            from sqlalchemy.orm import joinedload
            query = db.query(Conversation).options(joinedload(Conversation.messages))
            query = query.filter(Conversation.user_id == user_id)
            if not include_archived:
                query = query.filter(Conversation.is_archived == False)
            conversations = query.order_by(desc(Conversation.updated_at)).limit(limit).all()
            # Detach from session to avoid lazy loading issues
            db.expunge_all()
            return conversations
        finally:
            db.close()
    
    @staticmethod
    def update_conversation_title(conversation_id: int, title: str):
        """Update conversation title"""
        db = get_db()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def archive_conversation(conversation_id: int):
        """Archive a conversation"""
        db = get_db()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.is_archived = True
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def delete_conversation(conversation_id: int):
        """Permanently delete a conversation"""
        db = get_db()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                db.delete(conversation)
                db.commit()
        finally:
            db.close()

class MessageDB:
    """Database operations for messages"""
    
    @staticmethod
    def add_message(
        conversation_id: int,
        role: str,
        content: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        finish_reason: Optional[str] = None
    ) -> Message:
        """Add a message to a conversation"""
        db = get_db()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost=cost,
                finish_reason=finish_reason
            )
            db.add(message)
            
            # Update conversation timestamp
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            return message
        finally:
            db.close()
    
    @staticmethod
    def get_messages(conversation_id: int) -> List[Message]:
        """Get all messages in a conversation"""
        db = get_db()
        try:
            return db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()
        finally:
            db.close()
    
    @staticmethod
    def get_message_count(conversation_id: int) -> int:
        """Get count of messages in a conversation"""
        db = get_db()
        try:
            return db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).count()
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_tokens(conversation_id: int) -> dict:
        """Get total token usage for a conversation"""
        db = get_db()
        try:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).all()
            
            total_input = sum(m.input_tokens for m in messages)
            total_output = sum(m.output_tokens for m in messages)
            total_cost = sum(m.cost for m in messages)
            
            return {
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "total_cost": total_cost
            }
        finally:
            db.close()

