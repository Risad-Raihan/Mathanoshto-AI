"""
Thumbnail generation for files
"""
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont
import io


class ThumbnailGenerator:
    """Generate thumbnails for various file types"""
    
    DEFAULT_SIZE = (200, 200)
    ICON_SIZE = (150, 150)
    
    @staticmethod
    def generate_image_thumbnail(
        file_path: Path,
        output_path: Path,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> bool:
        """Generate thumbnail for image files"""
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (for PNG with transparency, etc.)
                if img.mode in ('RGBA', 'LA', 'P'):
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Create thumbnail maintaining aspect ratio
                img.thumbnail(size, Image.Resampling.LANCZOS)
                
                # Create a new image with the exact size and paste the thumbnail centered
                thumbnail = Image.new('RGB', size, (255, 255, 255))
                offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
                thumbnail.paste(img, offset)
                
                # Save thumbnail
                output_path.parent.mkdir(parents=True, exist_ok=True)
                thumbnail.save(output_path, 'JPEG', quality=85)
                
            return True
        
        except Exception as e:
            print(f"Error generating image thumbnail: {e}")
            return False
    
    @staticmethod
    def generate_pdf_thumbnail(
        file_path: Path,
        output_path: Path,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> bool:
        """Generate thumbnail from first page of PDF"""
        try:
            import fitz  # PyMuPDF
            
            # Open PDF
            doc = fitz.open(file_path)
            
            if len(doc) == 0:
                return False
            
            # Get first page
            page = doc[0]
            
            # Render page to image
            # Calculate zoom to get reasonable resolution
            zoom = 2.0  # Increase for better quality
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            
            # Create thumbnail
            img.thumbnail(size, Image.Resampling.LANCZOS)
            
            # Create a new image with the exact size and paste the thumbnail centered
            thumbnail = Image.new('RGB', size, (255, 255, 255))
            offset = ((size[0] - img.size[0]) // 2, (size[1] - img.size[1]) // 2)
            thumbnail.paste(img, offset)
            
            # Save thumbnail
            output_path.parent.mkdir(parents=True, exist_ok=True)
            thumbnail.save(output_path, 'JPEG', quality=85)
            
            doc.close()
            return True
        
        except ImportError:
            # Fallback: Create a generic PDF icon thumbnail
            return ThumbnailGenerator.generate_icon_thumbnail('PDF', output_path, size, (220, 50, 50))
        
        except Exception as e:
            print(f"Error generating PDF thumbnail: {e}")
            return ThumbnailGenerator.generate_icon_thumbnail('PDF', output_path, size, (220, 50, 50))
    
    @staticmethod
    def generate_icon_thumbnail(
        text: str,
        output_path: Path,
        size: Tuple[int, int] = DEFAULT_SIZE,
        bg_color: Tuple[int, int, int] = (100, 100, 100)
    ) -> bool:
        """Generate a simple icon thumbnail with text"""
        try:
            # Create image with background color
            img = Image.new('RGB', size, bg_color)
            draw = ImageDraw.Draw(img)
            
            # Try to use a nice font, fallback to default
            try:
                # Try to find a system font
                font_size = size[0] // 5
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
            except:
                # Use default font
                font = ImageFont.load_default()
            
            # Calculate text position (centered)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            position = (
                (size[0] - text_width) // 2,
                (size[1] - text_height) // 2
            )
            
            # Draw text
            draw.text(position, text, fill=(255, 255, 255), font=font)
            
            # Save
            output_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(output_path, 'JPEG', quality=85)
            
            return True
        
        except Exception as e:
            print(f"Error generating icon thumbnail: {e}")
            return False
    
    @staticmethod
    def generate_thumbnail(
        file_path: Path,
        file_type: str,
        output_path: Path,
        size: Tuple[int, int] = DEFAULT_SIZE
    ) -> bool:
        """
        Generate thumbnail based on file type
        
        Args:
            file_path: Path to the source file
            file_type: Type of file ('pdf', 'image', 'docx', etc.)
            output_path: Path where thumbnail should be saved
            size: Size of thumbnail (width, height)
        
        Returns:
            True if successful, False otherwise
        """
        file_path = Path(file_path)
        output_path = Path(output_path)
        
        if not file_path.exists():
            return False
        
        # Route to appropriate generator
        if file_type == 'image':
            return ThumbnailGenerator.generate_image_thumbnail(file_path, output_path, size)
        
        elif file_type == 'pdf':
            return ThumbnailGenerator.generate_pdf_thumbnail(file_path, output_path, size)
        
        elif file_type == 'docx':
            return ThumbnailGenerator.generate_icon_thumbnail('DOCX', output_path, size, (41, 128, 185))
        
        elif file_type == 'txt':
            return ThumbnailGenerator.generate_icon_thumbnail('TXT', output_path, size, (149, 165, 166))
        
        elif file_type == 'csv':
            return ThumbnailGenerator.generate_icon_thumbnail('CSV', output_path, size, (46, 204, 113))
        
        elif file_type == 'json':
            return ThumbnailGenerator.generate_icon_thumbnail('JSON', output_path, size, (241, 196, 15))
        
        elif file_type == 'xml':
            return ThumbnailGenerator.generate_icon_thumbnail('XML', output_path, size, (230, 126, 34))
        
        elif file_type == 'excel':
            return ThumbnailGenerator.generate_icon_thumbnail('XLS', output_path, size, (34, 153, 84))
        
        else:
            return ThumbnailGenerator.generate_icon_thumbnail('FILE', output_path, size, (127, 140, 141))


# Convenience instance
thumbnail_generator = ThumbnailGenerator()

