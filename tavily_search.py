# -*- coding: utf-8 -*-
"""
Tavily Search Agent with LLM Wrapper
Searches using Tavily API and wraps results using LLM (Gemini 2.5-flash or OpenAI)
Outputs formatted markdown for Obsidian
"""

import os
import argparse
from datetime import datetime
from tavily import TavilyClient
import google.generativeai as genai
from openai import OpenAI
from typing import Optional, Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Load API keys from environment variables
TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL')  # Custom endpoint (optional)

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# Initialize OpenAI (will be created per-request if custom endpoint is used)
openai_client = None
if OPENAI_API_KEY:
    if OPENAI_BASE_URL:
        # Custom endpoint - client will be created in wrap_with_openai
        openai_client = None  # Will create with custom base_url when needed
    else:
        # Standard OpenAI endpoint
        openai_client = OpenAI(api_key=OPENAI_API_KEY)


def search_tavily(query: str, max_results: int = 5, search_depth: str = "advanced") -> Dict:
    """
    Search using Tavily API

    Args:
        query: Search query string
        max_results: Maximum number of results (1-10)
        search_depth: "basic" or "advanced"
    """
    if not TAVILY_API_KEY:
        raise ValueError("TAVILY_API_KEY environment variable not set")
    
    client = TavilyClient(api_key=TAVILY_API_KEY)

    print(f"🔍 Searching: {query}")

    response = client.search(
        query=query,
        max_results=max_results,
        search_depth=search_depth,
        include_answer=True,
        include_raw_content=False,
        include_images=True
    )

    print(f"✓ Found {len(response.get('results', []))} results")
    return response


def wrap_with_gemini(query: str, search_results: List[Dict], model: str = None, max_tokens: int = 2000) -> str:
    """
    Wrap search results using Gemini models
    
    Args:
        query: Original search query
        search_results: List of search result dictionaries
        model: Specific Gemini model to use (optional, will try multiple if not specified)
        max_tokens: Maximum tokens for response
    """
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    
    # Prepare context from search results
    context = f"Search Query: {query}\n\n"
    context += "Search Results:\n\n"
    
    for i, result in enumerate(search_results, 1):
        title = result.get('title', 'Untitled')
        url = result.get('url', 'N/A')
        content = result.get('content', 'No content available')
        context += f"Result {i}:\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
    
    # Create prompt for Gemini
    prompt = f"""You are a research assistant. Based on the following search results, create a comprehensive, well-structured summary that:

1. Synthesizes the key information from all search results
2. Identifies common themes and important insights
3. Highlights the most relevant and valuable information
4. Organizes the content in a clear, logical manner
5. Provides actionable insights or conclusions when possible

Search Query: {query}

Search Results:
{context}

Please provide a detailed, well-formatted summary that wraps and synthesizes these search results. Use markdown formatting for better readability."""

    # Try different Gemini models in order of preference
    if model:
        models_to_try = [model]
    else:
        models_to_try = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
    
    for model_name in models_to_try:
        try:
            genai_model = genai.GenerativeModel(model_name)
            response = genai_model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=max_tokens,
                    temperature=0.7,
                )
            )
            print(f"✓ Using Gemini model: {model_name}")
            return response.text
        except Exception as e:
            print(f"⚠️ Error with {model_name}: {e}")
            continue
    
    print(f"❌ All Gemini models failed")
    return None


def wrap_with_openai(query: str, search_results: List[Dict], model: str = "gpt-4o-mini", max_tokens: int = 2000, base_url: Optional[str] = None) -> str:
    """
    Wrap search results using OpenAI
    
    Args:
        query: Original search query
        search_results: List of search result dictionaries
        model: OpenAI model to use (default: gpt-5)
        max_tokens: Maximum tokens for response
        base_url: Custom OpenAI-compatible endpoint URL (optional, uses OPENAI_BASE_URL env var if not provided)
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    
    # Use provided base_url, or fall back to environment variable, or None for default OpenAI
    endpoint_url = base_url or OPENAI_BASE_URL
    
    # Create client with custom endpoint if needed
    if endpoint_url:
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=endpoint_url)
        print(f"✓ Using custom OpenAI endpoint: {endpoint_url}")
    elif openai_client:
        client = openai_client
    else:
        raise ValueError("OpenAI client not initialized")
    
    # Prepare context from search results
    context = f"Search Query: {query}\n\n"
    context += "Search Results:\n\n"
    
    for i, result in enumerate(search_results, 1):
        title = result.get('title', 'Untitled')
        url = result.get('url', 'N/A')
        content = result.get('content', 'No content available')
        context += f"Result {i}:\nTitle: {title}\nURL: {url}\nContent: {content}\n\n"
    
    # Create prompt for OpenAI
    messages = [
        {
            "role": "system",
            "content": "You are a research assistant. Based on search results, create comprehensive, well-structured summaries that synthesize key information, identify themes, and provide actionable insights."
        },
        {
            "role": "user",
            "content": f"""Based on the following search results, create a comprehensive, well-structured summary that:

