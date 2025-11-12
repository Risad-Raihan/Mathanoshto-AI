"""
Database operations for the Memory system
Provides high-level database operations for memories
"""
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from backend.database.memory_models import (
    Memory, MemoryVersion, MemoryRelationship, MemoryAccess
)


class MemoryDB:
    """Database operations for memories"""
    
    @staticmethod
    def create_memory(
        db: Session,
        user_id: int,
        content: str,
        memory_type: str,
        **kwargs
    ) -> Memory:
        """Create a new memory"""
        memory = Memory(
            user_id=user_id,
            content=content,
            memory_type=memory_type,
            **kwargs
        )
        db.add(memory)
        db.commit()
        db.refresh(memory)
        return memory
    
    @staticmethod
    def get_memory(db: Session, memory_id: int) -> Optional[Memory]:
        """Get memory by ID"""
        return db.query(Memory).filter(Memory.id == memory_id).first()
    
    @staticmethod
    def get_user_memories(
        db: Session,
        user_id: int,
        memory_types: Optional[List[str]] = None,
        is_active: bool = True,
        limit: int = 100,
        offset: int = 0
    ) -> List[Memory]:
        """Get all memories for a user"""
        query = db.query(Memory).filter(Memory.user_id == user_id)
        
        if is_active:
            query = query.filter(Memory.is_active == True)
        
        if memory_types:
            query = query.filter(Memory.memory_type.in_(memory_types))
        
        return query.order_by(Memory.importance_score.desc()).limit(limit).offset(offset).all()
    
    @staticmethod
    def search_by_tags(
        db: Session,
        user_id: int,
        tags: List[str],
        match_all: bool = False
    ) -> List[Memory]:
        """Search memories by tags"""
        query = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        )
        
        if match_all:
            # All tags must match
            for tag in tags:
                query = query.filter(Memory.tags.contains([tag]))
        else:
            # Any tag matches (PostgreSQL specific)
            # For SQLite, we need a different approach
            memories = query.all()
            result = []
            for memory in memories:
                if any(tag in memory.tags for tag in tags):
                    result.append(memory)
            return result
        
        return query.all()
    
    @staticmethod
    def get_memories_by_category(
        db: Session,
        user_id: int,
        category: str
    ) -> List[Memory]:
        """Get memories by category"""
        return db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.category == category,
            Memory.is_active == True
        ).order_by(Memory.importance_score.desc()).all()
    
    @staticmethod
    def update_memory(
        db: Session,
        memory_id: int,
        **updates
    ) -> Optional[Memory]:
        """Update a memory"""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not memory:
            return None
        
        for key, value in updates.items():
            if hasattr(memory, key):
                setattr(memory, key, value)
        
        memory.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(memory)
        return memory
    
    @staticmethod
    def delete_memory(
        db: Session,
        memory_id: int,
        soft_delete: bool = True
    ) -> bool:
        """Delete a memory"""
        memory = db.query(Memory).filter(Memory.id == memory_id).first()
        if not memory:
            return False
        
        if soft_delete:
            memory.is_active = False
            memory.updated_at = datetime.utcnow()
            db.commit()
        else:
            db.delete(memory)
            db.commit()
        
        return True
    
    @staticmethod
    def get_memory_stats(db: Session, user_id: int) -> Dict:
        """Get memory statistics for a user"""
        total = db.query(func.count(Memory.id)).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).scalar()
        
        by_type = db.query(
            Memory.memory_type,
            func.count(Memory.id)
        ).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).group_by(Memory.memory_type).all()
        
        pinned = db.query(func.count(Memory.id)).filter(
            Memory.user_id == user_id,
            Memory.is_active == True,
            Memory.is_pinned == True
        ).scalar()
        
        verified = db.query(func.count(Memory.id)).filter(
            Memory.user_id == user_id,
            Memory.is_active == True,
            Memory.is_verified == True
        ).scalar()
        
        # Average importance
        avg_importance = db.query(func.avg(Memory.importance_score)).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).scalar() or 0
        
        # Most accessed
        most_accessed = db.query(Memory).filter(
            Memory.user_id == user_id,
            Memory.is_active == True
        ).order_by(Memory.access_count.desc()).limit(5).all()
        
        return {
            'total_memories': total,
            'by_type': dict(by_type),
            'pinned_count': pinned,
            'verified_count': verified,
            'average_importance': round(avg_importance, 2),
            'most_accessed': [m.to_dict() for m in most_accessed]
        }
    
    @staticmethod
    def log_memory_access(
        db: Session,
        memory_id: int,
        user_id: int,
        access_type: str,
        context: Optional[str] = None,
        relevance_score: Optional[float] = None
    ):
        """Log memory access for analytics"""
        access_log = MemoryAccess(
            memory_id=memory_id,
            user_id=user_id,
            access_type=access_type,
            context=context,
            relevance_score=relevance_score
        )
        db.add(access_log)
        db.commit()


class MemoryRelationshipDB:
    """Database operations for memory relationships"""
    
    @staticmethod
    def create_relationship(
        db: Session,
        from_memory_id: int,
        to_memory_id: int,
        relationship_type: str,
        strength: float = 1.0
    ) -> MemoryRelationship:
        """Create a relationship between memories"""
        relationship = MemoryRelationship(
            from_memory_id=from_memory_id,
            to_memory_id=to_memory_id,
            relationship_type=relationship_type,
            strength=strength
        )
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        return relationship
    
    @staticmethod
    def get_related_memories(
        db: Session,
        memory_id: int,
        relationship_types: Optional[List[str]] = None
    ) -> List[Tuple[Memory, str, float]]:
        """Get memories related to a given memory"""
        query = db.query(
            Memory,
            MemoryRelationship.relationship_type,
            MemoryRelationship.strength
        ).join(
            MemoryRelationship,
            MemoryRelationship.to_memory_id == Memory.id
        ).filter(
            MemoryRelationship.from_memory_id == memory_id
        )
        
        if relationship_types:
            query = query.filter(
                MemoryRelationship.relationship_type.in_(relationship_types)
            )
        
        return query.all()
    
    @staticmethod
    def find_conflicting_memories(
        db: Session,
        memory_id: int
    ) -> List[Memory]:
        """Find memories that conflict with a given memory"""
        return db.query(Memory).join(
            MemoryRelationship,
            MemoryRelationship.to_memory_id == Memory.id
        ).filter(
            MemoryRelationship.from_memory_id == memory_id,
            MemoryRelationship.relationship_type == 'contradicts'
        ).all()


# Initialize database tables
def init_memory_tables():
    """Initialize memory tables in database"""
    from backend.database.operations import engine
    from backend.database.memory_models import Base
    
    # Import all models to ensure they're registered
    from backend.database.memory_models import (
        Memory, MemoryVersion, MemoryRelationship, MemoryAccess
    )
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✅ Memory tables initialized")

