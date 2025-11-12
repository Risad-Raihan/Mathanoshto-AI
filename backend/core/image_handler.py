"""
Enhanced Image Handler - Comprehensive image processing and management
Supports upload, generation, clipboard, search integration, and vision models
"""
import base64
import io
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import requests
from PIL import Image
import mimetypes

class ImageHandler:
    """Comprehensive image handling system"""
    
    # Supported image formats
    SUPPORTED_FORMATS = {
        'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'
    }
    
    # Image directories
    UPLOAD_DIR = Path("uploads/images")
    GENERATED_DIR = Path("uploads/generated_images")
    SEARCH_CACHE_DIR = Path("uploads/search_images")
    
    # Maximum image sizes
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_DIMENSION = 4096  # pixels
    
    def __init__(self):
        """Initialize image handler"""
        # Create directories
        for dir_path in [self.UPLOAD_DIR, self.GENERATED_DIR, self.SEARCH_CACHE_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def validate_image(file_data: bytes, filename: str = None) -> Tuple[bool, Optional[str]]:
        """
        Validate image file
        
        Args:
            file_data: Image file bytes
            filename: Optional filename for format detection
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check size
        if len(file_data) > ImageHandler.MAX_UPLOAD_SIZE:
            size_mb = len(file_data) / (1024 * 1024)
            max_mb = ImageHandler.MAX_UPLOAD_SIZE / (1024 * 1024)
            return False, f"Image size ({size_mb:.1f}MB) exceeds maximum ({max_mb}MB)"
        
        # Try to open with PIL
        try:
            img = Image.open(io.BytesIO(file_data))
            
            # Check format
            if img.format.lower() not in ImageHandler.SUPPORTED_FORMATS:
                return False, f"Unsupported image format: {img.format}"
            
            # Check dimensions
            if max(img.size) > ImageHandler.MAX_DIMENSION:
                return False, f"Image dimension ({max(img.size)}px) exceeds maximum ({ImageHandler.MAX_DIMENSION}px)"
            
            return True, None
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def process_image(
        file_data: bytes,
        max_size: Optional[Tuple[int, int]] = None,
        format: str = 'PNG',
        quality: int = 95
    ) -> bytes:
        """
        Process and optimize image
        
        Args:
            file_data: Original image bytes
            max_size: Optional (width, height) to resize to
            format: Output format (PNG, JPEG, WEBP)
            quality: Quality for lossy formats (1-100)
            
        Returns:
            Processed image bytes
        """
        img = Image.open(io.BytesIO(file_data))
        
        # Convert RGBA to RGB for JPEG
        if format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        
        # Resize if needed
        if max_size:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save to bytes
        output = io.BytesIO()
        save_kwargs = {'format': format}
        if format.upper() in ('JPEG', 'WEBP'):
            save_kwargs['quality'] = quality
        
        img.save(output, **save_kwargs)
        return output.getvalue()
    
    def save_uploaded_image(
        self,
        file_data: bytes,
        filename: str,
        user_id: int,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Save uploaded image
        
        Args:
            file_data: Image file bytes
            filename: Original filename
            user_id: User ID
            metadata: Optional metadata
            
        Returns:
            Dictionary with image info
        """
        try:
            # Validate image
            is_valid, error = self.validate_image(file_data, filename)
            if not is_valid:
                return {'success': False, 'error': error}
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(file_data).hexdigest()[:8]
            ext = Path(filename).suffix or '.png'
            safe_name = Path(filename).stem[:50]
            
            unique_filename = f"{user_id}_{safe_name}_{timestamp}_{file_hash}{ext}"
            
            # Save original
            save_path = self.UPLOAD_DIR / unique_filename
            
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(file_data)
            
            # Get image info
            img = Image.open(io.BytesIO(file_data))
            
            # Get absolute and relative paths
            abs_path = save_path.resolve()
            rel_path = str(save_path)  # Already relative, just convert to string
            
            return {
                'success': True,
                'file_path': str(abs_path),
                'relative_path': rel_path,
                'filename': unique_filename,
                'original_filename': filename,
                'size_bytes': len(file_data),
                'size_kb': round(len(file_data) / 1024, 2),
                'format': img.format,
                'dimensions': img.size,
                'mode': img.mode,
                'created_at': datetime.now().isoformat(),
                'metadata': metadata or {}
            }
            
        except Exception as e:
            return {'success': False, 'error': f"Failed to save image: {str(e)}"}
    
    def save_from_clipboard(
        self,
        clipboard_data: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Save image from clipboard (base64 data)
        
        Args:
            clipboard_data: Base64 encoded image data or data URL
            user_id: User ID
            
        Returns:
            Dictionary with image info
        """
        try:
            # Handle data URL format (data:image/png;base64,...)
            if clipboard_data.startswith('data:'):
                clipboard_data = clipboard_data.split(',', 1)[1]
            
            # Decode base64
            file_data = base64.b64decode(clipboard_data)
            
            # Save as uploaded image
            filename = f"clipboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            return self.save_uploaded_image(
                file_data,
                filename,
                user_id,
                metadata={'source': 'clipboard'}
            )
            
        except Exception as e:
            return {'success': False, 'error': f"Failed to process clipboard image: {str(e)}"}
    
    def save_from_url(
        self,
        url: str,
        user_id: int,
        source: str = 'web'
    ) -> Dict[str, Any]:
        """
        Download and save image from URL
        
        Args:
            url: Image URL
            user_id: User ID
            source: Source identifier (e.g., 'search', 'web')
            
        Returns:
            Dictionary with image info
        """
        try:
            # Download image
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; ImageBot/1.0)'
            })
            response.raise_for_status()
            
            file_data = response.content
            
            # Get filename from URL or generate one
            url_path = Path(url.split('?')[0])  # Remove query params
            filename = url_path.name or f"downloaded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            
            # Determine save directory based on source
            if source == 'search':
                save_dir = self.SEARCH_CACHE_DIR
            else:
                save_dir = self.UPLOAD_DIR
            
            # Validate image
            is_valid, error = self.validate_image(file_data, filename)
            if not is_valid:
                return {'success': False, 'error': error}
            
            # Generate unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_hash = hashlib.md5(file_data).hexdigest()[:8]
            ext = Path(filename).suffix or '.png'
            
            unique_filename = f"{user_id}_{timestamp}_{file_hash}{ext}"
            
            # Save
            save_path = save_dir / unique_filename
            
            # Ensure parent directory exists
            save_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_path, 'wb') as f:
                f.write(file_data)
            
            # Get image info
            img = Image.open(io.BytesIO(file_data))
            
            # Get absolute and relative paths
            abs_path = save_path.resolve()
            rel_path = str(save_path)  # Already relative, just convert to string
            
            return {
                'success': True,
                'file_path': str(abs_path),
                'relative_path': rel_path,
                'filename': unique_filename,
                'original_url': url,
                'size_bytes': len(file_data),
                'size_kb': round(len(file_data) / 1024, 2),
                'format': img.format,
                'dimensions': img.size,
                'created_at': datetime.now().isoformat(),
                'source': source
            }
            
        except requests.RequestException as e:
            return {'success': False, 'error': f"Failed to download image: {str(e)}"}
        except Exception as e:
            return {'success': False, 'error': f"Failed to save image: {str(e)}"}
    
    def create_thumbnail(
        self,
        image_path: str,
        size: Tuple[int, int] = (200, 200)
    ) -> Optional[str]:
        """
        Create thumbnail for an image
        
        Args:
            image_path: Path to original image
            size: Thumbnail size (width, height)
            
        Returns:
            Path to thumbnail or None on failure
        """
        try:
            img = Image.open(image_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Save thumbnail
            path = Path(image_path)
            thumb_path = path.parent / f"{path.stem}_thumb{path.suffix}"
            img.save(thumb_path)
            
            return str(thumb_path)
            
        except Exception as e:
            print(f"Failed to create thumbnail: {e}")
            return None
    
    def get_image_base64(self, image_path: str) -> Optional[str]:
        """
        Get base64 encoded image for embedding
        
        Args:
            image_path: Path to image
            
        Returns:
            Base64 encoded string or None
        """
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"Failed to encode image: {e}")
            return None
    
    def get_image_data_url(self, image_path: str) -> Optional[str]:
        """
        Get data URL for image (for embedding in HTML/markdown)
        
        Args:
            image_path: Path to image
            
        Returns:
            Data URL string or None
        """
        try:
            mime_type = mimetypes.guess_type(image_path)[0] or 'image/png'
            base64_data = self.get_image_base64(image_path)
            if base64_data:
                return f"data:{mime_type};base64,{base64_data}"
            return None
        except Exception as e:
            print(f"Failed to create data URL: {e}")
            return None
    
    def list_user_images(
        self,
        user_id: int,
        source: str = 'all',
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        List images for a user
        
        Args:
            user_id: User ID
            source: Filter by source ('all', 'upload', 'generated', 'search')
            limit: Maximum number of images to return
            
        Returns:
            List of image info dictionaries
        """
        images = []
        
        # Determine directories to search
        if source == 'all':
            search_dirs = [self.UPLOAD_DIR, self.GENERATED_DIR, self.SEARCH_CACHE_DIR]
        elif source == 'upload':
            search_dirs = [self.UPLOAD_DIR]
        elif source == 'generated':
            search_dirs = [self.GENERATED_DIR]
        elif source == 'search':
            search_dirs = [self.SEARCH_CACHE_DIR]
        else:
            return []
        
        # Search for user's images
        for search_dir in search_dirs:
            if not search_dir.exists():
                continue
                
            pattern = f"{user_id}_*"
            for img_path in sorted(search_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True):
                if len(images) >= limit:
                    break
                
                try:
                    stat = img_path.stat()
                    img = Image.open(img_path)
                    
                    # Get absolute path
                    abs_path = img_path.resolve()
                    
                    images.append({
                        'file_path': str(abs_path),
                        'relative_path': str(img_path),  # Keep original relative path
                        'filename': img_path.name,
                        'size_bytes': stat.st_size,
                        'size_kb': round(stat.st_size / 1024, 2),
                        'format': img.format,
                        'dimensions': img.size,
                        'created_at': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified_at': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
                except Exception as e:
                    print(f"Error reading image {img_path}: {e}")
                    continue
        
        return images
    
    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image
        
        Args:
            image_path: Path to image
            
        Returns:
            True if deleted successfully
        """
        try:
            path = Path(image_path)
            if path.exists():
                path.unlink()
                
                # Also delete thumbnail if exists
                thumb_path = path.parent / f"{path.stem}_thumb{path.suffix}"
                if thumb_path.exists():
                    thumb_path.unlink()
                
                return True
            return False
        except Exception as e:
            print(f"Failed to delete image: {e}")
            return False


# Global instance
image_handler = ImageHandler()

