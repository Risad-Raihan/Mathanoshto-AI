"""
Tavily Web Search Tool
"""
import json
from typing import Dict, List
from tavily import TavilyClient
from backend.config.settings import get_settings

settings = get_settings()

class TavilySearchTool:
    """Web search using Tavily API"""
    
    def __init__(self):
        if not settings.tavily_api_key:
            raise ValueError("Tavily API key not configured in .env file")
        
        self.client = TavilyClient(api_key=settings.tavily_api_key)
    
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
                "description": "Search the web for current information, news, facts, or any real-time data. Use this when the user asks about current events, recent information, or anything that requires up-to-date knowledge.",
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
    
    def search(self, query: str, max_results: int = 5) -> str:
        """
        Execute web search
        
        Args:
            query: Search query
            max_results: Maximum results to return
            
        Returns:
            Formatted search results as string
        """
        try:
            # Perform search
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True,
                include_raw_content=False
            )
            
            # Format results
            result_text = []
            
            # Add AI summary if available
            if response.get('answer'):
                result_text.append(f"📝 Summary: {response['answer']}\n")
            
            # Add search results
            result_text.append(f"🔍 Search Results for '{query}':\n")
            
            for idx, item in enumerate(response.get('results', []), 1):
                result_text.append(f"\n{idx}. **{item.get('title', 'No title')}**")
                result_text.append(f"   URL: {item.get('url', 'N/A')}")
                result_text.append(f"   {item.get('content', 'No content')[:300]}...")
            
            return "\n".join(result_text)
            
        except Exception as e:
            return f"❌ Search failed: {str(e)}"
    
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


# Singleton instance
_tavily_tool = None

def get_tavily_tool() -> TavilySearchTool:
    """Get or create Tavily tool instance"""
    global _tavily_tool
    if _tavily_tool is None:
        _tavily_tool = TavilySearchTool()
    return _tavily_tool


def get_enabled_tools(use_tavily: bool = False) -> List[Dict]:
    """
    Get list of enabled tool definitions
    
    Args:
        use_tavily: Whether to enable Tavily search
        
    Returns:
        List of tool definitions for LLM
    """
    tools = []
    
    if use_tavily:
        try:
            tool = get_tavily_tool()
            tools.append(tool.get_tool_definition())
        except ValueError as e:
            # Tavily not configured, skip
            print(f"⚠️ Warning: {e}")
    
    return tools

