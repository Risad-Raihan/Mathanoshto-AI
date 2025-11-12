"""
Link Preview Extractor
Extracts preview images, favicons, and metadata from URLs for rich search results
"""
import requests
from bs4 import BeautifulSoup
from typing import Optional, Dict
from urllib.parse import urljoin, urlparse
import mimetypes


class LinkPreviewExtractor:
    """Extract preview images and metadata from URLs"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; PreviewBot/1.0)'
        }
        self.timeout = 5
    
    def extract_preview(self, url: str) -> Dict[str, Optional[str]]:
        """
        Extract preview metadata from a URL
        
        Args:
            url: URL to extract preview from
            
        Returns:
            Dict with 'image', 'favicon', 'title', 'description'
        """
        preview = {
            'image': None,
            'favicon': None,
            'title': None,
            'description': None,
            'site_name': None
        }
        
        try:
            # Fetch the page
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract Open Graph image (preferred)
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                preview['image'] = self._resolve_url(url, og_image['content'])
            
            # Fallback: Twitter Card image
            if not preview['image']:
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    preview['image'] = self._resolve_url(url, twitter_image['content'])
            
            # Fallback: Look for first large image
            if not preview['image']:
                preview['image'] = self._find_first_large_image(soup, url)
            
            # Extract favicon
            favicon = soup.find('link', rel='icon') or soup.find('link', rel='shortcut icon')
            if favicon and favicon.get('href'):
                preview['favicon'] = self._resolve_url(url, favicon['href'])
            else:
                # Default favicon location
                parsed = urlparse(url)
                preview['favicon'] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
            
            # Extract title
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                preview['title'] = og_title['content']
            elif soup.title:
                preview['title'] = soup.title.string
            
            # Extract description
            og_desc = soup.find('meta', property='og:description')
            if og_desc and og_desc.get('content'):
                preview['description'] = og_desc['content']
            else:
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    preview['description'] = meta_desc['content']
            
            # Extract site name
            og_site = soup.find('meta', property='og:site_name')
            if og_site and og_site.get('content'):
                preview['site_name'] = og_site['content']
            else:
                parsed = urlparse(url)
                preview['site_name'] = parsed.netloc
            
        except Exception as e:
            print(f"Failed to extract preview from {url}: {e}")
            # Return partial data with favicon at least
            parsed = urlparse(url)
            preview['favicon'] = f"{parsed.scheme}://{parsed.netloc}/favicon.ico"
            preview['site_name'] = parsed.netloc
        
        return preview
    
    def _resolve_url(self, base_url: str, relative_url: str) -> str:
        """Resolve relative URL to absolute"""
        if relative_url.startswith('http'):
            return relative_url
        return urljoin(base_url, relative_url)
    
    def _find_first_large_image(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Find first reasonably large image in the page"""
        for img in soup.find_all('img'):
            src = img.get('src')
            if not src:
                continue
            
            # Skip small images (icons, logos, etc.)
            width = img.get('width')
            height = img.get('height')
            
            if width and height:
                try:
                    w = int(width)
                    h = int(height)
                    if w < 200 or h < 200:
                        continue
                except:
                    pass
            
            # Check if it's an image URL (not data URI, not SVG)
            src_lower = src.lower()
            if src_lower.startswith('data:'):
                continue
            if src_lower.endswith('.svg'):
                continue
            
            return self._resolve_url(base_url, src)
        
        return None
    
    def is_valid_image_url(self, url: str) -> bool:
        """Check if URL is likely an image"""
        try:
            # Check extension
            path = urlparse(url).path.lower()
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            if any(path.endswith(ext) for ext in image_extensions):
                return True
            
            # Check MIME type (lightweight HEAD request)
            response = requests.head(url, headers=self.headers, timeout=3, allow_redirects=True)
            content_type = response.headers.get('content-type', '').lower()
            return content_type.startswith('image/')
        except:
            return False


# Global instance
link_preview_extractor = LinkPreviewExtractor()