1. Synthesizes the key information from all search results
2. Identifies common themes and important insights
3. Highlights the most relevant and valuable information
4. Organizes the content in a clear, logical manner
5. Provides actionable insights or conclusions when possible

Search Query: {query}

Search Results:
{context}

Please provide a detailed, well-formatted summary that wraps and synthesizes these search results. Use markdown formatting for better readability."""
        }
    ]
    
    # Determine which parameter to use based on model
    # Newer models (gpt-5, o1, o3, etc.) use max_completion_tokens
    # Older models use max_tokens
    use_max_completion_tokens = model.startswith(('gpt-5', 'o1', 'o3'))
    
    try:
        # Try with the appropriate parameter
        if use_max_completion_tokens:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_completion_tokens=max_tokens,
                temperature=0.7
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7
            )
        return response.choices[0].message.content
    except Exception as e:
        error_str = str(e)
        # If max_tokens error, retry with max_completion_tokens
        if ('max_tokens' in error_str.lower() and 
            ('max_completion_tokens' in error_str.lower() or 
             'unsupported_parameter' in error_str.lower() or
             'not supported' in error_str.lower())):
            try:
                print(f"⚠️  Model requires max_completion_tokens. Retrying...")
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_completion_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e2:
                print(f"❌ Error with OpenAI (retry): {e2}")
                return None
        else:
            print(f"❌ Error with OpenAI: {e}")
            return None


def wrap_search_results(query: str, search_results: List[Dict], llm_provider: str = "gemini", **kwargs) -> Optional[str]:
    """
    Wrap search results using specified LLM provider
    
    Args:
        query: Original search query
        search_results: List of search result dictionaries
        llm_provider: "gemini" or "openai"
        **kwargs: Additional arguments for LLM functions
    """
    print(f"🤖 Wrapping results with {llm_provider.upper()}...")
    
    if llm_provider.lower() == "gemini":
        return wrap_with_gemini(query, search_results, **kwargs)
    elif llm_provider.lower() == "openai":
        return wrap_with_openai(query, search_results, **kwargs)
    else:
        raise ValueError(f"Unknown LLM provider: {llm_provider}. Use 'gemini' or 'openai'.")


def format_as_markdown(query: str, response: Dict, llm_wrapped_content: Optional[str] = None, 
                      llm_provider: Optional[str] = None, include_images: bool = True) -> str:
    """Format Tavily response as Obsidian markdown with LLM-wrapped content"""

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_only = datetime.now().strftime("%Y-%m-%d")

    md = f"""---
tags: [search, tavily, {date_only}]
query: "{query}"
date: {timestamp}
---
"""

    if llm_provider:
        md += f"""
# 🔍 Search: {query}

**Date:** {timestamp}  
**Results:** {len(response.get('results', []))}  
**LLM Provider:** {llm_provider.upper()}

"""
    else:
        md += f"""
# 🔍 Search: {query}

**Date:** {timestamp}  
**Results:** {len(response.get('results', []))}

"""

    # LLM-Wrapped Summary (if available)
    if llm_wrapped_content:
        md += f"""## 🤖 LLM-Wrapped Summary

{llm_wrapped_content}

---

"""
    # Original AI Summary from Tavily
    elif response.get('answer'):
        md += f"""## 📝 AI Summary (Tavily)

{response['answer']}

---

"""

    # Search Results
    md += "## 📚 Search Results\n\n"

    for i, result in enumerate(response.get('results', []), 1):
        title = result.get('title', 'Untitled')
        url = result.get('url', 'N/A')
        score = result.get('score', 'N/A')
        content = result.get('content', 'No content available')

        md += f"""### {i}. [{title}]({url})

**Relevance Score:** {score:.3f}

{content}

**Source:** {url}

---

"""

    # Images
    if include_images and response.get('images'):
        md += "## 🖼️ Related Images\n\n"
        for img_url in response['images'][:5]:
            md += f"![]({img_url})\n\n"

    # Footer
    md += f"""---

*Generated with Tavily API{' + ' + llm_provider.upper() + ' LLM' if llm_provider else ''} on {timestamp}*
"""

    return md


def create_filename(query: str) -> str:
    """Create safe filename from query"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_query = "".join(c for c in query if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_query = safe_query.replace(' ', '_')[:50]
    return f"{timestamp}_{safe_query}.md"


