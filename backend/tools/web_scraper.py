"""
Web Scraper Tool - Extract content from URLs with smart parsing
Supports: Basic scraping, JavaScript rendering, content extraction, screenshots
"""
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, urljoin
import time
from datetime import datetime
import hashlib
import json
from pathlib import Path


class WebScraper:
    """
    Comprehensive web scraper with multiple extraction methods
    """
    
    def __init__(self, user_agent: str = None):
        """Initialize web scraper"""
        self.user_agent = user_agent or (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.user_agent})
        
        # Rate limiting
        self.last_request_time = {}
        self.min_delay = 1.0  # Minimum delay between requests to same domain
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc
    
    def _respect_rate_limit(self, url: str):
        """Implement rate limiting per domain"""
        domain = self._get_domain(url)
        
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.min_delay:
                time.sleep(self.min_delay - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    def check_robots_txt(self, url: str, user_agent: str = "*") -> bool:
        """Check if URL is allowed by robots.txt"""
        try:
            from reppy.robots import Robots
            
            parsed = urlparse(url)
            robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
            
            robots = Robots.fetch(robots_url)
            return robots.allowed(url, user_agent)
        
        except Exception as e:
            # If we can't fetch robots.txt, assume it's allowed
            print(f"Could not check robots.txt: {e}")
            return True
    
    def scrape_url(
        self,
        url: str,
        extract_content: bool = True,
        extract_metadata: bool = True,
        respect_robots: bool = True,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Scrape a URL and extract content
        
        Args:
            url: URL to scrape
            extract_content: Extract main content using readability
            extract_metadata: Extract metadata (title, description, etc.)
            respect_robots: Check robots.txt before scraping
            timeout: Request timeout in seconds
        
        Returns:
            Dictionary with scraped data
        """
        result = {
            'success': False,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': None,
            'metadata': {},
            'error': None
        }
        
        try:
            # Check robots.txt
            if respect_robots and not self.check_robots_txt(url):
                result['error'] = 'Blocked by robots.txt'
                return result
            
            # Rate limiting
            self._respect_rate_limit(url)
            
            # Fetch the page
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('content-type', '')
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Extract metadata
            if extract_metadata:
                result['metadata'] = self._extract_metadata(soup, url)
            
            # Extract main content
            if extract_content:
                result['content'] = self._extract_content(response.content, url)
            else:
                # Just get all text
                result['content'] = soup.get_text(separator='\n', strip=True)
            
            # Get links
            result['links'] = self._extract_links(soup, url)
            
            # Calculate content hash for change detection
            result['content_hash'] = hashlib.md5(
                result['content'].encode('utf-8')
            ).hexdigest()
            
            result['success'] = True
            
        except requests.exceptions.Timeout:
            result['error'] = f'Request timeout after {timeout} seconds'
        except requests.exceptions.RequestException as e:
            result['error'] = f'Request failed: {str(e)}'
        except Exception as e:
            result['error'] = f'Scraping failed: {str(e)}'
        
        return result
    
    def _extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract metadata from HTML"""
        metadata = {
            'url': url,
            'domain': self._get_domain(url)
        }
        
        # Title
        title_tag = soup.find('title')
        metadata['title'] = title_tag.string.strip() if title_tag else None
        
        # Meta tags
        meta_tags = {
            'description': soup.find('meta', attrs={'name': 'description'}),
            'keywords': soup.find('meta', attrs={'name': 'keywords'}),
            'author': soup.find('meta', attrs={'name': 'author'}),
            'og:title': soup.find('meta', attrs={'property': 'og:title'}),
            'og:description': soup.find('meta', attrs={'property': 'og:description'}),
            'og:image': soup.find('meta', attrs={'property': 'og:image'}),
            'twitter:title': soup.find('meta', attrs={'name': 'twitter:title'}),
            'twitter:description': soup.find('meta', attrs={'name': 'twitter:description'}),
        }
        
        for key, tag in meta_tags.items():
            if tag:
                content = tag.get('content', '') or tag.get('value', '')
                if content:
                    metadata[key] = content.strip()
        
        # Canonical URL
        canonical = soup.find('link', attrs={'rel': 'canonical'})
        if canonical:
            metadata['canonical_url'] = canonical.get('href')
        
        # Language
        html_tag = soup.find('html')
        if html_tag:
            metadata['language'] = html_tag.get('lang', '')
        
        return metadata
    
    def _extract_content(self, html_content: bytes, url: str) -> str:
        """Extract main article content using readability"""
        try:
            from readability import Document
            
            # Decode bytes to string for readability
            if isinstance(html_content, bytes):
                html_content = html_content.decode('utf-8', errors='ignore')
            
            doc = Document(html_content)
            
            # Get the main content
            content_html = doc.summary()
            
            # Convert to plain text
            soup = BeautifulSoup(content_html, 'lxml')
            text = soup.get_text(separator='\n', strip=True)
            
            return text
        
        except Exception as e:
            print(f"Readability extraction failed: {e}")
            # Fallback to BeautifulSoup
            soup = BeautifulSoup(html_content, 'lxml')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()
            
            # Get text
            text = soup.get_text(separator='\n', strip=True)
            return text
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """Extract all links from the page"""
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            
            # Convert relative URLs to absolute
            absolute_url = urljoin(base_url, href)
            
            links.append({
                'url': absolute_url,
                'text': text[:100] if text else ''  # Limit text length
            })
        
        return links[:50]  # Limit number of links
    
    def scrape_with_javascript(
        self,
        url: str,
        wait_for: Optional[str] = None,
        screenshot: bool = False,
        timeout: int = 30000
    ) -> Dict[str, Any]:
        """
        Scrape a URL with JavaScript rendering using Playwright
        
        Args:
            url: URL to scrape
            wait_for: CSS selector to wait for before extracting content
            screenshot: Whether to take a screenshot
            timeout: Timeout in milliseconds
        
        Returns:
            Dictionary with scraped data
        """
        result = {
            'success': False,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': None,
            'metadata': {},
            'screenshot_path': None,
            'error': None
        }
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Navigate to URL
                page.goto(url, timeout=timeout, wait_until='networkidle')
                
                # Wait for specific element if specified
                if wait_for:
                    page.wait_for_selector(wait_for, timeout=timeout)
                
                # Get page content
                content = page.content()
                soup = BeautifulSoup(content, 'lxml')
                
                # Extract metadata
                result['metadata'] = self._extract_metadata(soup, url)
                
                # Extract main content
                result['content'] = self._extract_content(content.encode('utf-8'), url)
                
                # Take screenshot if requested
                if screenshot:
                    screenshot_dir = Path('uploads') / 'screenshots'
                    screenshot_dir.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    domain = self._get_domain(url).replace('.', '_')
                    screenshot_path = screenshot_dir / f"{domain}_{timestamp}.png"
                    
                    page.screenshot(path=str(screenshot_path), full_page=True)
                    result['screenshot_path'] = str(screenshot_path)
                
                browser.close()
                
                result['success'] = True
        
        except Exception as e:
            result['error'] = f'JavaScript rendering failed: {str(e)}'
        
        return result
    
    def convert_to_markdown(self, html_content: str) -> str:
        """Convert HTML to Markdown"""
        try:
            import html2text
            
            h = html2text.HTML2Text()
            h.ignore_links = False
            h.ignore_images = False
            h.ignore_emphasis = False
            h.body_width = 0  # Don't wrap text
            
            markdown = h.handle(html_content)
            return markdown
        
        except Exception as e:
            print(f"HTML to Markdown conversion failed: {e}")
            return html_content


class URLMonitor:
    """Monitor URLs for changes"""
    
    def __init__(self, storage_path: str = "url_monitors.json"):
        """Initialize URL monitor"""
        self.storage_path = Path(storage_path)
        self.monitors = self._load_monitors()
        self.scraper = WebScraper()
    
    def _load_monitors(self) -> Dict[str, Any]:
        """Load monitors from storage"""
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_monitors(self):
        """Save monitors to storage"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.monitors, f, indent=2)
    
    def add_monitor(
        self,
        url: str,
        user_id: int,
        check_interval: int = 3600,
        notify_on_change: bool = True
    ) -> str:
        """
        Add a URL to monitor
        
        Args:
            url: URL to monitor
            user_id: User ID who created the monitor
            check_interval: Check interval in seconds
            notify_on_change: Whether to notify on changes
        
        Returns:
            Monitor ID
        """
        # Initial scrape
        result = self.scraper.scrape_url(url)
        
        if not result['success']:
            raise Exception(f"Failed to scrape URL: {result['error']}")
        
        # Create monitor ID
        monitor_id = hashlib.md5(f"{url}_{user_id}".encode()).hexdigest()[:16]
        
        self.monitors[monitor_id] = {
            'id': monitor_id,
            'url': url,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'last_checked': datetime.now().isoformat(),
            'check_interval': check_interval,
            'notify_on_change': notify_on_change,
            'last_content_hash': result['content_hash'],
            'last_status': 'active',
            'change_count': 0
        }
        
        self._save_monitors()
        return monitor_id
    
    def check_monitor(self, monitor_id: str) -> Dict[str, Any]:
        """Check a monitor for changes"""
        if monitor_id not in self.monitors:
            return {'success': False, 'error': 'Monitor not found'}
        
        monitor = self.monitors[monitor_id]
        
        # Scrape URL
        result = self.scraper.scrape_url(monitor['url'])
        
        if not result['success']:
            monitor['last_status'] = 'error'
            monitor['last_error'] = result['error']
            self._save_monitors()
            return {'success': False, 'changed': False, 'error': result['error']}
        
        # Check for changes
        changed = result['content_hash'] != monitor['last_content_hash']
        
        # Update monitor
        monitor['last_checked'] = datetime.now().isoformat()
        monitor['last_status'] = 'active'
        
        if changed:
            monitor['change_count'] += 1
            monitor['last_content_hash'] = result['content_hash']
            monitor['last_change_at'] = datetime.now().isoformat()
        
        self._save_monitors()
        
        return {
            'success': True,
            'changed': changed,
            'monitor': monitor,
            'content': result['content'] if changed else None
        }
    
    def get_user_monitors(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all monitors for a user"""
        return [
            monitor for monitor in self.monitors.values()
            if monitor['user_id'] == user_id
        ]
    
    def remove_monitor(self, monitor_id: str) -> bool:
        """Remove a monitor"""
        if monitor_id in self.monitors:
            del self.monitors[monitor_id]
            self._save_monitors()
            return True
        return False


# Global instances
web_scraper = WebScraper()
url_monitor = URLMonitor()

