# Quick Start Guide

This is a condensed version of the implementation plan. For full technical details, see **PROJECT_PLAN.md**.

## 🎯 What We're Building

Transforming your Tavily search wrapper into a **ChatGPT-like personal assistant** with:
- ✅ All OpenAI & Gemini models
- ✅ Chat interface with conversation history
- ✅ Multimodal (images, PDFs)
- ✅ Web search tool (Tavily)
- ✅ Token usage tracking
- ✅ Model switching on the fly

## 📦 Prerequisites

- Python 3.11+
- API keys for OpenAI and/or Gemini
- Tavily API key (for web search)

## 🚀 Quick Setup (Before Starting Implementation)

### 1. Install Additional Dependencies

```bash
pip install pydantic-settings PyYAML SQLAlchemy Pillow PyPDF2 python-magic tiktoken aiohttp streamlit
```

### 2. Create .env File

Create a `.env` file in your project root:

```env
TAVILY_API_KEY=your_tavily_key
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key
DATABASE_URL=sqlite:///./chat_history.db
```

## 📋 Implementation Order

Follow **PROJECT_PLAN.md** in this order:

### Week 1: Foundation
1. **Task 1.1**: Create new directory structure
2. **Task 1.2**: Configuration management (settings.py, models.yaml)
3. **Task 1.3**: Provider base class
4. **Task 1.4**: OpenAI provider
5. **Task 1.5**: Gemini provider
6. **Task 1.6**: Model factory

**Test milestone**: Can list all models from both providers

### Week 2: Chat & Database
7. **Task 2.1**: Database models (SQLAlchemy)
8. **Task 2.2**: Chat manager
9. **Task 3.1**: Basic Streamlit app

**Test milestone**: Can have a conversation and save to database

### Week 3: Multimodal & Tools
10. **Task 4.1**: File upload handler
11. **Task 4.2**: Integrate files in chat
12. **Task 5.1**: Tool base class
13. **Task 5.2**: Tavily search tool

**Test milestone**: Can upload images and use web search

### Week 4: Polish
14. Testing, error handling, documentation

## 🔍 Key Files You'll Create

### Core Backend
```
backend/
├── config/
│   ├── settings.py          # Centralized config (Pydantic)
│   └── models.yaml          # All model definitions
├── providers/
│   ├── base.py              # Abstract base class
│   ├── openai_provider.py   # OpenAI implementation
│   └── gemini_provider.py   # Gemini implementation
├── core/
│   ├── model_factory.py     # Provider manager
│   └── chat_manager.py      # Conversation handler
├── database/
│   ├── models.py            # SQLAlchemy models
│   └── operations.py        # DB operations
└── tools/
    ├── base.py              # Tool base class
    └── tavily_search.py     # Web search tool
```

### Frontend (Streamlit)
```
frontend/streamlit/
├── app.py                   # Main entry point
└── components/
    ├── sidebar.py           # Settings & model selector
    ├── chat.py              # Chat interface
    └── file_upload.py       # File handling UI
```

## ⚡ Quick Test Commands

After each phase, test your implementation:

### Test Providers (After Phase 1)
```python
import asyncio
from backend.providers.openai_provider import OpenAIProvider

async def test():
    provider = OpenAIProvider()
    models = provider.get_available_models()
    print([m.display_name for m in models])
    
    response = await provider.chat_completion(
        messages=[{"role": "user", "content": "Hello!"}],
        model="gpt-3.5-turbo"
    )
    print(f"Response: {response.content}")
    print(f"Cost: ${response.cost:.6f}")

asyncio.run(test())
```

### Test Database (After Phase 2)
```python
from backend.database.operations import init_database, ConversationDB, MessageDB

init_database()
conv = ConversationDB.create_conversation("Test")
MessageDB.add_message(conv.id, "user", "Hello!")
print(f"Created conversation {conv.id}")
```

### Test Chat Manager (After Phase 2)
```python
import asyncio
from backend.core.chat_manager import ChatManager

async def test():
    chat = ChatManager()
    response = await chat.send_message(
        user_message="What is 2+2?",
        provider="openai",
        model="gpt-3.5-turbo"
    )
    print(f"Response: {response.content}")
    print(f"Usage: {chat.get_token_usage()}")

asyncio.run(test())
```

### Run Streamlit App (After Phase 3)
```bash
streamlit run frontend/streamlit/app.py
```

## 🎯 MVP Feature Checklist

Your Minimum Viable Product should have:

- [x] Load all OpenAI models
- [x] Load all Gemini models
- [x] Switch between models
- [x] Chat interface
- [x] Save conversation history
- [x] Display token usage and cost
- [x] Token counter in real-time
- [x] New conversation button
- [x] Load previous conversations
- [x] Upload images (for vision models)
- [x] Web search tool (Tavily)
- [x] Auto-generate conversation titles