def search_and_save(query: str, max_results: int = 5, search_depth: str = "advanced",
                   llm_provider: Optional[str] = None, output_dir: str = "output",
                   include_images: bool = True, **llm_kwargs) -> tuple:
    """
    Perform a search, wrap with LLM (optional), and save to file
    
    Args:
        query: Search query string
        max_results: Maximum number of results (1-10)
        search_depth: "basic" or "advanced"
        llm_provider: "gemini" or "openai" (optional)
        output_dir: Directory to save output files
        include_images: Whether to include images in output
        **llm_kwargs: Additional arguments for LLM functions
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Search
        response = search_tavily(query, max_results, search_depth)
        
        # Wrap with LLM if provider is specified
        llm_wrapped_content = None
        if llm_provider:
            search_results = response.get('results', [])
            if search_results:
                llm_wrapped_content = wrap_search_results(
                    query, 
                    search_results, 
                    llm_provider=llm_provider,
                    **llm_kwargs
                )
                if llm_wrapped_content:
                    print(f"✓ LLM wrapping completed")
                else:
                    print(f"⚠️ LLM wrapping failed, continuing without LLM content")
            else:
                print(f"⚠️ No search results to wrap")
        
        # Format
        markdown = format_as_markdown(
            query, 
            response, 
            llm_wrapped_content=llm_wrapped_content,
            llm_provider=llm_provider,
            include_images=include_images
        )

        # Create filename
        filename = create_filename(query)
        filepath = os.path.join(output_dir, filename)

        # Save file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"✓ Created: {filepath}")
        print(f"✓ File saved to: {os.path.abspath(filepath)}")

        return filepath, markdown

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None, None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tavily Search Agent with LLM Wrapper - Search the web and wrap results with LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Search with OpenAI
  python tavily_search.py "latest AI developments" --llm openai
  
  # Search with Gemini
  python tavily_search.py "latest AI developments" --llm gemini
  
  # Search without LLM wrapping
  python tavily_search.py "latest AI developments"
  
  # Custom OpenAI endpoint and model
  python tavily_search.py "your query" --llm openai --model gpt-4 --base-url https://your-endpoint.com/v1
        """
    )
    
    parser.add_argument(
        "query",
        type=str,
        help="Search query string"
    )
    
    parser.add_argument(
        "--llm",
        type=str,
        choices=["openai", "gemini"],
        default=None,
        help="LLM provider to use for wrapping results (openai or gemini). If not specified, will use first available provider or skip LLM wrapping."
    )
    
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        choices=range(1, 11),
        metavar="[1-10]",
        help="Maximum number of search results (default: 5)"
    )
    
    parser.add_argument(
        "--search-depth",
        type=str,
        choices=["basic", "advanced"],
        default="advanced",
        help="Search depth: basic or advanced (default: advanced)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name to use (e.g., 'gpt-5' for OpenAI, 'gemini-1.5-flash' for Gemini). Defaults to provider defaults."
    )
    
    parser.add_argument(
        "--base-url",
        type=str,
        default=None,
        help="Custom OpenAI endpoint URL (overrides OPENAI_BASE_URL env var)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Output directory for markdown files (default: output)"
    )
    
    parser.add_argument(
        "--no-images",
        action="store_true",
        help="Exclude images from output"
    )
    
    args = parser.parse_args()
    
    # Determine LLM provider
    llm_provider = args.llm
    
    # If provider not specified, check available providers
    if not llm_provider:
        available_providers = []
        if OPENAI_API_KEY:
            available_providers.append("openai")
        if GEMINI_API_KEY:
            available_providers.append("gemini")
        
        if available_providers:
            llm_provider = available_providers[0]
            print(f"ℹ️  No LLM provider specified. Using: {llm_provider}")
        else:
            print("⚠️  No LLM API keys found. Running search without LLM wrapping.")
            print("   Set OPENAI_API_KEY (and optionally OPENAI_BASE_URL) or GEMINI_API_KEY environment variables to enable LLM wrapping.")
    else:
        # Validate provider has API key
        if llm_provider == "openai" and not OPENAI_API_KEY:
            print("❌ Error: OPENAI_API_KEY not set. Cannot use OpenAI provider.")
            exit(1)
        elif llm_provider == "gemini" and not GEMINI_API_KEY:
            print("❌ Error: GEMINI_API_KEY not set. Cannot use Gemini provider.")
            exit(1)
    
    # Prepare LLM kwargs
    llm_kwargs = {}
    if args.model:
        llm_kwargs["model"] = args.model
    if args.base_url:
        llm_kwargs["base_url"] = args.base_url
    
    # Print configuration
    print(f"\n{'='*60}")
    print(f"🔍 Search Query: {args.query}")
    print(f"📊 Max Results: {args.max_results}")
    print(f"🔬 Search Depth: {args.search_depth}")
    if llm_provider:
        print(f"🤖 LLM Provider: {llm_provider.upper()}")
        if llm_provider == "openai" and (args.base_url or OPENAI_BASE_URL):
            endpoint = args.base_url or OPENAI_BASE_URL
            print(f"🌐 Custom Endpoint: {endpoint}")
        if args.model:
            print(f"🎯 Model: {args.model}")
    else:
        print(f"🤖 LLM Provider: None (no wrapping)")
    print(f"📁 Output Directory: {args.output_dir}")
    print(f"{'='*60}\n")
    
    # Run search
    search_and_save(
        query=args.query,
        max_results=args.max_results,
        search_depth=args.search_depth,
        llm_provider=llm_provider,
        output_dir=args.output_dir,
        include_images=not args.no_images,
        **llm_kwargs
    )
