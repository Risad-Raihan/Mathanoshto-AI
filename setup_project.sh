#!/bin/bash
# Personal LLM Assistant - Automated Project Setup Script

set -e  # Exit on error

echo "======================================"
echo "Personal LLM Assistant - Setup Script"
echo "======================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Create directory structure
echo -e "${BLUE}Step 1: Creating directory structure...${NC}"

# Backend directories
mkdir -p backend/{config,core,providers,tools,utils,database}

# Frontend directories
mkdir -p frontend/streamlit/{components,styles}

# Test directories
mkdir -p tests/{unit,integration,fixtures/sample_images}

# Other directories
mkdir -p docs uploads

echo -e "${GREEN}✓ Directories created${NC}"

# Step 2: Create __init__.py files
echo -e "\n${BLUE}Step 2: Creating Python package markers...${NC}"

# List of directories that need __init__.py
init_dirs=(
    "backend"
    "backend/config"
    "backend/core"
    "backend/providers"
    "backend/tools"
    "backend/utils"
    "backend/database"
    "frontend"
    "frontend/streamlit"
    "frontend/streamlit/components"
    "tests"
    "tests/unit"
    "tests/integration"
    "tests/fixtures"
)

for dir in "${init_dirs[@]}"; do
    touch "$dir/__init__.py"
    echo "  Created $dir/__init__.py"
done

echo -e "${GREEN}✓ Package markers created${NC}"

# Step 3: Create .gitkeep files
echo -e "\n${BLUE}Step 3: Creating .gitkeep files...${NC}"

touch uploads/.gitkeep
touch output/.gitkeep

echo -e "${GREEN}✓ .gitkeep files created${NC}"

# Step 4: Create .gitignore
echo -e "\n${BLUE}Step 4: Creating .gitignore...${NC}"

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

# Output
output/*
!output/.gitkeep

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

# OS
Thumbs.db
EOF

echo -e "${GREEN}✓ .gitignore created${NC}"

# Step 5: Create .env.example
echo -e "\n${BLUE}Step 5: Creating .env.example...${NC}"

cat > .env.example << 'EOF'
# Personal LLM Assistant - Environment Variables
# Copy this file to .env and fill in your API keys

# Tavily API (Required for web search tool)
TAVILY_API_KEY=your_tavily_api_key_here

# OpenAI API (Optional - for OpenAI models)
OPENAI_API_KEY=your_openai_api_key_here
# Optional: Custom OpenAI-compatible endpoint (e.g., Azure OpenAI)
OPENAI_BASE_URL=

# Google Gemini API (Optional - for Gemini models)
GEMINI_API_KEY=your_gemini_api_key_here

# Anthropic API (Optional - for Claude models, coming soon)
ANTHROPIC_API_KEY=

# Database (Default uses SQLite in project directory)
DATABASE_URL=sqlite:///./chat_history.db

# Application Settings
DEBUG_MODE=false
APP_NAME=Personal LLM Assistant

# File Upload Settings
MAX_UPLOAD_SIZE_MB=10
UPLOAD_DIR=uploads
EOF

echo -e "${GREEN}✓ .env.example created${NC}"

# Step 6: Check if .env exists
echo -e "\n${BLUE}Step 6: Checking environment file...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your API keys!${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Step 7: Summary
echo -e "\n${GREEN}======================================"
echo "Setup Complete! ✅"
echo "======================================${NC}"
echo ""
echo "Directory structure created:"
echo "  📦 backend/     - Backend logic (providers, tools, database)"
echo "  🎨 frontend/    - Streamlit UI components"
echo "  ✅ tests/       - Test suite"
echo "  📚 docs/        - Documentation"
echo "  📎 uploads/     - User file uploads"
echo ""
echo "Next steps:"
echo "  1. Edit .env file with your API keys"
echo "  2. Install dependencies:"
echo "     pip install -r requirements.txt"
echo "  3. Follow PROJECT_PLAN.md to implement features"
echo "  4. Start with Phase 1, Task 1.2 (Configuration)"
echo ""
echo "Quick reference:"
echo "  📖 PROJECT_PLAN.md       - Detailed implementation guide"
echo "  ⚡ QUICK_START.md        - Quick reference"
echo "  📁 DIRECTORY_STRUCTURE.md - Structure explanation"
echo ""
echo -e "${YELLOW}Happy coding! 🚀${NC}"

