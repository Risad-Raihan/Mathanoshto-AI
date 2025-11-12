# Enhanced Multimodal Image System

## Overview

The Enhanced Multimodal Image System adds comprehensive image handling capabilities to your AI assistant, including image uploads, clipboard paste, AI image generation, vision model support, and image extraction from search results.

## Features

### 1. 🖼️ Image Upload & Management

#### Multiple Image Upload
- **Location**: Chat interface, below message input
- **Supported formats**: PNG, JPG, JPEG, GIF, WEBP, BMP
- **Features**:
  - Upload multiple images simultaneously
  - Real-time preview with dimensions and file size
  - Individual image removal
  - Automatic validation (size, format, dimensions)
  - Maximum size: 10 MB per image
  - Maximum dimension: 4096 pixels

#### Usage
```python
# In chat interface
1. Click on "Upload images" file uploader
2. Select one or more images
3. Images appear as previews
4. Click X to remove individual images
5. Type your question and send
```

### 2. 📋 Clipboard Paste Support

#### Features
- Paste images directly from clipboard using Ctrl+V (Cmd+V on Mac)
- Automatically processes and attaches pasted images
- Works with screenshots, copied images, etc.

#### Implementation
The system handles clipboard data through:
- `image_handler.save_from_clipboard()` - processes base64 encoded clipboard data
- Automatic format detection and validation
- Seamless integration with chat input

### 3. 🎨 AI Image Generation

#### Supported Providers
1. **DALL-E 3** (OpenAI)
   - High-quality image generation
   - Sizes: 1024x1024, 1792x1024 (landscape), 1024x1792 (portrait)
   - Quality: standard or HD
   - Style: vivid (dramatic/artistic) or natural (realistic)

2. **Stability AI** (Stable Diffusion XL)
   - Customizable parameters (CFG scale, steps)
   - Negative prompts for better control
   - Multiple model options

3. **Gemini Imagen** (Placeholder)
   - Integration ready when API becomes available

#### Tool Integration
The AI can automatically generate images when you ask:

```
User: "Create an image of a futuristic city at sunset"
AI: [Uses generate_image tool]
     ✅ Image Generated Successfully!
     [Displays generated image]
```

#### Configuration
Enable in sidebar:
- ☑️ Enable AI Image Generator
- Requires valid API keys (OPENAI_API_KEY for DALL-E, STABILITY_API_KEY for Stability AI)

### 4. 👁️ Vision Model Support

#### Supported Models
- **GPT-4V / GPT-4o** (OpenAI) - Vision-capable models
- **Gemini Pro Vision** (Google) - Multimodal understanding

#### Features
- Automatic detection of vision-capable models
- Proper image formatting for each provider
- Multiple images per message
- Detailed image analysis and understanding

#### Usage Example
```python
# Upload an image of a chart
User: "What does this chart show?"
AI: [Analyzes the uploaded image using GPT-4V]
    "This chart shows a bar graph depicting..."
```

### 5. 🔍 Image Extraction from Search

#### Tavily Search Integration
- Automatically downloads and caches images from search results
- Displays images inline with search results
- Limits to 3 images per search to avoid clutter
- Images saved to `uploads/search_images/`

#### Example
```
User: "Search for images of the Eiffel Tower"
AI: [Performs Tavily search with images enabled]

    📝 Summary: The Eiffel Tower is...
    
    🖼️ Related Images (3):
    [Image 1 displayed]
    [Image 2 displayed]
    [Image 3 displayed]
    
    🔍 Search Results:
    1. Wikipedia: Eiffel Tower...
```

### 6. 🖼️ Image Gallery

#### Access
- Click 🖼️ icon in sidebar
- View all uploaded, generated, and search-cached images

#### Features
- **Tabs**: All Images, Uploaded, Generated, From Search
- **Sorting**: Newest First, Oldest First, Largest, Smallest
- **Actions per image**:
  - View full size (expandable)
  - Download
  - Delete
- **Grid layout**: 3 columns for optimal viewing
- **Metadata display**: Dimensions, size, date

## Architecture

### Core Components

#### 1. Image Handler (`backend/core/image_handler.py`)
Main image processing and management system:

