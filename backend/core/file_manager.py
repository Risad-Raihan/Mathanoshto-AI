"""
Core File Manager - Coordinates file operations, storage, and parsing
"""
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from backend.database.file_operations import FileDB, FileTagDB, ConversationFileDB
from backend.utils.file_storage import file_storage, FileStorage
from backend.utils.file_parser import file_parser, FileParser
from backend.utils.thumbnail_generator import thumbnail_generator, ThumbnailGenerator


class FileManager:
    """
    High-level file management coordinating storage, parsing, and database operations
    """
    
    def __init__(self):
        self.storage = file_storage
        self.parser = file_parser
        self.thumbnail_gen = thumbnail_generator
    
    def upload_file(
        self,
        file_data: bytes,
        original_filename: str,
        user_id: int,
        description: Optional[str] = None,
        folder_path: str = "/",
        enable_text_extraction: bool = True,
        enable_thumbnail: bool = True,
        enable_ocr: bool = False
    ) -> Dict[str, Any]:
        """
        Upload and process a file
        
        Args:
            file_data: Raw file bytes
            original_filename: Original filename
            user_id: User ID
            description: Optional file description
            folder_path: Virtual folder path
            enable_text_extraction: Whether to extract text content
            enable_thumbnail: Whether to generate thumbnail
            enable_ocr: Whether to use OCR for images
        
        Returns:
            Dictionary with success status and file info or error
        """
        try:
            # Validate file type
            if not self.storage.is_supported_file(original_filename):
                return {
                    'success': False,
                    'error': 'Unsupported file type'
                }
            
            # Get file info
            file_type = self.storage.get_file_type(original_filename)
            mime_type = self.storage.get_mime_type(original_filename)
            file_size = len(file_data)
            
            # Validate file size
            is_valid, error_msg = self.storage.validate_file_size(file_size, file_type)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg
                }
            
            # Save file to disk
            file_path, unique_filename, _ = self.storage.save_file(
                file_data, original_filename, user_id
            )
            
            full_path = self.storage.get_file_path(file_path)
            
            # Extract text if enabled
            extracted_text = None
            metadata = {}
            if enable_text_extraction and file_type not in ['image']:
                parse_result = self.parser.parse_file(full_path, file_type, enable_ocr=False)
                if parse_result['success']:
                    extracted_text = parse_result['text']
                    metadata = parse_result.get('metadata', {})
            
            # Extract text from images if OCR enabled
            if enable_text_extraction and enable_ocr and file_type == 'image':
                parse_result = self.parser.parse_image_ocr(full_path)
                if parse_result['success']:
                    extracted_text = parse_result['text']
                    metadata = parse_result.get('metadata', {})
            
            # Generate thumbnail if enabled
            thumbnail_path = None
            if enable_thumbnail:
                thumb_dir = self.storage.get_thumbnails_directory(user_id)
                thumb_filename = f"thumb_{unique_filename}"
                if file_type not in ['image', 'pdf']:
                    thumb_filename = f"thumb_{Path(unique_filename).stem}.jpg"
                
                thumb_full_path = thumb_dir / thumb_filename
                
                if self.thumbnail_gen.generate_thumbnail(full_path, file_type, thumb_full_path):
                    thumbnail_path = str(thumb_full_path.relative_to(self.storage.base_dir))
            
            # Extract metadata fields
            author = metadata.get('author')
            creation_date = None
            if 'created' in metadata and metadata['created']:
                try:
                    if isinstance(metadata['created'], str):
                        creation_date = datetime.fromisoformat(metadata['created'].replace('Z', '+00:00'))
                    elif isinstance(metadata['created'], datetime):
                        creation_date = metadata['created']
                except:
                    pass
            
            # Create database record
            file_record = FileDB.create_file(
                user_id=user_id,
                filename=unique_filename,
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
            
            return {
                'success': True,
                'file': {
                    'id': file_record.id,
                    'filename': file_record.filename,
                    'original_filename': file_record.original_filename,
                    'file_type': file_record.file_type,
                    'file_size': file_record.file_size,
                    'file_path': file_record.file_path,
                    'thumbnail_path': file_record.thumbnail_path,
                    'uploaded_at': file_record.uploaded_at.isoformat(),
                    'has_text': bool(extracted_text),
                    'text_preview': extracted_text[:200] if extracted_text else None
                }
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to upload file: {str(e)}'
            }
    
    def get_file(self, file_id: int, user_id: int) -> Optional[Dict[str, Any]]:
        """Get file information"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return None
        
        # Get tags
        tags = FileTagDB.get_file_tags(file_id)
        
        return {
            'id': file_record.id,
            'filename': file_record.filename,
            'original_filename': file_record.original_filename,
            'file_type': file_record.file_type,
            'mime_type': file_record.mime_type,
            'file_size': file_record.file_size,
            'file_path': file_record.file_path,
            'description': file_record.description,
            'folder_path': file_record.folder_path,
            'thumbnail_path': file_record.thumbnail_path,
            'uploaded_at': file_record.uploaded_at.isoformat(),
            'updated_at': file_record.updated_at.isoformat(),
            'tags': tags,
            'has_text': bool(file_record.extracted_text)
        }
    
    def download_file(self, file_id: int, user_id: int) -> Optional[Tuple[bytes, str, str]]:
        """
        Download file data
        
        Returns:
            Tuple of (file_data, filename, mime_type) or None
        """
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return None
        
        file_data = self.storage.read_file(file_record.file_path)
        
        if not file_data:
            return None
        
        return file_data, file_record.original_filename, file_record.mime_type
    
    def delete_file(self, file_id: int, user_id: int) -> bool:
        """Delete a file"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        # Delete from disk
        self.storage.delete_file(file_record.file_path)
        
        # Delete thumbnail if exists
        if file_record.thumbnail_path:
            self.storage.delete_file(file_record.thumbnail_path)
        
        # Delete from database (will cascade to tags and conversation_files)
        return FileDB.delete_file(file_id)
    
    def rename_file(self, file_id: int, user_id: int, new_filename: str) -> bool:
        """Rename a file"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        # Sanitize new filename
        safe_filename = self.storage.sanitize_filename(new_filename)
        
        # Update in database
        updated = FileDB.update_file(file_id, filename=safe_filename)
        return updated is not None
    
    def update_file_description(self, file_id: int, user_id: int, description: str) -> bool:
        """Update file description"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        updated = FileDB.update_file(file_id, description=description)
        return updated is not None
    
    def move_file(self, file_id: int, user_id: int, new_folder_path: str) -> bool:
        """Move file to different folder"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        updated = FileDB.update_file(file_id, folder_path=new_folder_path)
        return updated is not None
    
    def list_files(
        self,
        user_id: int,
        folder_path: Optional[str] = None,
        file_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort_by: str = "uploaded_at",
        sort_order: str = "desc"
    ) -> List[Dict[str, Any]]:
        """List files with optional filtering"""
        files = FileDB.list_user_files(
            user_id=user_id,
            folder_path=folder_path,
            file_type=file_type,
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        result = []
        for f in files:
            tags = FileTagDB.get_file_tags(f.id)
            result.append({
                'id': f.id,
                'filename': f.filename,
                'original_filename': f.original_filename,
                'file_type': f.file_type,
                'file_size': f.file_size,
                'folder_path': f.folder_path,
                'thumbnail_path': f.thumbnail_path,
                'uploaded_at': f.uploaded_at.isoformat(),
                'tags': tags,
                'description': f.description
            })
        
        return result
    
    def search_files(
        self,
        user_id: int,
        query: str,
        file_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Search files"""
        files = FileDB.search_files(
            user_id=user_id,
            search_query=query,
            file_type=file_type,
            tags=tags,
            limit=limit
        )
        
        result = []
        for f in files:
            file_tags = FileTagDB.get_file_tags(f.id)
            result.append({
                'id': f.id,
                'filename': f.filename,
                'original_filename': f.original_filename,
                'file_type': f.file_type,
                'file_size': f.file_size,
                'folder_path': f.folder_path,
                'thumbnail_path': f.thumbnail_path,
                'uploaded_at': f.uploaded_at.isoformat(),
                'tags': file_tags,
                'description': f.description
            })
        
        return result
    
    def add_tags(self, file_id: int, user_id: int, tags: List[str]) -> bool:
        """Add tags to a file"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        FileTagDB.bulk_add_tags(file_id, tags)
        return True
    
    def remove_tags(self, file_id: int, user_id: int, tags: List[str]) -> bool:
        """Remove tags from a file"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        FileTagDB.bulk_remove_tags(file_id, tags)
        return True
    
    def get_user_tags(self, user_id: int) -> List[Tuple[str, int]]:
        """Get all tags for a user with usage counts"""
        return FileTagDB.get_all_user_tags(user_id)
    
    def get_storage_stats(self, user_id: int) -> Dict[str, Any]:
        """Get storage usage statistics"""
        return FileDB.get_user_storage_usage(user_id)
    
    def get_file_text(self, file_id: int, user_id: int) -> Optional[str]:
        """Get extracted text from a file"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return None
        
        return file_record.extracted_text
    
    def attach_to_conversation(
        self,
        file_id: int,
        conversation_id: int,
        user_id: int,
        message_id: Optional[int] = None,
        context_type: Optional[str] = None
    ) -> bool:
        """Attach a file to a conversation"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        ConversationFileDB.attach_file_to_conversation(
            conversation_id=conversation_id,
            file_id=file_id,
            message_id=message_id,
            context_type=context_type
        )
        return True
    
    def detach_from_conversation(
        self,
        file_id: int,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """Detach a file from a conversation"""
        file_record = FileDB.get_file(file_id)
        
        if not file_record or file_record.user_id != user_id:
            return False
        
        return ConversationFileDB.detach_file_from_conversation(conversation_id, file_id)
    
    def get_conversation_files(self, conversation_id: int, user_id: int) -> List[Dict[str, Any]]:
        """Get all files attached to a conversation"""
        files = ConversationFileDB.get_conversation_files(conversation_id)
        
        # Verify user has access to these files
        result = []
        for f in files:
            if f.user_id == user_id:
                tags = FileTagDB.get_file_tags(f.id)
                result.append({
                    'id': f.id,
                    'filename': f.filename,
                    'original_filename': f.original_filename,
                    'file_type': f.file_type,
                    'file_size': f.file_size,
                    'thumbnail_path': f.thumbnail_path,
                    'tags': tags
                })
        
        return result
    
    def bulk_delete_files(self, file_ids: List[int], user_id: int) -> int:
        """Delete multiple files"""
        count = 0
        for file_id in file_ids:
            if self.delete_file(file_id, user_id):
                count += 1
        return count
    
    def get_folders(self, user_id: int) -> List[str]:
        """Get list of folders for a user"""
        return FileDB.get_folders(user_id)


# Global instance
file_manager = FileManager()

