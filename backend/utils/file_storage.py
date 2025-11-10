"""
File storage system with organized directory structure
"""
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple
import hashlib
import mimetypes


class FileStorage:
    """Manages file storage on disk"""
    
    # Default upload directory
    BASE_UPLOAD_DIR = Path("uploads")
    
    # Supported file types and extensions
    SUPPORTED_TYPES = {
        'pdf': ['.pdf'],
        'docx': ['.docx', '.doc'],
        'txt': ['.txt', '.text', '.md', '.markdown'],
        'csv': ['.csv'],
        'json': ['.json'],
        'xml': ['.xml'],
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg'],
        'excel': ['.xlsx', '.xls'],
        'other': []
    }
    
    # Maximum file sizes (in bytes) - configurable per type
    MAX_FILE_SIZES = {
        'pdf': 50 * 1024 * 1024,      # 50 MB
        'docx': 25 * 1024 * 1024,      # 25 MB
        'txt': 10 * 1024 * 1024,       # 10 MB
        'csv': 20 * 1024 * 1024,       # 20 MB
        'json': 10 * 1024 * 1024,      # 10 MB
        'xml': 10 * 1024 * 1024,       # 10 MB
        'image': 10 * 1024 * 1024,     # 10 MB
        'excel': 30 * 1024 * 1024,     # 30 MB
        'default': 100 * 1024 * 1024,  # 100 MB default
    }
    
    def __init__(self, base_dir: Optional[Path] = None):
        """Initialize file storage"""
        self.base_dir = base_dir or self.BASE_UPLOAD_DIR
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_file_type(filename: str) -> str:
        """Determine file type from extension"""
        ext = Path(filename).suffix.lower()
        for file_type, extensions in FileStorage.SUPPORTED_TYPES.items():
            if ext in extensions:
                return file_type
        return 'other'
    
    @staticmethod
    def get_mime_type(filename: str) -> str:
        """Get MIME type for a file"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def is_supported_file(filename: str) -> bool:
        """Check if file type is supported"""
        file_type = FileStorage.get_file_type(filename)
        return file_type != 'other' or True  # Allow all files but categorize
    
    @staticmethod
    def validate_file_size(file_size: int, file_type: str) -> Tuple[bool, Optional[str]]:
        """Validate file size against limits"""
        max_size = FileStorage.MAX_FILE_SIZES.get(file_type, FileStorage.MAX_FILE_SIZES['default'])
        
        if file_size > max_size:
            max_mb = max_size / (1024 * 1024)
            actual_mb = file_size / (1024 * 1024)
            return False, f"File size ({actual_mb:.2f}MB) exceeds maximum allowed ({max_mb:.2f}MB) for {file_type} files"
        
        return True, None
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent security issues"""
        # Get the name and extension
        name = Path(filename).stem
        ext = Path(filename).suffix
        
        # Remove or replace dangerous characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
        name = ''.join(c if c in safe_chars else '_' for c in name)
        
        # Limit length
        if len(name) > 200:
            name = name[:200]
        
        return f"{name}{ext}"
    
    @staticmethod
    def generate_unique_filename(original_filename: str, user_id: int) -> str:
        """Generate a unique filename using hash"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ext = Path(original_filename).suffix
        
        # Create hash from original filename + timestamp + user_id
        hash_input = f"{original_filename}_{timestamp}_{user_id}".encode()
        file_hash = hashlib.md5(hash_input).hexdigest()[:8]
        
        safe_name = FileStorage.sanitize_filename(Path(original_filename).stem)
        return f"{safe_name}_{timestamp}_{file_hash}{ext}"
    
    def get_user_directory(self, user_id: int, create: bool = True) -> Path:
        """Get or create user's storage directory organized by year/month"""
        now = datetime.now()
        user_dir = self.base_dir / str(user_id) / str(now.year) / f"{now.month:02d}"
        
        if create:
            user_dir.mkdir(parents=True, exist_ok=True)
        
        return user_dir
    
    def get_thumbnails_directory(self, user_id: int, create: bool = True) -> Path:
        """Get or create thumbnails directory for user"""
        thumb_dir = self.base_dir / str(user_id) / "thumbnails"
        
        if create:
            thumb_dir.mkdir(parents=True, exist_ok=True)
        
        return thumb_dir
    
    def save_file(
        self,
        file_data: bytes,
        original_filename: str,
        user_id: int
    ) -> Tuple[str, str, int]:
        """
        Save file to disk
        
        Returns:
            Tuple of (file_path relative to base_dir, unique_filename, file_size)
        """
        # Generate unique filename
        unique_filename = self.generate_unique_filename(original_filename, user_id)
        
        # Get user directory
        user_dir = self.get_user_directory(user_id)
        
        # Full path
        full_path = user_dir / unique_filename
        
        # Write file
        with open(full_path, 'wb') as f:
            f.write(file_data)
        
        # Calculate relative path from base directory
        relative_path = str(full_path.relative_to(self.base_dir))
        
        # Get file size
        file_size = len(file_data)
        
        return relative_path, unique_filename, file_size
    
    def get_file_path(self, relative_path: str) -> Path:
        """Get full path from relative path"""
        return self.base_dir / relative_path
    
    def read_file(self, relative_path: str) -> Optional[bytes]:
        """Read file from disk"""
        full_path = self.get_file_path(relative_path)
        
        if not full_path.exists():
            return None
        
        with open(full_path, 'rb') as f:
            return f.read()
    
    def delete_file(self, relative_path: str) -> bool:
        """Delete file from disk"""
        full_path = self.get_file_path(relative_path)
        
        if not full_path.exists():
            return False
        
        try:
            full_path.unlink()
            
            # Try to remove empty parent directories
            try:
                full_path.parent.rmdir()
                full_path.parent.parent.rmdir()
            except OSError:
                pass  # Directory not empty
            
            return True
        except Exception as e:
            print(f"Error deleting file {relative_path}: {e}")
            return False
    
    def move_file(self, old_relative_path: str, new_relative_path: str) -> bool:
        """Move file to new location"""
        old_path = self.get_file_path(old_relative_path)
        new_path = self.get_file_path(new_relative_path)
        
        if not old_path.exists():
            return False
        
        try:
            new_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(old_path), str(new_path))
            return True
        except Exception as e:
            print(f"Error moving file: {e}")
            return False
    
    def get_storage_usage(self, user_id: int) -> int:
        """Calculate total storage used by user (in bytes)"""
        user_base_dir = self.base_dir / str(user_id)
        
        if not user_base_dir.exists():
            return 0
        
        total_size = 0
        for root, dirs, files in os.walk(user_base_dir):
            for file in files:
                file_path = Path(root) / file
                try:
                    total_size += file_path.stat().st_size
                except OSError:
                    pass
        
        return total_size
    
    def cleanup_empty_directories(self, user_id: int):
        """Remove empty directories for a user"""
        user_base_dir = self.base_dir / str(user_id)
        
        if not user_base_dir.exists():
            return
        
        # Walk bottom-up to remove empty directories
        for root, dirs, files in os.walk(user_base_dir, topdown=False):
            for dir_name in dirs:
                dir_path = Path(root) / dir_name
                try:
                    dir_path.rmdir()  # Only removes if empty
                except OSError:
                    pass  # Directory not empty


# Global instance
file_storage = FileStorage()