```python
from backend.core.image_handler import image_handler

# Save uploaded image
result = image_handler.save_uploaded_image(
    file_data=bytes,
    filename="image.png",
    user_id=user_id,
    metadata={'source': 'upload'}
)

# Save from URL (for search results)
result = image_handler.save_from_url(
    url="https://example.com/image.jpg",
    user_id=user_id,
    source='search'
)

# Save from clipboard
result = image_handler.save_from_clipboard(
    clipboard_data=base64_string,
    user_id=user_id
)

# List user's images
images = image_handler.list_user_images(
    user_id=user_id,
    source='all',  # or 'upload', 'generated', 'search'
    limit=50
)
```

**Key Methods**:
- `validate_image()` - Validates format, size, dimensions
- `process_image()` - Resizes, optimizes, converts format
- `create_thumbnail()` - Generates thumbnails
- `get_image_base64()` - Encodes for API transmission
- `delete_image()` - Removes image and thumbnail

#### 2. Image Generator (`backend/tools/image_generator.py`)
AI image generation integration:

```python
from backend.tools.image_generator import image_generator

# Generate with DALL-E
result = await image_generator.generate_dalle(
    prompt="A serene mountain landscape",
    user_id=user_id,
    model="dall-e-3",
    size="1024x1024",
    quality="hd",
    style="vivid"
)

# Generate with Stability AI
result = await image_generator.generate_stability(
    prompt="Cyberpunk cityscape",
    user_id=user_id,
    model="stable-diffusion-xl-1024-v1-0",
    width=1024,
    height=1024,
    cfg_scale=7.0,
    steps=30
)
```

**Tool Definition** (`IMAGE_GENERATION_TOOLS`):
- Automatically integrated with LLM function calling
- AI can invoke image generation based on user requests
- Results include path, metadata, and display-ready markdown

#### 3. Vision Model Integration (`backend/core/chat_manager.py`)
Handles multimodal messages:

```python
# Automatically formats images for vision models
response = await chat_manager.send_message(
    user_message="What's in this image?",
    provider="openai",
    model="gpt-4-vision-preview",
    images=[{
        'type': 'image',
        'data': base64_encoded_image,
        'filename': 'photo.jpg',
        'format': 'jpeg',
        'dimensions': (1024, 768)
    }]
)
```

**Format Handling**:
- **OpenAI**: Converts to `image_url` format with data URLs
- **Gemini**: Uses `inline_data` with MIME types
- **Fallback**: Adds text note if model doesn't support vision

#### 4. Enhanced Search (`backend/tools/tavily_search.py`)
Extended to include image extraction:

```python
# Search with images
result = tavily_tool.search(
    query="latest AI developments",
    max_results=5,
    include_images=True  # New parameter
)
```

**Image Processing**:
1. Receives image URLs from Tavily API
2. Downloads and validates images
3. Caches in `uploads/search_images/`
4. Returns markdown with image references
5. Chat UI automatically displays images

#### 5. Image Gallery (`frontend/streamlit/components/image_gallery.py`)
Rich UI for image management:

```python
from frontend.streamlit.components.image_gallery import ImageGalleryUI

# Render full gallery
ImageGalleryUI.render()

# Compact selector (for use in other components)
selected_path = ImageGalleryUI.render_compact_selector(
    user_id=user_id,
    key_prefix="my_selector"
)
```

**Features**:
- Tabbed interface (All, Uploaded, Generated, Search)
- Grid layout with 3 columns
- Image cards with preview and metadata
- Actions: View, Download, Delete
- Sorting and filtering

### Directory Structure

```
uploads/
├── images/                    # Uploaded images
│   └── {user_id}_{name}_{timestamp}_{hash}.{ext}
├── generated_images/          # AI-generated images
│   └── {user_id}_{provider}_{timestamp}_{hash}.png
└── search_images/             # Images from search results
    └── {user_id}_{timestamp}_{hash}.{ext}
```

### Database Considerations

**Current**: Images are stored as files, not in database
**Metadata**: Stored in file system (filenames, timestamps)
**Future Enhancement**: Add `images` table for better tracking:

```sql
CREATE TABLE images (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    filename VARCHAR(255),
    file_path VARCHAR(500),
    source VARCHAR(50),  -- 'upload', 'generated', 'search'
    provider VARCHAR(50),  -- 'dalle', 'stability', NULL
    prompt TEXT,  -- For generated images
    metadata JSON,
    created_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

## Configuration

### Environment Variables

Add to `.env`:

```bash
# OpenAI (for DALL-E and GPT-4V)
OPENAI_API_KEY=sk-...

