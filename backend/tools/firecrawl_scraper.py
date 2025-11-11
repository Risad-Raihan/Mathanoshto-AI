"""
Firecrawl API Integration - Advanced web scraping service
Optional: Requires FIRECRAWL_API_KEY in environment
"""
import os
from typing import Dict, Any, Optional, List
from datetime import datetime


class FirecrawlScraper:
    """
    Firecrawl API wrapper for advanced web scraping
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Firecrawl scraper"""
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')
        self.client = None
        
        if self.api_key:
            try:
                from firecrawl import FirecrawlApp
                self.client = FirecrawlApp(api_key=self.api_key)
            except ImportError:
                print("Firecrawl library not installed. Install with: pip install firecrawl-py")
            except Exception as e:
                print(f"Failed to initialize Firecrawl: {e}")
    
    def is_available(self) -> bool:
        """Check if Firecrawl is available"""
        return self.client is not None
    
    def scrape_url(
        self,
        url: str,
        formats: List[str] = None,
        only_main_content: bool = True,
        include_html: bool = False,
        wait_for: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Scrape a URL using Firecrawl API
        
        Args:
            url: URL to scrape
            formats: List of formats to return ('markdown', 'html', 'links', 'screenshot')
            only_main_content: Extract only main content
            include_html: Include raw HTML
            wait_for: Milliseconds to wait for page load
        
        Returns:
            Dictionary with scraped data
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Firecrawl not available. Please set FIRECRAWL_API_KEY environment variable.'
            }
        
        result = {
            'success': False,
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'content': None,
            'metadata': {},
            'error': None
        }
        
        try:
            # Prepare scrape options
            params = {
                'formats': formats or ['markdown', 'links'],
                'onlyMainContent': only_main_content,
                'includeHtml': include_html
            }
            
            if wait_for:
                params['waitFor'] = wait_for
            
            # Scrape using Firecrawl
            response = self.client.scrape_url(url, params=params)
            
            if response.get('success'):
                result['success'] = True
                result['content'] = response.get('markdown', response.get('text', ''))
                result['html'] = response.get('html') if include_html else None
                result['links'] = response.get('links', [])
                result['metadata'] = response.get('metadata', {})
                result['screenshot_url'] = response.get('screenshot')
            else:
                result['error'] = response.get('error', 'Unknown error')
        
        except Exception as e:
            result['error'] = f'Firecrawl scraping failed: {str(e)}'
        
        return result
    
    def crawl_website(
        self,
        url: str,
        max_depth: int = 2,
        limit: int = 10,
        include_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Crawl an entire website
        
        Args:
            url: Base URL to crawl
            max_depth: Maximum depth to crawl
            limit: Maximum number of pages
            include_paths: URL patterns to include
            exclude_paths: URL patterns to exclude
        
        Returns:
            Dictionary with crawled data
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Firecrawl not available'
            }
        
        try:
            params = {
                'maxDepth': max_depth,
                'limit': limit
            }
            
            if include_paths:
                params['includePaths'] = include_paths
            if exclude_paths:
                params['excludePaths'] = exclude_paths
            
            response = self.client.crawl_url(url, params=params)
            
            return {
                'success': True,
                'pages': response.get('data', []),
                'total_pages': len(response.get('data', []))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Crawling failed: {str(e)}'
            }
    
    def map_website(self, url: str) -> Dict[str, Any]:
        """
        Get a map of all URLs on a website
        
        Args:
            url: Website URL to map
        
        Returns:
            Dictionary with site map
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Firecrawl not available'
            }
        
        try:
            response = self.client.map_url(url)
            
            return {
                'success': True,
                'links': response.get('links', []),
                'total_links': len(response.get('links', []))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f'Mapping failed: {str(e)}'
            }


# Global instance
firecrawl_scraper = FirecrawlScraper()

