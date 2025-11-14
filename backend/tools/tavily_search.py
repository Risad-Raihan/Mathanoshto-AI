"""
Tavily Web Search Tool
"""
import json
from typing import Dict, List, Optional
from tavily import TavilyClient
from backend.config.settings import settings
from backend.database.user_operations import UserAPIKeyDB

class TavilySearchTool:
    """Web search using Tavily API"""
    
    def __init__(self, api_key: Optional[str] = None, user_id: Optional[int] = None):
        """
        Initialize Tavily search tool
        
        Args:
            api_key: Tavily API key (optional, will try to load from database if user_id provided)
            user_id: User ID to load API key from database
        """
        # Try to get API key from user's database if user_id provided
        if not api_key and user_id:
            user_keys = UserAPIKeyDB.get_all_user_keys(user_id)
            api_key = user_keys.get('tavily')
        
        # Fallback to settings if still no key
        if not api_key:
            api_key = settings.tavily_api_key
            
        if not api_key:
            raise ValueError("Tavily API key not found. Please add your Tavily API key in settings.")
        
        self.client = TavilyClient(api_key=api_key)
    
    @staticmethod
    def get_tool_definition() -> Dict:
        """
        Return the tool definition for function calling
        
        This format is compatible with OpenAI and other providers
        """
        return {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Search the web for current information, news, facts, or any real-time data. Use this when the user asks about current events, recent information, or anything that requires up-to-date knowledge. Make ONE comprehensive search query instead of multiple separate searches.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to find information about"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of search results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        }
    
    def search(self, query: str, max_results: int = 5, include_images: bool = True, extract_previews: bool = False) -> str:
        """
        Execute web search with rich previews
        
        Args:
            query: Search query
            max_results: Maximum results to return
            include_images: Whether to include Tavily images
            extract_previews: Whether to extract link preview images
            
        Returns:
            Formatted search results as string with images
        """
        try:
            # Perform search with images
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False,
                include_images=include_images
            )
            
            # Debug: Print the raw response to see what we're getting
            print(f"📊 Tavily Response Keys: {response.keys() if isinstance(response, dict) else 'Not a dict'}")
            if isinstance(response, dict):
                print(f"📊 Answer: {response.get('answer', 'No answer')[:200]}")
                print(f"📊 Results count: {len(response.get('results', []))}")
                print(f"📊 Images count: {len(response.get('images', []))}")
            
            # Format results
            result_text = []
            
            # Add AI summary if available
            if response.get('answer'):
                result_text.append(f"📝 **Summary:** {response['answer']}\n")
            
            # Add Tavily images if available
            images = response.get('images', [])
            if images and include_images:
                print(f"🖼️ Processing {len(images)} Tavily images...")
                result_text.append(f"\n🖼️ **Related Images ({len(images)}):**\n")
                
                # Download and cache images
                try:
                    from backend.core.image_handler import image_handler
                    print(f"✅ Image handler loaded successfully")
                except Exception as e:
                    print(f"❌ Failed to load image handler: {e}")
                    result_text.append(f"*(Could not load image handler)*\n")
                    images = []  # Skip image processing
                
                if images:
                    # Try to get user_id safely
                    user_id = 1  # Default user
                    try:
                        import streamlit as st
                        if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_id'):
                            user_id = st.session_state.user_id
                            print(f"✅ Got user_id from session: {user_id}")
                        else:
                            print(f"⚠️ Using default user_id: {user_id}")
                    except Exception as e:
                        print(f"⚠️ Could not get user_id from session: {e}, using default: {user_id}")
                    
                    successful_images = 0
                    for idx, img_url in enumerate(images[:5], 1):  # Try up to 5 images
                        if successful_images >= 3:  # But only show 3
                            break
                        
                        print(f"📥 Attempting to download image {idx}: {img_url[:80]}...")
                        
                        # Try to download and save image
                        try:
                            img_result = image_handler.save_from_url(img_url, user_id, source='search')
                            
                            if img_result.get('success'):
                                successful_images += 1
                                print(f"✅ Image {successful_images} downloaded: {img_result['relative_path']}")
                                # Add image reference that will be displayed
                                result_text.append(f"\n![Image {successful_images}]({img_result['relative_path']})")
                                result_text.append(f"*Image {successful_images}* - {img_result.get('size_kb', 'unknown')} KB\n")
                            else:
                                print(f"❌ Image download failed: {img_result.get('error', 'Unknown error')}")
                        except Exception as img_error:
                            print(f"❌ Exception downloading image: {str(img_error)}")
                            import traceback
                            traceback.print_exc()
                    
                    print(f"✅ Successfully downloaded {successful_images} out of {len(images[:5])} images")
                    
                    if successful_images == 0:
                        result_text.append("*(No images could be downloaded - check terminal for errors)*\n")
            
            # Add search results with link previews
            result_text.append(f"\n📑 **Search Results for '{query}':**\n")
            
            # Extract link previews for better visual results
            if extract_previews:
                from backend.utils.link_preview import link_preview_extractor
                from backend.core.image_handler import image_handler
                
                user_id = 1
                try:
                    import streamlit as st
                    if hasattr(st, 'session_state') and hasattr(st.session_state, 'user_id'):
                        user_id = st.session_state.user_id
                except:
                    pass
            
            for idx, item in enumerate(response.get('results', []), 1):
                url = item.get('url', 'N/A')
                title = item.get('title', 'No title')
                content = item.get('content', 'No content')
                
                result_text.append(f"\n### {idx}. {title}")
                result_text.append(f"🔗 {url}\n")
                
                # Try to extract and show preview image
                if extract_previews and url != 'N/A':
                    try:
                        preview = link_preview_extractor.extract_preview(url)
                        
                        # If we found a preview image, download and display it
                        if preview['image']:
                            img_result = image_handler.save_from_url(
                                preview['image'], 
                                user_id, 
                                source='search'
                            )
                            
                            if img_result['success']:
                                result_text.append(f"![Preview]({img_result['relative_path']})")
                                result_text.append(f"*{preview.get('site_name', 'Website')} preview*\n")
                    except Exception as preview_error:
                        print(f"Preview extraction failed for {url}: {preview_error}")
                
                # Add description
                result_text.append(f"{content[:250]}..." if len(content) > 250 else content)
                result_text.append("")  # Empty line for spacing
            
            final_result = "\n".join(result_text)
            print(f"📊 Final formatted result length: {len(final_result)} chars")
            print(f"✅ Search complete with {len(response.get('results', []))} results")
            
            return final_result
            
        except Exception as e:
            error_msg = f"❌ Search failed: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg
    
    def execute(self, function_args: Dict) -> str:
        """
        Execute the tool with given arguments
        
        Args:
            function_args: Dictionary with 'query' and optionally 'max_results'
            
        Returns:
            Search results as string
        """
        query = function_args.get('query')
        max_results = function_args.get('max_results', 5)
        
        if not query:
            return "❌ Error: No search query provided"
        
        return self.search(query, max_results)


