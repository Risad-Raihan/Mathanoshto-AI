"""
Unified Web Scraper Tool for LLM Integration
Provides web scraping capabilities as a tool that can be called by LLMs
"""
from typing import Dict, Any, Optional, List
import json

from backend.tools.web_scraper import web_scraper, url_monitor
from backend.tools.firecrawl_scraper import firecrawl_scraper


def scrape_url_tool(
    url: str,
    method: str = "standard",
    extract_main_content: bool = True,
    include_links: bool = False,
    javascript_rendering: bool = False,
    screenshot: bool = False
) -> str:
    """
    Scrape a URL and extract its content
    
    Args:
        url: The URL to scrape
        method: Scraping method ('standard', 'firecrawl', 'javascript')
        extract_main_content: Extract only main article content
        include_links: Include links found on the page
        javascript_rendering: Use JavaScript rendering (for dynamic content)
        screenshot: Take a screenshot of the page
    
    Returns:
        JSON string with scraped content and metadata
    """
    try:
        result = {}
        
        # Choose scraping method
        if method == "firecrawl" and firecrawl_scraper.is_available():
            # Use Firecrawl API
            formats = ['markdown', 'links'] if include_links else ['markdown']
            if screenshot:
                formats.append('screenshot')
            
            result = firecrawl_scraper.scrape_url(
                url=url,
                formats=formats,
                only_main_content=extract_main_content
            )
        
        elif method == "javascript" or javascript_rendering:
            # Use Playwright for JavaScript rendering
            result = web_scraper.scrape_with_javascript(
                url=url,
                screenshot=screenshot
            )
        
        else:
            # Standard scraping
            result = web_scraper.scrape_url(
                url=url,
                extract_content=extract_main_content,
                extract_metadata=True
            )
        
        # Format response for LLM
        if result.get('success'):
            response = {
                'success': True,
                'url': url,
                'title': result.get('metadata', {}).get('title', 'Unknown'),
                'content': result.get('content', '')[:15000],  # Limit content length
                'metadata': result.get('metadata', {}),
            }
            
            if include_links:
                response['links'] = result.get('links', [])[:20]  # Limit links
            
            if screenshot and result.get('screenshot_path'):
                response['screenshot'] = result['screenshot_path']
            
            return json.dumps(response, indent=2)
        else:
            return json.dumps({
                'success': False,
                'url': url,
                'error': result.get('error', 'Unknown error')
            })
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'url': url,
            'error': f'Scraping failed: {str(e)}'
        })


def monitor_url_tool(
    action: str,
    url: Optional[str] = None,
    user_id: Optional[int] = None,
    monitor_id: Optional[str] = None,
    check_interval: int = 3600
) -> str:
    """
    Monitor URLs for changes
    
    Args:
        action: Action to perform ('add', 'check', 'list', 'remove')
        url: URL to monitor (for 'add' action)
        user_id: User ID
        monitor_id: Monitor ID (for 'check' and 'remove' actions)
        check_interval: Check interval in seconds (for 'add' action)
    
    Returns:
        JSON string with result
    """
    try:
        if action == "add" and url and user_id:
            monitor_id = url_monitor.add_monitor(
                url=url,
                user_id=user_id,
                check_interval=check_interval
            )
            return json.dumps({
                'success': True,
                'action': 'add',
                'monitor_id': monitor_id,
                'url': url,
                'message': f'Started monitoring {url}'
            })
        
        elif action == "check" and monitor_id:
            result = url_monitor.check_monitor(monitor_id)
            return json.dumps(result)
        
        elif action == "list" and user_id:
            monitors = url_monitor.get_user_monitors(user_id)
            return json.dumps({
                'success': True,
                'action': 'list',
                'monitors': monitors,
                'count': len(monitors)
            })
        
        elif action == "remove" and monitor_id:
            success = url_monitor.remove_monitor(monitor_id)
            return json.dumps({
                'success': success,
                'action': 'remove',
                'monitor_id': monitor_id
            })
        
        else:
            return json.dumps({
                'success': False,
                'error': 'Invalid action or missing parameters'
            })
    
    except Exception as e:
        return json.dumps({
            'success': False,
            'error': f'Monitor operation failed: {str(e)}'
        })


# Tool definitions for LLM function calling
SCRAPER_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "scrape_url",
            "description": "Scrape a webpage and extract its content, including text, metadata, and optionally links and screenshots. Useful for reading articles, documentation, or any web content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the webpage to scrape"
                    },
                    "method": {
                        "type": "string",
                        "enum": ["standard", "firecrawl", "javascript"],
                        "description": "Scraping method: 'standard' for static pages, 'javascript' for dynamic pages, 'firecrawl' for advanced API-based scraping",
                        "default": "standard"
                    },
                    "extract_main_content": {
                        "type": "boolean",
                        "description": "Extract only the main article content (removes nav, ads, etc.)",
                        "default": True
                    },
                    "include_links": {
                        "type": "boolean",
                        "description": "Include links found on the page",
                        "default": False
                    },
                    "javascript_rendering": {
                        "type": "boolean",
                        "description": "Use JavaScript rendering for dynamic content",
                        "default": False
                    },
                    "screenshot": {
                        "type": "boolean",
                        "description": "Take a screenshot of the page",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "monitor_url",
            "description": "Monitor a URL for changes. Can add new monitors, check existing ones, list all monitors, or remove monitors.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["add", "check", "list", "remove"],
                        "description": "Action to perform"
                    },
                    "url": {
                        "type": "string",
                        "description": "URL to monitor (required for 'add' action)"
                    },
                    "user_id": {
                        "type": "integer",
                        "description": "User ID (required for 'add' and 'list' actions)"
                    },
                    "monitor_id": {
                        "type": "string",
                        "description": "Monitor ID (required for 'check' and 'remove' actions)"
                    },
                    "check_interval": {
                        "type": "integer",
                        "description": "Check interval in seconds (default: 3600 = 1 hour)",
                        "default": 3600
                    }
                },
                "required": ["action"]
            }
        }
    }
]


def get_scraper_tools(enabled: bool = True) -> Optional[List[Dict]]:
    """Get scraper tools if enabled"""
    return SCRAPER_TOOLS if enabled else None


def execute_scraper_tool(tool_name: str, tool_input: Dict[str, Any]) -> str:
    """Execute a scraper tool by name"""
    if tool_name == "scrape_url":
        return scrape_url_tool(**tool_input)
    elif tool_name == "monitor_url":
        return monitor_url_tool(**tool_input)
    else:
        return json.dumps({
            'success': False,
            'error': f'Unknown tool: {tool_name}'
        })

