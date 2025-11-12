# Search Results with Image Previews - User Guide

## What's New? 🎉

Your Tavily search results now include **rich image previews** for every search result! This makes your chat interface much more visual and engaging.

## Features

### 1. **Tavily Images** 🖼️
- If Tavily returns images for your query, they're displayed at the top
- Up to 3 high-quality images shown
- Images are downloaded and cached locally
- Shows image size and format

### 2. **Link Preview Cards** 📸
- **Every search result** gets a preview image extracted from the website
- Uses Open Graph images (the same images you see when sharing links on social media)
- Falls back to Twitter Card images
- Finds the first large image if no social media metadata exists

### 3. **Better Formatting** ✨
- Clean markdown headers for each result
- Preview images display inline with results
- Site names shown under preview images
- Clickable URLs

## How It Works

When you search with Tavily, the system now:

1. **Gets Tavily's images** (if available for the query)
2. **Extracts preview images** from each result URL by:
   - Fetching the webpage
   - Looking for Open Graph `og:image` tags
   - Checking Twitter Card images
   - Finding large images on the page
3. **Downloads and caches** all images locally
4. **Displays them beautifully** in your chat

## Example Results

### Before (Text Only):
```
🔍 Search Results for 'best smartphones 2024':

1. Top 10 Smartphones of 2024
   URL: https://example.com/smartphones
   The latest smartphones feature...
```

### After (With Images):
```
📝 Summary: The best smartphones of 2024 include...

🖼️ Related Images (3):
[Image 1 displayed]
[Image 2 displayed]
[Image 3 displayed]

📑 Search Results for 'best smartphones 2024':

### 1. Top 10 Smartphones of 2024
🔗 https://example.com/smartphones

[Preview image of smartphone displayed]
*example.com preview*

The latest smartphones feature...

### 2. Smartphone Buyer's Guide
🔗 https://techsite.com/guide

[Preview image displayed]
*techsite.com preview*

When choosing a smartphone...
```

## Usage Tips

### Get Better Images
1. **Use image-friendly queries**:
   - ✅ "Show me the latest iPhone design"
   - ✅ "Best gaming laptops with images"
   - ✅ "Modern office interior ideas"
   - ❌ "What is quantum computing" (might not have images)

2. **Be specific**: More specific queries = better images
   - ✅ "Tesla Model 3 interior photos"
   - ❌ "car information"

### Troubleshooting

#### No images showing?
- Check that Web Search is enabled in sidebar
- Some websites block image extraction (privacy/security)
- Text-heavy sites might not have preview images
- Check console/terminal for error messages

#### Images loading slowly?
- First time fetching from a site takes longer (needs to download)
- Subsequent searches use cached images (much faster)
- Preview extraction adds 1-2 seconds per result
- You can disable by modifying `extract_previews=False` in code

#### Too many images?
- System limits to 3 Tavily images
- Shows 1 preview per search result
- Adjust limits in `tavily_search.py` if needed

## Performance

### Speed:
- Tavily images: ~1-2 seconds to download 3 images
- Link previews: ~1-2 seconds per website
- Total search with 5 results + images: ~10-15 seconds

### Storage:
- Images cached in `uploads/search_images/`
- Typical image: 50-500 KB
- Old images not auto-deleted (implement cleanup if needed)

### API Costs:
- Tavily search: ~$0.001 per search (no extra cost for images)
- No additional API calls for link preview extraction

## Configuration

### Enable/Disable Features

In your search, you can control:

1. **Tavily Images**: Already enabled by default
2. **Link Previews**: Enabled by default, can disable in code

To disable link previews, modify `backend/tools/tavily_search.py`:

```python
def search(self, query: str, ..., extract_previews: bool = False):  # Change to False
```

### Adjust Image Limits

In `tavily_search.py`:

```python
# Line ~104: Change number of Tavily images (default: 3)
for idx, img_url in enumerate(images[:5], 1):  # Try up to 5
    if successful_images >= 3:  # But only show 3 (change this)
        break

# Preview extraction happens per result (1 per result)
# To disable preview for specific result, add conditions
```

## Technical Details

### How Preview Extraction Works:

```python
1. Fetch webpage HTML
2. Parse with BeautifulSoup
3. Check for Open Graph tags:
   - <meta property="og:image" content="...">
4. Fallback to Twitter Cards:
   - <meta name="twitter:image" content="...">
5. Fallback to first large image:
   - Find <img> tags with width/height > 200px
6. Download image and cache locally
7. Return path for display
```

### Supported Image Formats:
- PNG, JPG, JPEG, GIF, WEBP, BMP
- SVG images are skipped (not rendered well)
- Data URIs are skipped (too large)

### Caching:
- Images saved to: `uploads/search_images/`
- Filename format: `{user_id}_{timestamp}_{hash}.{ext}`
- No automatic cleanup (implement if needed)

## Future Enhancements

Potential improvements:
- [ ] Cache preview metadata (avoid re-fetching)
- [ ] Thumbnail generation for faster loading
- [ ] Lazy loading for images
- [ ] Image carousel view
- [ ] Filter by image availability
- [ ] Image search mode (images only)
- [ ] OCR on preview images
- [ ] Similar image finder

## Need Help?

**Issue**: Images not displaying
- Check file paths in terminal logs
- Verify images downloaded to `uploads/search_images/`
- Check Streamlit console for errors

**Issue**: Preview extraction slow
- Normal for first-time fetches
- Consider disabling for text-only searches
- Implement async fetching (future enhancement)

**Issue**: Images look stretched/broken
- Check original image quality
- Some websites serve low-res preview images
- Try different search query

## Testing

Try these searches to see image previews:

1. **Product searches**: "latest iPhone", "PlayStation 5", "Tesla cars"
2. **Visual topics**: "beautiful landscapes", "modern architecture", "recipe chocolate cake"
3. **News/Events**: "CES 2024", "Olympics highlights", "tech announcements"
4. **Guides**: "best hiking trails", "coding tutorials", "travel destinations"

---

**Enjoy your enhanced visual search experience!** 🎨🔍