# Cache instances per user_id
_tavily_tools = {}

def get_tavily_tool(user_id: Optional[int] = None) -> TavilySearchTool:
    """
    Get or create Tavily tool instance for a specific user
    
    Args:
        user_id: User ID to load API key from database. If None, uses settings.
    
    Returns:
        TavilySearchTool instance
    """
    # Use user_id as cache key, or 'default' if None
    cache_key = user_id if user_id is not None else 'default'
    
    if cache_key not in _tavily_tools:
        _tavily_tools[cache_key] = TavilySearchTool(user_id=user_id)
    
    return _tavily_tools[cache_key]


def get_enabled_tools(use_tavily: bool = False, use_web_scraper: bool = False, use_youtube: bool = False, use_data_analyzer: bool = False, use_image_generator: bool = False, user_id: Optional[int] = None) -> List[Dict]:
    """
    Get list of enabled tool definitions
    
    Args:
        use_tavily: Whether to enable Tavily search
        use_web_scraper: Whether to enable web scraper
        use_youtube: Whether to enable YouTube summarizer
        use_data_analyzer: Whether to enable data analyzer
        use_image_generator: Whether to enable AI image generation
        user_id: User ID to load API keys from database
    
    Returns:
        List of tool definitions for LLM
    """
    tools = []
    
    if use_tavily:
        try:
            tool = get_tavily_tool(user_id=user_id)
            tools.append(tool.get_tool_definition())
        except ValueError as e:
            # Tavily not configured, skip
            print(f"⚠️ Warning: {e}")
    
    if use_web_scraper:
        try:
            from backend.tools.scraper_tool import SCRAPER_TOOLS
            tools.extend(SCRAPER_TOOLS)
        except Exception as e:
            print(f"⚠️ Warning: Web scraper not available: {e}")
    
    if use_youtube:
        try:
            from backend.tools.youtube_integration import YOUTUBE_TOOLS
            tools.extend(YOUTUBE_TOOLS)
        except Exception as e:
            print(f"⚠️ Warning: YouTube tools not available: {e}")
    
    if use_data_analyzer:
        try:
            from backend.tools.data_analyzer_integration import DATA_ANALYZER_TOOLS
            tools.extend(DATA_ANALYZER_TOOLS)
        except Exception as e:
            print(f"⚠️ Warning: Data analyzer not available: {e}")
    
    if use_image_generator:
        try:
            from backend.tools.image_generator import IMAGE_GENERATION_TOOLS
            tools.extend(IMAGE_GENERATION_TOOLS)
        except Exception as e:
            print(f"⚠️ Warning: Image generator not available: {e}")
    
    return tools

