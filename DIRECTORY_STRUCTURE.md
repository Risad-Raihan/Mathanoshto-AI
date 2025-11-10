# Project Directory Structure

## 📁 Complete Directory Layout

This is the complete directory structure you need to create for the Personal LLM Assistant project.

```
tavily_search_wraper/                    # Project root
│
├── backend/                             # Backend logic
│   ├── __init__.py                      # Package marker
│   │
│   ├── config/                          # Configuration management
│   │   ├── __init__.py
│   │   ├── settings.py                  # Pydantic settings (env vars)
│   │   └── models.yaml                  # Model definitions (all providers)
│   │
│   ├── providers/                       # LLM provider implementations
│   │   ├── __init__.py
│   │   ├── base.py                      # Abstract base class
│   │   ├── openai_provider.py           # OpenAI implementation
│   │   ├── gemini_provider.py           # Gemini implementation
│   │   └── anthropic_provider.py        # [Future] Claude implementation
│   │
│   ├── core/                            # Core business logic
│   │   ├── __init__.py
│   │   ├── model_factory.py             # Provider factory (singleton)
│   │   ├── chat_manager.py              # Conversation management
│   │   └── message_handler.py           # [Future] Message processing
│   │
│   ├── tools/                           # Function calling tools
│   │   ├── __init__.py
│   │   ├── base.py                      # Abstract tool class
│   │   ├── tavily_search.py             # Web search tool
│   │   ├── code_execution.py            # [Future] Code interpreter
│   │   └── calculator.py                # [Future] Math tool
│   │
│   ├── utils/                           # Utility functions
│   │   ├── __init__.py
│   │   ├── file_handler.py              # File upload/processing
│   │   ├── image_processor.py           # Image optimization
│   │   ├── token_counter.py             # Token counting utilities
│   │   └── logger.py                    # [Future] Logging setup
│   │
│   └── database/                        # Database layer
│       ├── __init__.py
│       ├── models.py                    # SQLAlchemy models
│       └── operations.py                # Database operations (CRUD)
│
├── frontend/                            # Frontend interfaces
│   ├── __init__.py
│   │
│   └── streamlit/                       # Streamlit UI (MVP)
│       ├── app.py                       # Main entry point
│       │
│       ├── components/                  # UI components
│       │   ├── __init__.py
│       │   ├── sidebar.py               # Settings sidebar
│       │   ├── chat.py                  # Main chat interface
│       │   ├── file_upload.py           # File upload widget
│       │   └── token_display.py         # [Future] Token counter widget
│       │
│       └── styles/                      # Custom styling
│           ├── custom.css               # [Optional] Custom CSS
│           └── theme.json               # [Optional] Streamlit theme
│
├── tests/                               # Test suite
│   ├── __init__.py
│   │
│   ├── unit/                            # Unit tests
│   │   ├── __init__.py
│   │   ├── test_providers.py            # Test LLM providers
│   │   ├── test_chat_manager.py         # Test chat logic
│   │   ├── test_database.py             # Test database ops
│   │   └── test_tools.py                # Test tools
│   │
│   ├── integration/                     # Integration tests
│   │   ├── __init__.py
│   │   ├── test_end_to_end.py           # Full flow tests
│   │   └── test_api_calls.py            # API integration tests
│   │
│   ├── fixtures/                        # Test data
│   │   ├── __init__.py
│   │   ├── sample_conversations.json    # Sample data
│   │   └── sample_images/               # Test images
│   │
│   └── conftest.py                      # Pytest configuration
│
├── docs/                                # Documentation
│   ├── api_reference.md                 # API documentation
│   ├── architecture.md                  # System architecture
│   ├── deployment.md                    # Deployment guide
│   └── contributing.md                  # Contribution guidelines
│
├── uploads/                             # User file uploads (created at runtime)
│   └── .gitkeep                         # Keep directory in git
│
├── output/                              # [Legacy] Search output files
│   └── .gitkeep
│
├── .env                                 # Environment variables (NOT in git)
├── .env.example                         # Example env file (in git)
├── .gitignore                           # Git ignore rules
├── requirements.txt                     # Python dependencies
├── README.md                            # Project overview
├── PROJECT_PLAN.md                      # Detailed implementation guide ✅
├── QUICK_START.md                       # Quick reference guide ✅
├── DIRECTORY_STRUCTURE.md               # This file ✅
├── CHANGELOG.md                         # [Optional] Version history
│
├── tavily_search.py                     # [Legacy] Original script (keep for reference)
│
└── chat_history.db                      # SQLite database (created at runtime)
```

## 🚀 Quick Setup Commands

### 1. Create All Directories

Run these commands from your project root:

```bash
# Backend directories
mkdir -p backend/{config,core,providers,tools,utils,database}

# Frontend directories
mkdir -p frontend/streamlit/{components,styles}

# Test directories
mkdir -p tests/{unit,integration,fixtures/sample_images}

# Other directories
mkdir -p docs uploads

# Create all __init__.py files
touch backend/__init__.py
touch backend/config/__init__.py
touch backend/core/__init__.py
touch backend/providers/__init__.py
touch backend/tools/__init__.py
touch backend/utils/__init__.py
touch backend/database/__init__.py
touch frontend/__init__.py
touch frontend/streamlit/__init__.py
touch frontend/streamlit/components/__init__.py
touch tests/__init__.py
touch tests/unit/__init__.py
touch tests/integration/__init__.py
touch tests/fixtures/__init__.py

# Create .gitkeep files
touch uploads/.gitkeep
touch output/.gitkeep
```