## 🐛 Common Issues & Solutions

### Issue: "Module not found"
**Solution**: Make sure all `__init__.py` files are created in package directories.

### Issue: "API key not found"
**Solution**: Check your `.env` file is in the project root and has correct variable names.

### Issue: "Database not initialized"
**Solution**: Call `init_database()` at app startup in `app.py`.

### Issue: Async errors in Streamlit
**Solution**: Use `asyncio.run()` to execute async functions from Streamlit.

### Issue: Gemini token counting errors
**Solution**: Falls back to rough estimation. This is expected and handled in the code.

## 📊 Architecture Overview

```
User Input (Streamlit)
    ↓
Chat Manager
    ↓
Model Factory → Provider (OpenAI/Gemini)
    ↓
LLM API
    ↓
Response → Database → Display
```

### Data Flow:
1. User sends message via Streamlit
2. Chat Manager retrieves conversation history
3. Model Factory provides the selected provider
4. Provider formats request and calls LLM API
5. Response includes content + token counts
6. Chat Manager saves to database
7. Streamlit displays response + usage stats

## 🎨 UI Features

### Sidebar:
- Provider selector (OpenAI/Gemini)
- Model dropdown (filtered by provider)
- Model info card (context window, costs, capabilities)
- Advanced settings (temperature, max tokens)
- System prompt input
- Tools toggle (Tavily search)
- New conversation button
- Recent conversations list

### Main Chat:
- Token counter at top (input/output/total/cost)
- Chat message history
- User/assistant avatars
- Token info per message
- File upload button
- Chat input box

## 💰 Cost Tracking

The system automatically tracks:
- Input tokens per message
- Output tokens per message
- Cost per message (calculated from model pricing)
- Total cost per conversation
- Real-time display in UI

Example:
```
GPT-4o-mini: $0.15 per 1M input tokens, $0.60 per 1M output tokens
Message: 100 input, 50 output
Cost: (100/1,000,000 * 0.15) + (50/1,000,000 * 0.60) = $0.000045
```

## 🔧 Configuration Deep Dive

### models.yaml Structure:
Each model has these properties:
- `name`: API identifier (e.g., "gpt-4o")
- `display_name`: Human-readable name
- `description`: Short description
- `context_window`: Maximum context in tokens
- `max_output_tokens`: Maximum output length
- `supports_vision`: Boolean for image support
- `supports_tools`: Boolean for function calling
- `supports_json_mode`: Boolean for JSON output
- `cost_per_1m_input_tokens`: Cost per million input tokens
- `cost_per_1m_output_tokens`: Cost per million output tokens

This makes it easy to add new models - just add them to the YAML!

## 📈 Extending the System

### Adding a New Provider (e.g., Claude):

1. Create `backend/providers/anthropic_provider.py`
2. Inherit from `BaseLLMProvider`
3. Implement all abstract methods
4. Add models to `models.yaml`
5. Register in `model_factory.py`

### Adding a New Tool:

1. Create file in `backend/tools/`
2. Inherit from `BaseTool`
3. Define name, description, parameters
4. Implement `execute()` method
5. Register in tool manager
6. Add toggle in sidebar

## 🎓 Learning Resources

- **Streamlit Docs**: https://docs.streamlit.io/
- **OpenAI API**: https://platform.openai.com/docs/api-reference
- **Gemini API**: https://ai.google.dev/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org/
- **Pydantic**: https://docs.pydantic.dev/

## 💡 Tips for Success

1. **Work incrementally**: Complete each task, test, then move on
2. **Use the tests**: Run the test code after each phase
3. **Check the database**: Use a SQLite browser to inspect your data
4. **Print debug info**: Use `print()` statements liberally during development
5. **Start simple**: Get basic chat working before adding advanced features
6. **Read error messages**: Python errors are usually very helpful
7. **Refer to PROJECT_PLAN.md**: It has all the detailed code

## 🚀 After MVP: Next Features

Once your MVP is working, consider adding:

1. **Streaming responses**: Real-time token-by-token output
2. **Message editing**: Edit and regenerate responses
3. **Conversation branching**: Multiple paths from one message
4. **Code execution**: Run Python code in responses
5. **Export**: Save conversations as Markdown/PDF
6. **Voice input**: Speech-to-text
7. **Plugins**: Extensible tool system
8. **Next.js frontend**: Professional web UI
9. **Docker**: Easy deployment
10. **Cloud hosting**: Deploy on Vercel/AWS

## ❓ Need Help?

If you get stuck:
1. Check **PROJECT_PLAN.md** for detailed code examples
2. Review the test commands above
3. Verify your `.env` file is correct
4. Check that all dependencies are installed
5. Make sure directory structure matches the plan

---

**Ready to start? Open PROJECT_PLAN.md and begin with Phase 1, Task 1.1!** 🎉

