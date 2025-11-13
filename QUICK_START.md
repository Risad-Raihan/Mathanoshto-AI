# 🚀 Mathanoshto AI - Quick Start Guide

**Personal AI Assistant with Multi-Model Support**

---

## 📦 Setup with Docker (Recommended)

### Prerequisites
- Docker & Docker Compose installed
- 8GB+ RAM recommended
- Internet connection

### ✅ Cross-Platform Support
**Works on:** Linux, macOS, Windows  
Docker images are platform-independent. Tested on:
- ✅ **Linux** (Arch, Ubuntu, Debian)
- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Windows** (with Docker Desktop)

### 1️⃣ Start the Application
```bash
docker-compose up -d
```

### 2️⃣ Access the App
Open your browser: **http://localhost:8501**

### 3️⃣ First-Time Setup
1. **Sign Up** - Create your account:
   - Click "✨ Sign Up" tab
   - Enter your username, email, and password
   - Click "Create Account"

2. **Sign In** - Login with your credentials:
   - Switch to "🔐 Sign In" tab
   - Enter your credentials
   - Check "Remember me" to stay logged in

3. **Add Your API Keys** (Click **👤 Profile** → **API Keys**):
   - **OpenAI**: Get from https://platform.openai.com/api-keys
   - **Google Gemini**: Get from https://aistudio.google.com/app/apikey
   - **Anthropic**: Get from https://console.anthropic.com/
   - **Tavily** (Search): Get from https://tavily.com/

3. **Start Chatting!** 🎉

---

## 💡 Key Features

### 🤖 Multi-Model AI
- **OpenAI**: GPT-4o, GPT-4o-mini
- **Gemini**: Gemini 2.5 Flash
- **Anthropic**: Claude Sonnet 4.0, 3.7, 3.5 Haiku

### 🛠️ Built-in Tools
- 🔍 **Web Search** (Tavily) with image previews
- 🖼️ **Vision AI** - Upload & analyze images
- 📊 **Data Analysis** - CSV, Excel visualization
- 📄 **RAG System** - Upload PDFs, DOCX for context
- 🧠 **Long-Term Memory** - AI remembers your preferences
- 🤖 **Custom Agents** - Create specialized AI personas

---

## 🎯 Quick Usage Tips

### Chat with AI
1. Select **provider** & **model** from sidebar
2. Type your message
3. Enable tools (Tavily Search, etc.) as needed

### Upload Files
- **Images**: Drag & drop for vision AI analysis
- **Documents**: PDF/DOCX for RAG-powered chat
- Max file size: **10MB**

### Create Custom Agent
1. Go to **🤖 AI Agents** tab
2. Click **➕ Create Agent**
3. Set system prompt, tools, temperature
4. Use in chat by selecting from sidebar

### Manage Memory
1. Go to **🧠 Memories** tab
2. Add facts, preferences, context
3. AI automatically retrieves relevant memories

---

## 🔧 Maintenance

### View Logs
```bash
docker-compose logs -f
```

### Stop Application
```bash
docker-compose down
```

### Restart Application
```bash
docker-compose restart
```

### Update to Latest Version
```bash
git pull origin developer
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup Data
```bash
# Backup database and uploads
tar -czf backup-$(date +%Y%m%d).tar.gz data/ uploads/
```

---

## ⚠️ Troubleshooting

### Port Already in Use
```bash
# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use 8502 instead
```

### Out of Memory
- Increase Docker memory limit to 8GB+
- Close unused applications

### API Keys Not Working
- Verify keys are correct (no spaces)
- Check API quotas/billing
- Try re-adding the key

---

## 👥 Team Members
**Risad • Mazed • Mrittika • Nafis • Rafi**

---

## 📞 Support
For issues, contact: **Team Administrator**

---

**Built with ❤️ for seamless AI interactions**