# Stability AI (optional)
STABILITY_API_KEY=sk-...

# Tavily Search (already configured, now includes images)
TAVILY_API_KEY=tvly-...
```

### Settings

In `backend/config/settings.py`:

```python
class Settings:
    # Image handler settings
    max_image_size: int = 10 * 1024 * 1024  # 10 MB
    max_image_dimension: int = 4096
    
    # Supported formats
    supported_image_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg']
```

## Usage Guide

### For Users

#### Uploading Images
1. Navigate to chat interface
2. Scroll to "🖼️ Image Attachments" section
3. Click "Upload images" or drag & drop
4. Select one or more images
5. See previews appear
6. Type your question about the images
7. Send message

#### Pasting from Clipboard
1. Copy an image (screenshot, browser, etc.)
2. Focus on chat input
3. Press Ctrl+V (or Cmd+V on Mac)
4. Image is automatically attached
5. Proceed as with uploaded images

#### Generating Images
1. Enable "AI Image Generator" in sidebar
2. Ask the AI to create an image:
   - "Generate an image of..."
   - "Create a picture showing..."
   - "I need an illustration of..."
3. AI automatically calls generation tool
4. Image appears in chat

#### Viewing Image Gallery
1. Click 🖼️ icon in sidebar
2. Browse tabs: All, Uploaded, Generated, Search
3. Sort by date, size, etc.
4. View full-size by clicking expand
5. Download or delete as needed

### For Developers

#### Adding a New Image Source

```python
# In image_handler.py
def save_from_custom_source(
    self,
    source_data: dict,
    user_id: int
) -> Dict[str, Any]:
    """Save image from custom source"""
    # Validate
    is_valid, error = self.validate_image(source_data['bytes'])
    if not is_valid:
        return {'success': False, 'error': error}
    
    # Process
    filename = self._generate_unique_filename(source_data['name'], user_id)
    save_path = self.UPLOAD_DIR / filename
    
    # Save
    with open(save_path, 'wb') as f:
        f.write(source_data['bytes'])
    
    return {
        'success': True,
        'file_path': str(save_path),
        # ... other metadata
    }
```

#### Adding a New Image Generation Provider

```python
# In image_generator.py
async def generate_custom_provider(
    self,
    prompt: str,
    user_id: int,
    **kwargs
) -> Dict[str, Any]:
    """Generate image using custom provider"""
    try:
        # Call provider API
        response = await custom_provider_api.generate(
            prompt=prompt,
            **kwargs
        )
        
        # Save image
        image_bytes = response.image_data
        filename = f"{user_id}_custom_{timestamp}_{hash}.png"
        filepath = self.output_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        return {
            'success': True,
            'file_path': str(filepath),
            'relative_path': str(filepath.relative_to(Path.cwd())),
            'provider': 'custom',
            # ... metadata
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}

# Add to IMAGE_GENERATION_TOOLS
CUSTOM_GENERATION_TOOL = {
    "type": "function",
    "function": {
        "name": "generate_image_custom",
        "description": "Generate image using custom provider",
        "parameters": {
            # ... define parameters
        }
    }
}
```

#### Extending Vision Model Support

```python
# In chat_manager.py
# Add new provider format in send_message()

elif provider.lower() == "anthropic":
    # Claude with vision format
    content_parts = [{"type": "text", "text": messages[i]["content"]}]
    
    for img in images:
        content_parts.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": f"image/{img['format']}",
                "data": img['data']
            }
        })
    
    messages[i]["content"] = content_parts
