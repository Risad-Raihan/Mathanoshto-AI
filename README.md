# Personal LLM Assistant

> 🚀 **Status**: Under Development | Previously: Tavily Search Wrapper

A full-featured ChatGPT-like personal assistant with multi-model support, multimodal capabilities, and web search integration. Built with Python, Streamlit, and support for OpenAI, Google Gemini, and Anthropic Claude.

## 🎯 Vision

Transform from a simple search wrapper into a comprehensive personal AI assistant that:
- Supports **all models** from OpenAI, Gemini, and Claude
- Provides a **chat interface** with conversation history
- Handles **multimodal input** (images, PDFs, documents)
- Includes **web search** as an optional tool (Tavily)
- Tracks **token usage and costs** in real-time
- Allows **model switching** mid-conversation

## ✨ Key Features (Planned)

### Core Features (MVP)
- 🤖 **Multi-Provider Support**: OpenAI (GPT-4o, GPT-3.5, etc.), Google Gemini (1.5 Pro, Flash, 2.0), Anthropic Claude
- 🔄 **Model Switching**: Switch between any model during conversation
- 💬 **Chat Interface**: Beautiful Streamlit UI (Next.js planned)
- 💾 **Conversation History**: SQLite database with full persistence
- 📊 **Token Tracking**: Real-time token usage and cost calculation
- 🖼️ **Multimodal**: Image upload, PDF parsing, document processing
- 🔍 **Web Search Tool**: Optional Tavily search integration
- ⚙️ **Extensible**: Easy to add new providers and tools

### Advanced Features (Roadmap)
- 📤 **Export**: Save conversations as Markdown, JSON, or PDF
- 🎙️ **Voice I/O**: Speech-to-text and text-to-speech
- 🔧 **Custom Tools**: Code execution, calculator, and more
- 🌊 **Streaming**: Real-time token-by-token responses
- 🎨 **Themes**: Customizable UI themes
- 🐳 **Docker**: Easy deployment

## 📚 Documentation

**Start here if you're new:**
1. **[QUICK_START.md](QUICK_START.md)** - Quick reference and overview
2. **[PROJECT_PLAN.md](PROJECT_PLAN.md)** - Detailed step-by-step implementation guide
3. **[DIRECTORY_STRUCTURE.md](DIRECTORY_STRUCTURE.md)** - Project structure explanation
4. **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Progress tracking and milestones

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API keys for OpenAI and/or Gemini
- Tavily API key (for web search)

### Installation

1. **Clone and setup:**
```bash
git clone <your-repo>
cd tavily_search_wraper

# Run automated setup
./setup_project.sh

# Or manually create structure
mkdir -p backend/{config,core,providers,tools,utils,database}
mkdir -p frontend/streamlit/components
mkdir -p tests/{unit,integration}
```

2. **Install dependencies:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or .\venv\Scripts\activate on Windows

pip install -r requirements.txt
```

3. **Configure environment:**
```bash
# Copy template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

Required keys:
```env
TAVILY_API_KEY=your_tavily_key_here
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

4. **Follow implementation guide:**
```bash
# Open PROJECT_PLAN.md and start with Phase 1
# Implement backend/config/settings.py first
```

5. **Run the app (after implementation):**
```bash
streamlit run frontend/streamlit/app.py
```

## 📋 Implementation Status

```
Phase 1: Foundation         [░░░░░░░░░░] 0%
Phase 2: Database          [░░░░░░░░░░] 0%
Phase 3: Frontend          [░░░░░░░░░░] 0%
Phase 4: Multimodal        [░░░░░░░░░░] 0%
Phase 5: Tools             [░░░░░░░░░░] 0%
Phase 6: Testing           [░░░░░░░░░░] 0%
```

See **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** for detailed progress.

## 🏗️ Architecture

```
User Interface (Streamlit)
         ↓
   Chat Manager
         ↓
   Model Factory → Provider Abstraction
         ↓
   LLM APIs (OpenAI, Gemini, Claude)
         ↓
   Response Processing
         ↓
   Database Storage (SQLite)
```

### Key Components:
- **Providers**: Abstraction layer for LLM APIs
- **Chat Manager**: Conversation flow and history
- **Model Factory**: Provider instantiation and management
- **Tools**: Function calling framework (web search, etc.)
- **Database**: SQLAlchemy models for persistence

## 🛠️ Technology Stack

### Backend
- **Python 3.11+**
- **LLM SDKs**: `openai`, `google-generativeai`, `anthropic`
- **Database**: SQLAlchemy + SQLite
- **Config**: Pydantic, PyYAML
- **Async**: aiohttp, asyncio
- **Files**: Pillow, PyPDF2

### Frontend
- **Streamlit** (MVP)
- **Next.js + FastAPI** (Planned)

### Development
- **Testing**: pytest, pytest-asyncio
- **Code Quality**: black, flake8, mypy

## 💰 Token Tracking

The system automatically tracks and displays:
- Input tokens per message
- Output tokens per message
- Cost per message (calculated from model pricing)
- Total cost per conversation
- Real-time updates in UI

Example pricing (from `models.yaml`):
- GPT-4o: $2.50 / $10.00 per 1M tokens
- GPT-4o-mini: $0.15 / $0.60 per 1M tokens
- Gemini 1.5 Flash: $0.075 / $0.30 per 1M tokens

## 🔧 Configuration

All models are defined in `backend/config/models.yaml`:
```yaml
openai:
  models:
    - name: "gpt-4o"
      display_name: "GPT-4o"
      context_window: 128000
      supports_vision: true
      supports_tools: true
      cost_per_1m_input_tokens: 2.50
      # ... more config
```

Easy to add new models or update pricing!

## 🎨 UI Preview (Planned)

### Sidebar:
- Provider selector (OpenAI / Gemini / Claude)
- Model dropdown (filtered by provider)
- Advanced settings (temperature, max tokens)
- System prompt editor
- Tool toggles (web search, etc.)
- Conversation list

### Main Chat:
- Token counter dashboard
- Message history with avatars
- File upload button
- Code syntax highlighting
- Markdown rendering

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=frontend

# Run specific test file
pytest tests/unit/test_providers.py

# Format code
black backend/ frontend/ tests/
```

## 📖 Legacy: Original Search Wrapper

The original Tavily search wrapper is preserved in `tavily_search.py`. It still works and can be used independently:

```bash
# Old usage (still works)
python tavily_search.py "your query" --llm openai
```

See the legacy documentation below for details.

---

# Legacy Documentation (Original Project)

## Old Features (Still Available)

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

