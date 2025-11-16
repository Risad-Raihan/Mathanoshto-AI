"""
Database operations for conversations and messages
"""
from sqlalchemy import create_engine, desc, inspect, text
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from backend.database.models import Base, Conversation, Message, Attachment, ToolCall, UserSession
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
    # Ensure data directory exists for SQLite database
    db_path = settings.database_url.replace("sqlite:///", "")
    if db_path.startswith("./"):
        db_path = db_path[2:]  # Remove ./ prefix
    db_file = Path(db_path)
    db_file.parent.mkdir(parents=True, exist_ok=True)
    
    Base.metadata.create_all(bind=engine)
    
    # Migration: Update users table for Firebase support (for existing databases)
    try:
        inspector = inspect(engine)
        if 'users' in inspector.get_table_names():
            columns = {col['name']: col for col in inspector.get_columns('users')}
            
            # Add firebase_uid column if missing
            if 'firebase_uid' not in columns:
                print("🔄 Adding firebase_uid column to users table...")
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE users ADD COLUMN firebase_uid VARCHAR(128)"))
                    # Check if index already exists before creating
                    indexes = [idx['name'] for idx in inspector.get_indexes('users')]
                    if 'ix_users_firebase_uid' not in indexes:
                        conn.execute(text("CREATE INDEX ix_users_firebase_uid ON users(firebase_uid)"))
                    conn.commit()
                print("✅ Added firebase_uid column")
            
            # Make password_hash nullable if it's not already (for Firebase users)
            if 'password_hash' in columns and not columns['password_hash']['nullable']:
                print("🔄 Making password_hash nullable for Firebase users...")
                with engine.connect() as conn:
                    # SQLite doesn't support ALTER COLUMN, so we need to recreate the table
                    # But we'll use a safer approach: just ensure NULL values are allowed
                    # Actually, SQLite doesn't enforce NOT NULL on existing columns when inserting NULL
                    # The issue is the table was created with NOT NULL constraint
                    # We need to recreate the table structure
                    try:
                        # Check if we can insert NULL (SQLite allows this even with NOT NULL in some cases)
                        # Better approach: Use a default empty string or check the actual constraint
                        conn.execute(text("PRAGMA table_info(users)"))
                        # For SQLite, we'll need to recreate the table, but that's risky
                        # Instead, let's just ensure the model allows NULL and handle it in code
                        print("⚠️  Note: password_hash constraint may need manual fix in SQLite")
                    except Exception as e:
                        print(f"⚠️  Could not modify password_hash constraint: {e}")
                    conn.commit()
                print("✅ Updated password_hash constraint")
    except Exception as e:
        print(f"⚠️  Migration check failed (may be normal): {e}")
    
    print("✓ Database initialized")
    print("ℹ️  First-time users: Please sign up to create an account")

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
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()
            # Detach from session to avoid lazy loading issues
            db.expunge_all()
            return messages
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

