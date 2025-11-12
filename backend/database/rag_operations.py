"""
RAG Database Operations
CRUD operations for RAG system
"""

from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.database.rag_models import (
    DocumentChunk, ChunkCitation, RAGConfiguration, RAGMetrics
)


class RAGOperations:
    """Database operations for RAG"""
    
    @staticmethod
    def get_user_config(db: Session, user_id: int) -> Optional[RAGConfiguration]:
        """Get user RAG configuration"""
        return db.query(RAGConfiguration).filter(
            RAGConfiguration.user_id == user_id
        ).first()
    
    @staticmethod
    def update_config(
        db: Session,
        user_id: int,
        **updates
    ) -> Optional[RAGConfiguration]:
        """Update user RAG configuration"""
        config = RAGOperations.get_user_config(db, user_id)
        
        if not config:
            return None
        
        for key, value in updates.items():
            if hasattr(config, key):
                setattr(config, key, value)
        
        db.commit()
        db.refresh(config)
        return config
    
    @staticmethod
    def get_file_chunks(
        db: Session,
        file_id: int,
        user_id: int
    ) -> List[DocumentChunk]:
        """Get all chunks for a file"""
        return db.query(DocumentChunk).filter(
            DocumentChunk.file_id == file_id,
            DocumentChunk.user_id == user_id
        ).order_by(DocumentChunk.chunk_index).all()
    
    @staticmethod
    def get_chunk_count(db: Session, user_id: int) -> int:
        """Get total chunks for user"""
        return db.query(DocumentChunk).filter(
            DocumentChunk.user_id == user_id
        ).count()
    
    @staticmethod
    def get_processed_files(db: Session, user_id: int) -> List[Dict]:
        """Get list of processed files with chunk counts"""
        results = db.query(
            DocumentChunk.file_id,
            func.count(DocumentChunk.id).label('chunk_count'),
            func.max(DocumentChunk.created_at).label('processed_at')
        ).filter(
            DocumentChunk.user_id == user_id
        ).group_by(DocumentChunk.file_id).all()
        
        return [
            {
                "file_id": r.file_id,
                "chunk_count": r.chunk_count,
                "processed_at": r.processed_at
            }
            for r in results
        ]
    
    @staticmethod
    def delete_file_chunks(db: Session, file_id: int, user_id: int) -> int:
        """Delete all chunks for a file"""
        deleted = db.query(DocumentChunk).filter(
            DocumentChunk.file_id == file_id,
            DocumentChunk.user_id == user_id
        ).delete()
        
        db.commit()
        return deleted
    
    @staticmethod
    def save_metrics(
        db: Session,
        user_id: int,
        query: str,
        metrics: Dict,
        conversation_id: Optional[int] = None,
        message_id: Optional[int] = None
    ) -> RAGMetrics:
        """Save RAG metrics"""
        metric = RAGMetrics(
            user_id=user_id,
            conversation_id=conversation_id,
            message_id=message_id,
            query=query,
            query_length=len(query),
            chunks_retrieved=metrics.get('chunks_retrieved', 0),
            retrieval_time_ms=metrics.get('retrieval_time_ms', 0),
            retrieval_method=metrics.get('retrieval_method', 'hybrid'),
            avg_relevance_score=metrics.get('avg_relevance_score'),
            max_relevance_score=metrics.get('max_relevance_score'),
            min_relevance_score=metrics.get('min_relevance_score'),
            files_covered=metrics.get('files_covered', 0),
            unique_chunks=metrics.get('unique_chunks', 0),
            generation_time_ms=metrics.get('generation_time_ms'),
            total_tokens=metrics.get('total_tokens'),
            citations_generated=metrics.get('citations_generated', 0)
        )
        
        db.add(metric)
        db.commit()
        db.refresh(metric)
        return metric
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int) -> Dict:
        """Get RAG usage statistics for user"""
        total_chunks = db.query(DocumentChunk).filter(
            DocumentChunk.user_id == user_id
        ).count()
        
        total_queries = db.query(RAGMetrics).filter(
            RAGMetrics.user_id == user_id
        ).count()
        
        avg_retrieval_time = db.query(
            func.avg(RAGMetrics.retrieval_time_ms)
        ).filter(
            RAGMetrics.user_id == user_id
        ).scalar() or 0
        
        return {
            "total_chunks": total_chunks,
            "total_queries": total_queries,
            "avg_retrieval_time_ms": round(avg_retrieval_time, 2)
        }

