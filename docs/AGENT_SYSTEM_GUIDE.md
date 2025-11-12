# 🤖 AI Agent System - Complete Guide

## Table of Contents
1. [Overview](#overview)
2. [What Are AI Agents?](#what-are-ai-agents)
3. [Pre-defined Agents](#pre-defined-agents)
4. [Setup & Installation](#setup--installation)
5. [Using Agents](#using-agents)
6. [Creating Custom Agents](#creating-custom-agents)
7. [Agent Management](#agent-management)
8. [Best Practices](#best-practices)
9. [Technical Architecture](#technical-architecture)
10. [Troubleshooting](#troubleshooting)

---

## Overview

The AI Agent System transforms your AI assistant into a team of specialized experts. Each agent has:
- **Unique personality & expertise** defined by custom system prompts
- **Specialized knowledge** in specific domains (research, coding, product, etc.)
- **Optimized settings** (temperature, tokens) for their role
- **Tool permissions** controlling what they can access
- **Usage tracking** to see which agents are most helpful

---

## What Are AI Agents?

Think of agents as different "hats" your AI can wear. Instead of one general-purpose assistant, you get:

- 🔬 **Research Agent** - Analyzes papers, summarizes research
- 👨‍💻 **Code Reviewer** - Reviews code for bugs and best practices
- 💡 **Product Advisor** - Brainstorms features, validates ideas
- 🏗️ **Architecture Expert** - Designs scalable systems
- 🤖 **ML Model Advisor** - Helps with model training and debugging
- 🐛 **Debugging Assistant** - Systematic bug hunting
- 📝 **Technical Writer** - Creates documentation
- 🎯 **Prompt Engineer** - Optimizes LLM prompts
- 📊 **Data Analyst** - Analyzes data, creates insights
- 🚀 **Startup Advisor** - Business strategy and fundraising

---

## Pre-defined Agents

### 🔬 Research Agent
**Category:** Research  
**Temperature:** 0.3 (focused)  
**Expertise:** AI research paper analysis  

**When to use:**
- Analyzing academic papers
- Summarizing research findings
- Comparing different methodologies
- Literature reviews
- Staying current with AI/ML advances

**Tools:** Web Search, PDF Reader, arXiv Search

**Example prompts:**
```
"Summarize the key findings from the Attention Is All You Need paper"
"Compare transformer architectures: BERT vs GPT vs T5"
"What are the latest breakthroughs in diffusion models?"
```

---

### 👨‍💻 Code Reviewer
**Category:** Development  
**Temperature:** 0.2 (very focused)  
**Expertise:** Code quality, security, best practices  

**When to use:**
- Reviewing pull requests
- Finding bugs and security issues
- Improving code maintainability
- Checking best practices
- Performance optimization

**Tools:** Code Execution, Linter, Security Scanner

**Example prompts:**
```
"Review this Python function for bugs and improvements"
"Check this API endpoint for security vulnerabilities"
"Suggest refactoring for better performance"
```

---

### 💡 Product Discussion Partner
**Category:** Product  
**Temperature:** 0.8 (creative)  
**Expertise:** Product strategy, UX, market analysis  

**When to use:**
- Brainstorming features
- Validating product ideas
- Competitive analysis
- Defining user stories
- Planning product roadmaps

**Tools:** Web Search, Diagram Generator, Market Research

**Example prompts:**
```
"Help me design a user onboarding flow for an AI app"
"What features should an AI code assistant have?"
"Analyze competitors in the AI assistant space"
```

---

### 🏗️ Architecture Advisor
**Category:** Development  
**Temperature:** 0.4  
**Expertise:** System design, scalability, infrastructure  

**When to use:**
- Designing system architecture
- Scaling applications
- Cloud infrastructure decisions
- Database design
- Microservices vs monolith

**Tools:** Diagram Generator, Architecture Patterns, Cloud Calculator

**Example prompts:**
```
"Design a scalable architecture for a real-time chat app"
"Should I use microservices or a monolith for my MVP?"
"How do I handle 10M concurrent users?"
```

---

### 🤖 ML Model Advisor
**Category:** Data/AI  
**Temperature:** 0.3  
**Expertise:** Model training, hyperparameter tuning, ML debugging  

**When to use:**
- Choosing the right model
- Training strategies
- Debugging ML pipelines
- Hyperparameter optimization
- Model evaluation

**Tools:** Code Execution, Jupyter Notebook, Data Visualization

**Example prompts:**
```
"My model is overfitting - how do I fix it?"
"Which model should I use for sentiment analysis?"
"How do I handle class imbalance in my dataset?"
```

---

### 🐛 Debugging Assistant
**Category:** Development  
**Temperature:** 0.2  
**Expertise:** Systematic debugging, error analysis  

**When to use:**
- Finding and fixing bugs
- Analyzing error logs
- Debugging complex issues
- Performance problems
- Troubleshooting

**Tools:** Code Execution, Log Analyzer, Profiler

**Example prompts:**
```
"Help me debug this error: AttributeError: 'NoneType' object..."
"Why is my API taking 5 seconds to respond?"
"Analyze these error logs and find the root cause"
```

---

### 📝 Technical Writer
**Category:** Documentation  
**Temperature:** 0.4  
**Expertise:** API docs, README files, tutorials  

**When to use:**
- Writing documentation
- Creating tutorials
- API reference docs
- README files
- Architecture decision records

**Tools:** Markdown Formatter, Diagram Generator

**Example prompts:**
```
"Write API documentation for this endpoint"
"Create a README for my Python project"
"Write a tutorial on using this library"
```

---

### 🎯 Prompt Engineer
**Category:** Data/AI  
**Temperature:** 0.5  
**Expertise:** LLM prompt optimization  

**When to use:**
- Crafting effective prompts
- Optimizing LLM outputs
- Few-shot learning
- Chain-of-thought prompting
- Prompt testing

**Tools:** Prompt Tester, Model Comparison, Token Counter

**Example prompts:**
```
"Optimize this prompt for better classification accuracy"
"Create a few-shot prompt for extracting structured data"
"How do I get more consistent JSON outputs from GPT-4?"
```

---

### 📊 Data Analyst
**Category:** Data  
**Temperature:** 0.3  
**Expertise:** Data analysis, visualization, statistics  

**When to use:**
- Exploratory data analysis
- Creating visualizations
- Statistical analysis
- Data cleaning
- Generating insights

**Tools:** Data Visualization, Statistical Analysis, SQL Query

**Example prompts:**
```
"Analyze this CSV file and find key insights"
"Create visualizations for sales data"
"What statistical tests should I use for this data?"
```

---

### 🚀 Startup Advisor
**Category:** Product/Business  
**Temperature:** 0.7  
**Expertise:** Business strategy, fundraising, GTM  

**When to use:**
- Business strategy
- Fundraising advice
- Go-to-market planning
- Pitch deck feedback
- Product-market fit

**Tools:** Web Search, Market Research, Financial Calculator

**Example prompts:**
```
"Help me create a pitch deck for my AI startup"
"What should my go-to-market strategy be?"
"How do I price my SaaS product?"
```

---

## Setup & Installation

### Prerequisites
- Python 3.8+
- PostgreSQL or SQLite
- Streamlit
- All dependencies from `requirements.txt`

### Installation Steps

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Run Setup Script**
```bash
python setup_agent_system.py
```

This will:
- Create necessary database tables
- Load 10 pre-defined agents
- Verify the setup
- Run basic tests

3. **Start the Application**
```bash
streamlit run frontend/streamlit/app.py
```

### Verification

After setup, you should see:
```
✨ Agent System Setup Complete!

🎉 You can now:
   1. Select agents from the sidebar
   2. Create custom agents
   3. Use specialized agents for tasks
```

---

## Using Agents

### Selecting an Agent

1. **Open the sidebar** in the Streamlit app
2. **Find the "🤖 AI Agent" section**
3. **Select an agent** from the dropdown
4. **View agent info** by expanding the info section
5. **Start chatting** - the agent is now active!

### Agent Indicator

When an agent is active, you'll see:
```
🔬 Agent: Research Agent
```

This appears above AI responses to remind you which agent you're talking to.

### Switching Agents

You can switch agents at any time:
1. Select a different agent from the dropdown
2. The new agent takes effect immediately
3. Previous conversation history is preserved

### Manual Mode

Select "⚙️ Custom Settings (Manual)" to use your own custom settings instead of an agent.

---

## Creating Custom Agents

### Why Create Custom Agents?

- **Hyper-specialized** for your specific workflows
- **Team-specific** knowledge and terminology
- **Company context** built into system prompts
- **Unique tool combinations** for your use case

### Step-by-Step Guide

1. **Navigate to Agent Manager**
   - Click "✏️ Manage Agents" in the sidebar
   - Go to the "➕ Create Agent" tab

2. **Basic Information**
   ```
   Name: Django Expert
   Emoji: 🐍
   Description: Specialized in Django web development
   ```

3. **System Prompt** (Most Important!)
   ```
   You are a Django Expert with 10+ years of experience.
   
   Your expertise:
   - Django ORM and database optimization
   - REST API design with Django REST Framework
   - Authentication and permissions
   - Celery for async tasks
   - Deployment and scaling
   
   When answering:
   1. Provide Django-specific best practices
   2. Include code examples with explanations
   3. Consider security implications
   4. Suggest testing approaches
   5. Reference Django documentation
   
   Always use Django 4.2+ features and conventions.
   ```

4. **Settings**
   - **Category:** Development
   - **Tone:** Technical
   - **Temperature:** 0.3 (focused for code)
   - **Max Tokens:** 2000

5. **Tool Permissions**
   - ✅ Web Search (for documentation)
   - ✅ Code Execution
   - ❌ YouTube (not needed)
   - ❌ Data Analyzer (not needed)

6. **Tags**
   ```
   python, django, backend, api, orm
   ```

7. **Click "✨ Create Agent"**

### System Prompt Tips

**Good System Prompt:**
```
You are a [SPECIFIC ROLE] with [EXPERIENCE/EXPERTISE].

Your core responsibilities:
- [Specific task 1]
- [Specific task 2]
- [Specific task 3]

When responding:
1. [Guideline 1]
2. [Guideline 2]
3. [Guideline 3]

Always [important principle or constraint].
```

**Bad System Prompt:**
```
You are helpful and smart. Answer questions well.
```

**Key Elements:**
1. **Specific role** - Not just "expert" but "Senior Backend Engineer"
2. **Explicit expertise** - List concrete skills and knowledge areas
3. **Clear guidelines** - How should they respond?
4. **Examples** - Show the format or style you want
5. **Constraints** - What should they avoid or always do?

---

## Agent Management

### Viewing All Agents

**Agent Manager → 📋 All Agents Tab**

Features:
- Filter by type (System/Custom)
- Filter by category
- View agent details
- Use agent directly
- Edit/delete custom agents

### Editing Custom Agents

**Agent Manager → ✏️ Edit Agent Tab**

1. Select the agent to edit
2. Modify any settings
3. Add a change summary (optional)
4. Save changes

**Version History:**  
Each edit creates a new version, allowing you to track changes over time.

### Deleting Agents

**Note:** You can only delete custom agents you created.

1. Navigate to the agent
2. Click "🗑️ Delete"
3. Confirm deletion

### Agent Statistics

**Agent Manager → 📊 Agent Stats Tab**

View:
- Total agents (system + custom)
- Most used agents
- Usage counts
- Average ratings
- Category distribution

---

## Best Practices

### Choosing the Right Agent

| Task | Best Agent | Why |
|------|-----------|-----|
| Literature review | Research Agent | Analytical, references sources |
| Code review | Code Reviewer | Security-focused, best practices |
| Feature brainstorming | Product Partner | Creative, user-first thinking |
| System design | Architecture Advisor | Scalability expertise |
| Bug fixing | Debugging Assistant | Systematic problem-solving |
| Writing docs | Technical Writer | Clear, structured documentation |

### Agent Combinations

For complex tasks, **switch agents** as needed:

1. **Product Partner** → brainstorm feature
2. **Architecture Advisor** → design system
3. **Code Reviewer** → implement & review
4. **Technical Writer** → document it

### Creating Effective Prompts

**For Code Agents (low temperature):**
```
"Review this authentication endpoint for security issues"
```

**For Creative Agents (high temperature):**
```
"Brainstorm 10 innovative features for an AI code editor"
```

**For Analytical Agents (medium temperature):**
```
"Analyze the trade-offs between MongoDB and PostgreSQL for my use case"
```

### Custom Agent Tips

1. **Start specific** - "Python Testing Expert" not "Developer"
2. **Test iteratively** - Create, test, refine system prompt
3. **Set appropriate temperature**:
   - 0.1-0.3: Code, facts, precision tasks
   - 0.4-0.7: Balanced, general use
   - 0.8-1.5: Creative, brainstorming

4. **Limit tools** - Only enable what the agent needs
5. **Use tags** - Makes agents easy to find

---

## Technical Architecture

### Database Schema

**`agents` Table:**
```sql
- id (primary key)
- name, emoji, description
- system_prompt
- temperature, max_tokens, top_p
- tone, expertise_level, response_format
- allowed_tools (JSON)
- category, tags (JSON)
- version, is_system, is_active
- created_by (user_id)
- usage_count, rating
- created_at, updated_at
```

**`agent_versions` Table:**
```sql
- id (primary key)
- agent_id (foreign key)
- version, system_prompt
- settings (JSON)
- change_summary
- changed_by (user_id)
- created_at
```

**`agent_sessions` Table:**
```sql
- id (primary key)
- agent_id (foreign key)
- conversation_id (foreign key)
- user_id (foreign key)
- started_at, ended_at
- message_count
- rating, feedback
```

### Agent Flow

```
1. User selects agent in sidebar
   ↓
2. Agent settings loaded (system_prompt, temperature, tools)
   ↓
3. Agent session started (tracked in database)
   ↓
4. User sends message
   ↓
5. Agent system prompt + memory context injected
   ↓
6. Agent tools filtered by permissions
   ↓
7. LLM called with agent settings
   ↓
8. Response returned with agent indicator
   ↓
9. Session updated (message count++)
```

### System Prompt Injection

```python
# Agent's system prompt
agent_prompt = agent.system_prompt

# Memory context (if available)
memory_context = retrieve_relevant_memories(user_id, query)

# Combined prompt
final_prompt = agent_prompt + "\n\n" + memory_context
```

### Tool Permission Filtering

```python
allowed_tools = agent.allowed_tools  # e.g., ["web_search", "code_execution"]

# Filter enabled tools
if "web_search" not in allowed_tools:
    settings["use_tavily"] = False

if "code_execution" not in allowed_tools:
    settings["use_code_execution"] = False
```

---

## Troubleshooting

### Agents Not Showing in Sidebar

**Cause:** Agents not initialized  
**Solution:**
```bash
python setup_agent_system.py
```

### Agent Not Using Correct Temperature

**Cause:** Manual settings override  
**Solution:** Ensure agent is selected (not "Custom Settings")

### Agent Can't Access Tools

**Cause:** Tool not in `allowed_tools` list  
**Solution:** Edit agent and add the tool permission

### Custom Agent Creation Fails

**Cause:** Duplicate name  
**Solution:** Use a unique agent name

### "Agent Session Error"

**Cause:** Database session issue  
**Solution:** Restart the application

### Agent Responses Not Specialized Enough

**Cause:** Weak system prompt  
**Solution:** Improve system prompt with:
- More specific expertise
- Clear guidelines
- Concrete examples
- Explicit constraints

---

## Advanced Features

### Agent Ratings & Feedback

(Coming Soon)
- Rate agent responses 1-5 stars
- Provide feedback on agent performance
- Track agent effectiveness over time

### Agent Marketplace

(Coming Soon)
- Share custom agents with other users
- Browse community-created agents
- Import agents from marketplace

### Team Agent Libraries

(Coming Soon)
- Organization-wide agent library
- Shared agent templates
- Team-specific agents

### Agent Analytics

(Coming Soon)
- Usage heatmaps
- Success metrics
- A/B testing agents
- Performance tracking

---

## FAQ

**Q: Can I use multiple agents in the same conversation?**  
A: Yes! Switch agents anytime. Each message uses the currently selected agent.

**Q: Will agents remember previous conversations?**  
A: Agents use the memory system, so they access relevant memories across conversations.

**Q: Can I modify system agents?**  
A: No, system agents are read-only. Create a custom agent based on a system agent instead.

**Q: How many custom agents can I create?**  
A: Unlimited! Create as many as you need.

**Q: Do agents work with all LLM providers?**  
A: Yes! Agents work with OpenAI, Gemini, Anthropic, and any supported provider.

**Q: Can agents use tools?**  
A: Yes, based on their `allowed_tools` permissions.

---

## Resources

- **System Prompt Examples:** `/docs/agent_prompt_examples.md`
- **API Reference:** `/docs/agent_api.md`
- **Video Tutorial:** [Coming Soon]
- **Community Agents:** [Coming Soon]

---

## Support

Having issues? Need help?

1. Check this guide
2. Run the setup script again
3. Check logs for error messages
4. Open an issue on GitHub

---

**Built with ❤️ by the Mathanoshto AI Team**  
*Making AI assistants actually intelligent, one agent at a time.*