### 2. Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Environment variables
.env
.env.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3
chat_history.db

# Uploads
uploads/*
!uploads/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Logs
*.log

# Testing
.pytest_cache/
.coverage
htmlcov/

# Streamlit
.streamlit/secrets.toml
EOF
```

## 📦 File Creation Order

Follow this order when implementing (matches PROJECT_PLAN.md):

### Phase 1: Foundation (Week 1)
1. ✅ Create directory structure (above)
2. `backend/config/settings.py`
3. `backend/config/models.yaml`
4. `backend/providers/base.py`
5. `backend/providers/openai_provider.py`
6. `backend/providers/gemini_provider.py`
7. `backend/core/model_factory.py`

### Phase 2: Database (Week 2)
8. `backend/database/models.py`
9. `backend/database/operations.py`
10. `backend/core/chat_manager.py`

### Phase 3: Frontend (Week 2)
11. `frontend/streamlit/app.py`
12. `frontend/streamlit/components/sidebar.py`
13. `frontend/streamlit/components/chat.py`

### Phase 4: Multimodal (Week 3)
14. `backend/utils/file_handler.py`
15. `frontend/streamlit/components/file_upload.py`

### Phase 5: Tools (Week 3)
16. `backend/tools/base.py`
17. `backend/tools/tavily_search.py`

### Phase 6: Testing (Week 4)
18. `tests/conftest.py`
19. `tests/unit/test_providers.py`
20. `tests/unit/test_chat_manager.py`
21. etc.

## 📋 Verification Checklist

After creating the structure, verify:

```bash
# Check directory structure
tree -L 3 -I '__pycache__|*.pyc|.git'

# Verify __init__.py files exist
find backend frontend tests -name "__init__.py" -type f

# Check file count
find backend -type f -name "*.py" | wc -l
# Should have at least 12+ files after Phase 1
```

## 🎯 What Each Directory Does

### `backend/config/`
**Purpose**: Centralized configuration management
- Environment variables
- Model definitions
- Settings validation

### `backend/providers/`
**Purpose**: LLM API integrations
- Abstract interface for all providers
- Concrete implementations (OpenAI, Gemini, Claude)
- Token counting
- Message formatting

### `backend/core/`
**Purpose**: Business logic
- Conversation management
- Provider factory
- Message handling

### `backend/tools/`
**Purpose**: Function calling capabilities
- Web search (Tavily)
- Code execution
- Calculator
- Custom tools

### `backend/utils/`
**Purpose**: Helper functions
- File processing
- Image optimization
- Token utilities
- Logging

### `backend/database/`
**Purpose**: Data persistence
- SQLAlchemy models
- CRUD operations
- Query builders

### `frontend/streamlit/`
**Purpose**: User interface
- Main app entry point
- UI components
- Custom styling

### `tests/`
**Purpose**: Quality assurance
- Unit tests (individual functions)
- Integration tests (full flows)
- Test fixtures and data

## 🔄 Migration from Old Structure

If you want to preserve the old functionality:

1. **Keep** `tavily_search.py` as reference
2. **Extract** search logic → `backend/tools/tavily_search.py`
3. **Extract** OpenAI code → `backend/providers/openai_provider.py`
4. **Extract** Gemini code → `backend/providers/gemini_provider.py`
5. **Keep** `output/` directory for legacy exports

## 🚦 Current vs. New Structure

### Before (Current):
```
tavily_search_wraper/
├── README.md
├── requirements.txt
└── tavily_search.py
```

### After (Complete):
```
tavily_search_wraper/
├── backend/          # 📦 Backend logic (20+ files)
├── frontend/         # 🎨 UI layer (5+ files)
├── tests/            # ✅ Test suite (10+ files)
├── docs/             # 📚 Documentation
├── uploads/          # 📎 User uploads
├── tavily_search.py  # 🔙 Legacy (reference)
└── chat_history.db   # 💾 Database
```

## 📝 Notes

- **__init__.py**: Required for Python packages (can be empty)
- **.gitkeep**: Keeps empty directories in git
- **Legacy files**: Keep `tavily_search.py` for reference during migration
- **Database**: `chat_history.db` created automatically on first run
- **Uploads**: Directory created by app when first file is uploaded

## ⚡ One-Command Setup

Want to create everything at once? Save this as `setup_structure.sh`:

```bash
#!/bin/bash

echo "Creating directory structure..."

# Backend
mkdir -p backend/{config,core,providers,tools,utils,database}

# Frontend
mkdir -p frontend/streamlit/{components,styles}

# Tests
mkdir -p tests/{unit,integration,fixtures/sample_images}

# Other
mkdir -p docs uploads

# Create __init__.py files
for dir in backend backend/config backend/core backend/providers \
            backend/tools backend/utils backend/database frontend \
            frontend/streamlit frontend/streamlit/components \
            tests tests/unit tests/integration tests/fixtures; do
    touch "$dir/__init__.py"
done

# Create .gitkeep files
touch uploads/.gitkeep
touch output/.gitkeep

echo "✅ Directory structure created!"
echo "Next: Create .env file and start implementing Phase 1"
```

Run it:
```bash
chmod +x setup_structure.sh
./setup_structure.sh
```

---

**Now you're ready to start implementing! Go to PROJECT_PLAN.md Phase 1, Task 1.1** 🚀

