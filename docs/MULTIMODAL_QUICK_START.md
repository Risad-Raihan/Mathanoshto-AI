# Multimodal Image System - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Step 1: Install Dependencies (if needed)

```bash
# All dependencies should already be in requirements.txt
# If you need to reinstall:
pip install -r requirements.txt
```

### Step 2: Configure API Keys

Edit your `.env` file:

```bash
# Required for vision models and image generation
OPENAI_API_KEY=sk-...  # For DALL-E and GPT-4V

# Optional: For Stability AI
STABILITY_API_KEY=sk-...

# Already configured (now includes images)
TAVILY_API_KEY=tvly-...
```

### Step 3: Run the Application

```bash
streamlit run frontend/streamlit/app.py
```

### Step 4: Start Using Multimodal Features!

## ✨ Quick Feature Tour

### 1. Upload Images (30 seconds)
1. Open chat interface
2. Scroll down to "🖼️ Image Attachments"
3. Click "Upload images" and select files
4. Ask: "What's in these images?"
5. Send! ✅

### 2. Generate Images (1 minute)
1. In sidebar, enable ☑️ "Enable AI Image Generator"
2. Ask: "Generate an image of a sunset over mountains"
3. AI automatically creates and displays the image
4. Download it from the chat! 🎨

### 3. Analyze Images with Vision Models (1 minute)
1. In sidebar, select a vision model:
   - `gpt-4-vision-preview`
   - `gpt-4o`
   - `gemini-1.5-pro`
2. Upload an image (chart, photo, diagram)
3. Ask: "Explain what this shows"
4. Get detailed AI analysis! 👁️

### 4. View Image Gallery (30 seconds)
1. Click 🖼️ icon in sidebar (top row, 4th button)
2. Browse your images in tabs
3. View, download, or delete images
4. Sort by date, size, etc. 📁

### 5. Search with Images (1 minute)
1. Enable ☑️ "Enable Web Search" in sidebar
2. Ask: "Search for images of the Eiffel Tower"
3. Get results with relevant images
4. Images automatically downloaded and displayed 🔍

## 📝 Common Use Cases

### Use Case 1: Code Review from Screenshot
```
User: [Uploads screenshot of code]
      "What's wrong with this code?"

AI: [Analyzes using GPT-4V]
    "I see several issues:
    1. Line 15: Missing semicolon
    2. Line 23: Variable 'data' is undefined
    3. ..."
```

### Use Case 2: Create Marketing Visual
```
User: "Generate a professional banner image for a tech startup. 
       Include elements suggesting innovation and growth."

AI: [Uses DALL-E 3]
    ✅ Image Generated Successfully!
    [Displays 1792×1024 banner image]
```

### Use Case 3: Data Visualization Analysis
```
User: [Uploads chart image]
      "Summarize the trends in this chart"

AI: [Analyzes with vision model]
    "This chart shows:
    - Overall upward trend from Q1 to Q4
    - Peak in Q3 at approximately 85%
    - Notable dip in Q2..."
```

### Use Case 4: Research with Visuals
```
User: "Search for the latest AI chip designs and show me images"

AI: [Tavily search with images]
    📝 Summary: Latest AI chips...
    
    🖼️ Related Images:
    [Image 1: NVIDIA H100]
    [Image 2: Google TPU v5]
    [Image 3: AMD MI300X]
```

## 🎯 Tips & Tricks

### Best Practices

#### For Image Upload
- ✅ Use clear, high-resolution images
- ✅ Compress very large images before upload (< 10 MB)
- ✅ Use PNG for screenshots, JPEG for photos
- ❌ Don't upload sensitive/private information

#### For Image Generation
- ✅ Be specific in prompts: "A cyberpunk cityscape at night with neon lights, raining, cinematic lighting"
- ✅ Use style keywords: "photorealistic", "oil painting", "minimalist", "3D render"
- ✅ Specify important details: colors, composition, mood
- ❌ Avoid vague prompts: "nice picture"

#### For Vision Analysis
- ✅ Ask specific questions about the image
- ✅ Use high-quality, well-lit images
- ✅ Crop to relevant area before upload
- ❌ Don't expect OCR of tiny text (though it can read some text)

### Pro Tips

1. **Batch Processing**: Upload multiple images at once for comparison
   ```
   User: [Uploads 3 product photos]
         "Compare these products and tell me which is best"
   ```

2. **Iterative Generation**: Refine AI-generated images
   ```
   User: "Make it more vibrant"
         "Add a sunset in the background"
         "Make it wider (1792×1024)"
   ```

3. **Combine Tools**: Use search + vision + generation
   ```
   User: "Search for modern office designs"
         [Reviews search images]
         "Generate a similar office design but with more plants"
   ```

4. **Save to Gallery**: All images auto-saved for later reference
   - Generated images → "Generated" tab
   - Uploads → "Uploaded" tab
   - Search results → "From Search" tab

## 🔧 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Paste image from clipboard | `Ctrl+V` (Win/Linux) / `Cmd+V` (Mac) |
| Send message | `Ctrl+Enter` |
| Open image gallery | Click 🖼️ in sidebar |
| Back to chat | `Esc` (when in gallery) |

## ⚙️ Configuration

### Sidebar Settings

**AI Image Generator** (Enable to allow AI to create images)
- Used with: "Generate an image of...", "Create a picture of..."
- Provider: DALL-E 3 (default) or Stability AI
- Cost: ~$0.04-0.08 per image

**Vision Models** (Select model)
- `gpt-4-vision-preview` - Best for detailed analysis
- `gpt-4o` - Fast, multimodal, good balance
- `gemini-1.5-pro` - Long context, good for complex images

### Advanced Settings

In `backend/core/image_handler.py`, you can adjust:

```python
# Maximum upload size (default: 10 MB)
MAX_UPLOAD_SIZE = 10 * 1024 * 1024

# Maximum dimension (default: 4096 pixels)
MAX_DIMENSION = 4096

# Supported formats
SUPPORTED_FORMATS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'}
```

## 🐛 Troubleshooting

### Issue: Images not uploading
**Solution**: Check file size (< 10 MB) and format (PNG, JPG, etc.)

### Issue: Vision model not understanding images
**Solution**: Ensure you selected a vision-capable model (gpt-4o, gpt-4-vision-preview)

### Issue: Image generation fails
**Solution**: Check API key is valid and has credits

### Issue: Search images not appearing
**Solution**: Enable "Web Search" tool in sidebar

## 📚 Learn More

- Full Documentation: [`docs/MULTIMODAL_IMAGE_SYSTEM.md`](MULTIMODAL_IMAGE_SYSTEM.md)
- API Reference: See "API Reference" section in main docs
- Architecture: See "Architecture" section in main docs

## 🎉 You're Ready!

Start experimenting with:
- 🖼️ Uploading and analyzing images
- 🎨 Generating custom visuals
- 👁️ Using vision AI for insights
- 🔍 Finding images through search

**Have fun building with multimodal AI!** 🚀

---

**Need Help?** Check the full documentation or open an issue on GitHub.

