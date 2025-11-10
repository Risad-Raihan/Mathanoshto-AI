# Tavily Search Agent with LLM Wrapper

An intelligent search agent that uses Tavily API to search the web and wraps the results using LLM (Gemini 2.5-flash or OpenAI) for enhanced summaries. Outputs formatted markdown files optimized for Obsidian.

## Features

- 🔍 **Tavily Search**: Advanced web search with Tavily API
- 🤖 **LLM Wrapping**: Synthesize and enhance search results using:
  - Google Gemini 2.5-flash (or 1.5-flash as fallback)
  - OpenAI GPT models (gpt-5 by default)
- 📝 **Obsidian Format**: Outputs beautifully formatted markdown files
- 🎯 **Flexible**: Use with or without LLM wrapping

## Installation

1. **If you have a virtual environment**, activate it first:
```bash
# Windows PowerShell
.\search_agent\Scripts\Activate.ps1

# Windows Command Prompt
.\search_agent\Scripts\activate.bat

# Linux/Mac
source search_agent/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

**Note:** If you're using the existing virtual environment in `search_agent/`, the packages are already installed. Just make sure to activate it or use the venv's Python directly:
```bash
# Use venv Python directly (Windows)
.\search_agent\Scripts\python.exe tavily_search.py "your query" --llm openai
```

3. Set up API keys as environment variables:

**Windows (PowerShell):**
```powershell
$env:TAVILY_API_KEY="your_tavily_api_key"
$env:OPENAI_API_KEY="your_openai_api_key"
# Optional: Custom OpenAI endpoint (e.g., Azure OpenAI, OpenAI-compatible API)
$env:OPENAI_BASE_URL="https://your-custom-endpoint.com/v1"
```

**Windows (Command Prompt):**
```cmd
set TAVILY_API_KEY=your_tavily_api_key
set OPENAI_API_KEY=your_openai_api_key
set OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

**Linux/Mac:**
```bash
export TAVILY_API_KEY="your_tavily_api_key"
export OPENAI_API_KEY="your_openai_api_key"
export OPENAI_BASE_URL="https://your-custom-endpoint.com/v1"
```

Or create a `.env` file (recommended):
```
TAVILY_API_KEY=your_tavily_api_key
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

**Note:** If you only want to use OpenAI (not Gemini), you don't need to set `GEMINI_API_KEY`.

## Usage

### Basic Usage (with LLM wrapping)

```python
from tavily_search import search_and_save

# Search with Gemini
search_and_save(
    query="latest developments in AI agents 2025",
    max_results=5,
    search_depth="advanced",
    llm_provider="gemini"
)

# Search with OpenAI
search_and_save(
    query="latest developments in AI agents 2025",
    max_results=5,
    search_depth="advanced",
    llm_provider="openai",
    model="gpt-5"  # Optional: specify OpenAI model (default is gpt-5)
)
```

### Without LLM Wrapping

```python
from tavily_search import search_and_save

search_and_save(
    query="latest developments in AI agents 2025",
    max_results=5,
    search_depth="advanced"
)
```

### Using OpenAI with Custom Endpoint

If you have a custom OpenAI-compatible endpoint (e.g., Azure OpenAI, local LLM server, or other OpenAI-compatible APIs):

**Windows (PowerShell):**
```powershell
$env:TAVILY_API_KEY="your_tavily_api_key"
$env:OPENAI_API_KEY="your_api_key"
$env:OPENAI_BASE_URL="https://your-endpoint.com/v1"
```

**In code:**
```python
from tavily_search import search_and_save

search_and_save(
    query="your query",
    llm_provider="openai",
    base_url="https://your-custom-endpoint.com/v1",  # Optional: override env var
    model="your-model-name"  # Model name for your endpoint
)
```

### Command Line

Run the script with command-line arguments:

**Basic usage:**
```bash
# Search with OpenAI
python tavily_search.py "latest developments in AI agents 2025" --llm openai

# Search with Gemini
python tavily_search.py "latest developments in AI agents 2025" --llm gemini

# Search without LLM wrapping
python tavily_search.py "latest developments in AI agents 2025"
```

**With custom options:**
```bash
# Custom OpenAI endpoint and model
python tavily_search.py "your query" --llm openai --model gpt-4 --base-url https://your-endpoint.com/v1

# More results, basic search depth
python tavily_search.py "your query" --llm openai --max-results 10 --search-depth basic

# Custom output directory, no images
python tavily_search.py "your query" --llm gemini --output-dir my_results --no-images
```

**All available options:**
```bash
python tavily_search.py --help
```

The `--llm` parameter allows you to explicitly choose between `openai` or `gemini`. If not specified, it will use the first available provider based on your API keys.

## API Keys

You'll need API keys from:

1. **Tavily** (Required): Get your API key from [tavily.com](https://tavily.com)
2. **OpenAI** (Optional, for LLM wrapping): 
   - Standard OpenAI: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
   - Custom endpoint: Set `OPENAI_BASE_URL` to your endpoint URL (e.g., Azure OpenAI, local LLM server)
3. **Gemini** (Optional, for LLM wrapping): Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

**To use only OpenAI:** Just set `TAVILY_API_KEY` and `OPENAI_API_KEY` (and `OPENAI_BASE_URL` if using a custom endpoint). You don't need Gemini.

## Output

The script creates markdown files in the `output/` directory with:
- LLM-wrapped comprehensive summary (if LLM provider is used)
- Original search results with relevance scores
- Related images (if available)
- Proper Obsidian frontmatter with tags and metadata

## Customization

You can customize the LLM behavior:

```python
# Gemini with custom max tokens
search_and_save(
    query="your query",
    llm_provider="gemini",
    max_tokens=3000
)

# OpenAI with specific model
search_and_save(
    query="your query",
    llm_provider="openai",
    model="gpt-4",
    max_tokens=2000
)
```

## License

MIT

