"""
Database operations for file management
"""
from sqlalchemy import create_engine, desc, or_, and_
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict, Tuple
from datetime import datetime
import os
import shutil
from pathlib import Path

from backend.database.models import Base, File, FileTag, ConversationFile
from backend.config.settings import settings

# Import existing engine and session from operations.py
from backend.database.operations import engine, SessionLocal, get_db


class FileDB:
    """Database operations for file management"""
    
    @staticmethod
    def create_file(
        user_id: int,
        filename: str,
        original_filename: str,
        file_type: str,
        mime_type: str,
        file_size: int,
        file_path: str,
        description: Optional[str] = None,
        extracted_text: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
        author: Optional[str] = None,
        creation_date: Optional[datetime] = None,
        folder_path: str = "/"
    ) -> File:
        """Create a new file record"""
        db = get_db()
        try:
            file = File(
                user_id=user_id,
                filename=filename,
                original_filename=original_filename,
                file_type=file_type,
                mime_type=mime_type,
                file_size=file_size,
                file_path=file_path,
                description=description,
                extracted_text=extracted_text,
                thumbnail_path=thumbnail_path,
                author=author,
                creation_date=creation_date,
                folder_path=folder_path
            )
            db.add(file)
            db.commit()
            db.refresh(file)
            return file
        finally:
            db.close()
    
    @staticmethod
    def get_file(file_id: int) -> Optional[File]:
        """Get a file by ID"""
        db = get_db()
        try:
            return db.query(File).filter(File.id == file_id).first()
        finally:
            db.close()
    
    @staticmethod
    def get_file_by_path(file_path: str, user_id: int) -> Optional[File]:
        """Get a file by path and user"""
        db = get_db()
        try:
            return db.query(File).filter(
                and_(File.file_path == file_path, File.user_id == user_id)
            ).first()
        finally:
            db.close()
    
    @staticmethod
    def list_user_files(
        user_id: int,
        folder_path: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "uploaded_at",
        sort_order: str = "desc"
    ) -> List[File]:
        """List files for a user with optional filtering"""
        db = get_db()
        try:
            query = db.query(File).filter(File.user_id == user_id)
            
            # Filter by folder
            if folder_path is not None:
                query = query.filter(File.folder_path == folder_path)
            
            # Filter by file type
            if file_type:
                query = query.filter(File.file_type == file_type)
            
            # Apply sorting
            sort_column = getattr(File, sort_by, File.uploaded_at)
            if sort_order == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)
            
            files = query.limit(limit).offset(offset).all()
            db.expunge_all()
            return files
        finally:
            db.close()
    
    @staticmethod
    def search_files(
        user_id: int,
        search_query: str,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[File]:
        """Search files by name, description, or content"""
        db = get_db()
        try:
            query = db.query(File).filter(File.user_id == user_id)
            
            # Search in filename, description, and extracted text
            search_filter = or_(
                File.filename.ilike(f"%{search_query}%"),
                File.original_filename.ilike(f"%{search_query}%"),
                File.description.ilike(f"%{search_query}%"),
                File.extracted_text.ilike(f"%{search_query}%")
            )
            query = query.filter(search_filter)
            
            # Filter by file type
            if file_type:
                query = query.filter(File.file_type == file_type)
            
            # Filter by tags
            if tags:
                query = query.join(FileTag).filter(FileTag.tag.in_(tags))
            
            files = query.order_by(desc(File.uploaded_at)).limit(limit).all()
            db.expunge_all()
            return files
        finally:
            db.close()
    
    @staticmethod
    def update_file(
        file_id: int,
        filename: Optional[str] = None,
        description: Optional[str] = None,
        folder_path: Optional[str] = None,
        extracted_text: Optional[str] = None,
        thumbnail_path: Optional[str] = None
    ) -> Optional[File]:
        """Update file metadata"""
        db = get_db()
        try:
            file = db.query(File).filter(File.id == file_id).first()
            if not file:
                return None
            
            if filename is not None:
                file.filename = filename
            if description is not None:
                file.description = description
            if folder_path is not None:
                file.folder_path = folder_path
            if extracted_text is not None:
                file.extracted_text = extracted_text
            if thumbnail_path is not None:
                file.thumbnail_path = thumbnail_path
            
            file.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(file)
            return file
        finally:
            db.close()
    
    @staticmethod
    def delete_file(file_id: int) -> bool:
        """Delete a file record"""
        db = get_db()
        try:
            file = db.query(File).filter(File.id == file_id).first()
            if not file:
                return False
            
            db.delete(file)
            db.commit()
            return True
        finally:
            db.close()
    
    @staticmethod
    def get_user_storage_usage(user_id: int) -> Dict[str, any]:
        """Get storage usage statistics for a user"""
        db = get_db()
        try:
            files = db.query(File).filter(File.user_id == user_id).all()
            
            total_size = sum(f.file_size for f in files)
            file_count = len(files)
            
            # Count by type
            type_counts = {}
            for f in files:
                type_counts[f.file_type] = type_counts.get(f.file_type, 0) + 1
            
            return {
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count,
                "by_type": type_counts
            }
        finally:
            db.close()
    
    @staticmethod
    def get_folders(user_id: int) -> List[str]:
        """Get list of unique folder paths for a user"""
        db = get_db()
        try:
            folders = db.query(File.folder_path).filter(
                File.user_id == user_id
            ).distinct().all()
            return [f[0] for f in folders if f[0]]
        finally:
            db.close()


class FileTagDB:
    """Database operations for file tags"""
    
    @staticmethod
    def add_tag(file_id: int, tag: str) -> FileTag:
        """Add a tag to a file"""
        db = get_db()
        try:
            # Check if tag already exists
            existing = db.query(FileTag).filter(
                and_(FileTag.file_id == file_id, FileTag.tag == tag.lower())
            ).first()
            
            if existing:
                return existing
            
            file_tag = FileTag(file_id=file_id, tag=tag.lower())
            db.add(file_tag)
            db.commit()
            db.refresh(file_tag)
            return file_tag
        finally:
            db.close()
    
    @staticmethod
    def remove_tag(file_id: int, tag: str) -> bool:
        """Remove a tag from a file"""
        db = get_db()
        try:
            file_tag = db.query(FileTag).filter(
                and_(FileTag.file_id == file_id, FileTag.tag == tag.lower())
            ).first()
            
            if not file_tag:
                return False
            
            db.delete(file_tag)
            db.commit()
            return True
        finally:
            db.close()
    
    @staticmethod
    def get_file_tags(file_id: int) -> List[str]:
        """Get all tags for a file"""
        db = get_db()
        try:
            tags = db.query(FileTag.tag).filter(FileTag.file_id == file_id).all()
            return [t[0] for t in tags]
        finally:
            db.close()
    
    @staticmethod
    def get_all_user_tags(user_id: int) -> List[Tuple[str, int]]:
        """Get all unique tags for a user with usage count"""
        db = get_db()
        try:
            from sqlalchemy import func
            tags = db.query(
                FileTag.tag, 
                func.count(FileTag.id).label('count')
            ).join(File).filter(
                File.user_id == user_id
            ).group_by(FileTag.tag).order_by(desc('count')).all()
            
            return [(t[0], t[1]) for t in tags]
        finally:
            db.close()
    
    @staticmethod
    def bulk_add_tags(file_id: int, tags: List[str]) -> List[FileTag]:
        """Add multiple tags to a file"""
        result = []
        for tag in tags:
            if tag.strip():
                result.append(FileTagDB.add_tag(file_id, tag.strip()))
        return result
    
    @staticmethod
    def bulk_remove_tags(file_id: int, tags: List[str]) -> int:
        """Remove multiple tags from a file"""
        count = 0
        for tag in tags:
            if FileTagDB.remove_tag(file_id, tag.strip()):
                count += 1
        return count


class ConversationFileDB:
    """Database operations for conversation-file associations"""
    
    @staticmethod
    def attach_file_to_conversation(
        conversation_id: int,
        file_id: int,
        message_id: Optional[int] = None,
        context_type: Optional[str] = None
    ) -> ConversationFile:
        """Attach a file to a conversation or message"""
        db = get_db()
        try:
            # Check if already attached
            existing = db.query(ConversationFile).filter(
                and_(
                    ConversationFile.conversation_id == conversation_id,
                    ConversationFile.file_id == file_id
                )
            ).first()
            
            if existing:
                return existing
            
            conv_file = ConversationFile(
                conversation_id=conversation_id,
                message_id=message_id,
                file_id=file_id,
                context_type=context_type
            )
            db.add(conv_file)
            db.commit()
            db.refresh(conv_file)
            return conv_file
        finally:
            db.close()
    
    @staticmethod
    def detach_file_from_conversation(conversation_id: int, file_id: int) -> bool:
        """Detach a file from a conversation"""
        db = get_db()
        try:
            conv_file = db.query(ConversationFile).filter(
                and_(
                    ConversationFile.conversation_id == conversation_id,
                    ConversationFile.file_id == file_id
                )
            ).first()
            
            if not conv_file:
                return False
            
            db.delete(conv_file)
            db.commit()
            return True
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_files(conversation_id: int) -> List[File]:
        """Get all files attached to a conversation"""
        db = get_db()
        try:
            files = db.query(File).join(ConversationFile).filter(
                ConversationFile.conversation_id == conversation_id
            ).order_by(desc(ConversationFile.attached_at)).all()
            db.expunge_all()
            return files
        finally:
            db.close()
    
    @staticmethod
    def get_message_files(message_id: int) -> List[File]:
        """Get all files attached to a specific message"""
        db = get_db()
        try:
            files = db.query(File).join(ConversationFile).filter(
                ConversationFile.message_id == message_id
            ).order_by(desc(ConversationFile.attached_at)).all()
            db.expunge_all()
            return files
        finally:
            db.close()
    
    @staticmethod
    def get_file_conversations(file_id: int) -> List[int]:
        """Get all conversation IDs that reference this file"""
        db = get_db()
        try:
            conv_ids = db.query(ConversationFile.conversation_id).filter(
                ConversationFile.file_id == file_id
            ).distinct().all()
            return [c[0] for c in conv_ids]
        finally:
            db.close()