```

## API Reference

### ImageHandler

#### Methods

##### `validate_image(file_data: bytes, filename: str = None) -> Tuple[bool, Optional[str]]`
Validates image file.

**Returns**: `(is_valid, error_message)`

##### `process_image(file_data: bytes, max_size: Tuple[int, int] = None, format: str = 'PNG', quality: int = 95) -> bytes`
Process and optimize image.

**Returns**: Processed image bytes

##### `save_uploaded_image(file_data: bytes, filename: str, user_id: int, metadata: Dict = None) -> Dict[str, Any]`
Save uploaded image.

**Returns**: Dictionary with `success`, `file_path`, metadata

##### `save_from_clipboard(clipboard_data: str, user_id: int) -> Dict[str, Any]`
Save image from clipboard base64 data.

**Returns**: Dictionary with `success`, `file_path`, metadata

##### `save_from_url(url: str, user_id: int, source: str = 'web') -> Dict[str, Any]`
Download and save image from URL.

**Returns**: Dictionary with `success`, `file_path`, metadata

##### `list_user_images(user_id: int, source: str = 'all', limit: int = 50) -> List[Dict]`
List images for a user.

**Returns**: List of image info dictionaries

##### `delete_image(image_path: str) -> bool`
Delete an image.

**Returns**: True if successful

### ImageGenerator

#### Methods

##### `async generate_dalle(prompt: str, user_id: int, model: str = "dall-e-3", size: str = "1024x1024", quality: str = "standard", style: str = "vivid") -> Dict[str, Any]`
Generate image using DALL-E.

**Returns**: Dictionary with `success`, `file_path`, `revised_prompt`, metadata

##### `async generate_stability(prompt: str, user_id: int, model: str = "stable-diffusion-xl-1024-v1-0", negative_prompt: str = None, width: int = 1024, height: int = 1024, cfg_scale: float = 7.0, steps: int = 30) -> Dict[str, Any]`
Generate image using Stability AI.

**Returns**: Dictionary with `success`, `file_path`, metadata

##### `generate(prompt: str, user_id: int, provider: str = "dalle", **kwargs) -> Dict[str, Any]`
Generate image (sync wrapper).

**Returns**: Dictionary with generation result

## Troubleshooting

### Common Issues

#### 1. Images Not Displaying
**Problem**: Images uploaded but not showing in chat

**Solutions**:
- Check file path is correct
- Verify file exists in `uploads/` directory
- Check console for errors
- Ensure `display_message_with_images()` is called

#### 2. Image Generation Fails
**Problem**: DALL-E or Stability AI returns error

**Solutions**:
- Verify API keys in `.env`
- Check API quota/credits
- Review prompt for policy violations
- Try different model or parameters

#### 3. Vision Models Not Working
**Problem**: Model doesn't understand images

**Solutions**:
- Ensure using vision-capable model (GPT-4V, GPT-4o)
- Check image format is supported
- Verify base64 encoding is correct
- Check model info has `supports_vision: true`

#### 4. Clipboard Paste Not Working
**Problem**: Ctrl+V doesn't attach images

**Solutions**:
- Currently requires browser with clipboard API support
- Try manual upload instead
- Check browser permissions
- Verify clipboard contains image data

#### 5. Search Images Not Appearing
**Problem**: Tavily search doesn't show images

**Solutions**:
- Check `include_images=True` is set
- Verify Tavily API returns images
- Check network connectivity for downloads
- Review download error messages

### Debug Mode

Enable debug logging in `.env`:

```bash
DEBUG_MODE=true
```

This will print:
- API request details
- Image processing steps
- Tool execution logs
- Error stack traces

## Performance Considerations

### Optimization Tips

1. **Image Size**: 
   - Compress images before upload
   - Use appropriate dimensions for use case
   - Consider WebP for better compression

2. **Caching**:
   - Search images are cached to avoid re-downloads
   - Use thumbnails for gallery views
   - Implement lazy loading for large galleries

3. **API Costs**:
   - DALL-E 3 HD: $0.080 per image
   - DALL-E 3 Standard: $0.040 per image
   - Stable Diffusion XL: ~$0.002 per image
   - Vision models: Higher token costs due to image processing

4. **Storage**:
   - Implement cleanup for old search cache
   - Set retention policies for generated images
   - Use cloud storage for production (S3, GCS)

## Future Enhancements

### Planned Features

1. **Advanced Editing**:
   - Crop, rotate, filters in gallery
   - Image-to-image generation
   - Inpainting and outpainting

2. **Better Organization**:
   - Albums/collections
   - Tags and labels
   - Search by content (visual search)

3. **Batch Operations**:
   - Multi-select in gallery
   - Bulk download/delete
   - Batch generation

4. **Enhanced Integration**:
   - Drag images directly from gallery to chat
   - Image comparison tool
   - Side-by-side view

5. **Collaboration**:
   - Share galleries
   - Collaborative image annotation
   - Comments on images

## License

This system is part of the Mathanoshto AI project. See main LICENSE file for details.

## Support

For issues or questions:
- GitHub Issues: [Your repo URL]
- Documentation: `docs/`
- Email: [Your email]

---

**Last Updated**: November 12, 2025
**Version**: 1.0.0
**Status**: Production Ready ✅

