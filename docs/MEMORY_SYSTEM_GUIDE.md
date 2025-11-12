# Memory System - Complete Guide

## 🧠 Overview

The Context Memory System gives your AI assistant **long-term memory** - it remembers important facts, preferences, and context across all your conversations. Think of it as giving your AI a persistent memory that improves over time.

## ✨ Key Features

### 🎯 What Makes It Special?

1. **Semantic Search** - Find memories by meaning, not just keywords
2. **Automatic Extraction** - AI automatically identifies important information
3. **Smart Context Injection** - Relevant memories are automatically added to conversations
4. **Multiple Memory Types** - Organized categories for different kinds of information
5. **Importance Scoring** - Prioritizes what matters most
6. **Version History** - Track changes to memories over time
7. **Conflict Resolution** - Handles contradicting information intelligently

### 📊 Memory Types

| Type | Icon | Description | Examples |
|------|------|-------------|----------|
| **Personal Info** | 👤 | Name, age, location, occupation | "User's name is Sarah", "Lives in Seattle" |
| **Preferences** | ⭐ | Likes, dislikes, interests | "Loves Italian food", "Prefers Python over JavaScript" |
| **Facts** | 💡 | Important knowledge | "Has a cat named Whiskers", "Works at Tech Corp" |
| **Tasks** | ✅ | Things to remember | "Needs to submit report by Friday" |
| **Goals** | 🎯 | Aspirations, objectives | "Learning machine learning", "Planning trip to Japan" |
| **Relationships** | 👥 | People information | "Best friend is Alex", "Manager is John" |
| **Past Discussions** | 💬 | Conversation context | "Discussed React yesterday" |

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**New packages added:**
- `chromadb>=0.4.0` - Vector database
- `sentence-transformers>=2.2.0` - Local embeddings
- `torch>=2.0.0` - Deep learning framework

### Step 2: Initialize Memory Tables

```bash
cd /home/risad/projects/tavily_search_wraper
python -c "from backend.database.memory_operations import init_memory_tables; init_memory_tables()"
```

### Step 3: Access Memory System

1. **Start the app**: `streamlit run frontend/streamlit/app.py`
2. **Log in** to your account
3. Click the **🧠** icon in the sidebar
4. Explore the Memory System!

## 📖 Using the Memory System

### Creating Memories Manually

**Best for**: Important facts you want the AI to always remember

1. Go to **Memory System** (🧠 icon)
2. Click **"Add Memory"** tab
3. Fill in the details:
   - **Content**: What to remember
   - **Type**: Category (personal_info, preference, etc.)
   - **Importance**: 0-1 score (higher = more important)
   - **Tags**: For organization
   - **Pin**: Always include in context
4. Click **"Save Memory"**

**Example:**
```
Content: "Prefers dark mode for all applications"
Type: Preference
Category: ui_preferences
Tags: dark_mode, ui
Importance: 0.7
Pin: Yes
```

### Automatic Memory Extraction

**Best for**: Let AI learn from your conversations automatically

The system automatically extracts important information as you chat!

**How it works:**
1. Have natural conversations
2. AI identifies important facts, preferences, and context
3. Memories are created and stored automatically
4. No manual input needed!

**What gets extracted:**
- ✅ Personal details you share
- ✅ Your preferences and interests
- ✅ Important facts and context
- ✅ Tasks and goals you mention
- ❌ Casual small talk
- ❌ Temporary information

### Searching Memories

**Semantic search** finds memories by meaning, not exact words!

**Example searches:**
- "What does the user like to eat?" → Finds food preferences
- "Where does the user work?" → Finds occupation info
- "What programming languages does the user know?" → Finds skills

**How to search:**
1. Go to **"Search"** tab
2. Enter your question or description
3. Optionally filter by type
4. Click **"Search"**
5. Results show similarity scores (higher = more relevant)

### Managing Memories

#### View All Memories
- **"All Memories"** tab shows everything
- Filter by type, sort by importance/date/access
- See detailed metadata

#### Edit Memories
- Click ✏️ to edit
- Update content, importance, tags
- Changes are versioned (history preserved)

#### Pin Important Memories
- Click 📌 to pin
- Pinned memories are **always** included in AI context
- Great for critical information

#### Verify Memories
- Click ✅ to verify
- Marks information as confirmed accurate
- Helps AI trust the information more

#### Delete Memories
- Click 🗑️ to delete
- Soft delete by default (can be restored)
- Hard delete in settings (permanent)

## 🔧 Advanced Features

### Memory Importance & Decay

Memories have **importance scores** that decay over time:

**Importance Levels:**
- **🔴 High (0.8-1.0)**: Critical information, always relevant
- **🟡 Medium (0.5-0.8)**: Important but context-dependent
- **⚪ Low (0-0.5)**: Nice to know, rarely used

**Decay Algorithm:**
- New memories maintain full importance
- After 30 days, importance gradually decreases
- Frequently accessed memories decay slower
- Pinned memories never decay

### Conflict Resolution

When new information contradicts existing memories:

1. **Detection**: System finds similar memories
2. **Analysis**: AI determines if there's a conflict
3. **Resolution Options**:
   - **Supersede**: New replaces old
   - **Merge**: Combine information
   - **Keep Both**: No real conflict
4. **Version History**: Old info is preserved, not lost

### Memory Injection into Conversations

Relevant memories are **automatically** injected into AI context:

**How it works:**
1. You send a message
2. System searches for relevant memories
3. Top N memories are added to system prompt
4. AI responds with full context

**Configuration:**
- Max memories per request: 3-20 (default: 10)
- Minimum relevance: 0.6 similarity score
- Pinned memories: Always included
- High-importance memories: Prioritized

### Memory Relationships

Memories can be linked to show relationships:

**Relationship Types:**
- `related_to`: General connection
- `contradicts`: Conflicting information
- `supports`: Reinforcing information
- `supersedes`: Newer version
- `derived_from`: Inferred from another
- `part_of`: Component of larger context

## 💡 Best Practices

### For Manual Memory Creation

1. **Be Specific**: "Prefers Python 3.11+" vs "Likes Python"
2. **Use Tags**: Helps with organization and search
3. **Set Appropriate Importance**: Not everything is critical
4. **Pin Wisely**: Too many pinned memories clutter context
5. **Add Context**: Include why it matters

### For Automatic Extraction

1. **Enable in Settings**: Turn on automatic extraction
2. **Natural Conversations**: Just chat normally
3. **Be Explicit**: "I prefer..." vs implicit preferences
4. **Verify Important Info**: Check and verify key memories
5. **Review Regularly**: Check what's been extracted

### For Search

1. **Ask Questions**: "What does user like?" works better than "preferences"
2. **Be Descriptive**: More context = better results
3. **Use Filters**: Narrow by type when needed
4. **Check Similarity**: 80%+ is very relevant, 60-80% is moderate
5. **Try Different Phrasings**: If not found, rephrase

### For Organization

1. **Use Categories**: Group related memories
2. **Tag Consistently**: Use same tags across memories
3. **Review Monthly**: Clean up outdated memories
4. **Verify Key Info**: Mark confirmed facts as verified
5. **Pin Critical Items**: Things AI should always know

## 🎓 Example Workflows

### Workflow 1: Personal Assistant Setup

**Goal**: Set up AI as your personal assistant

```markdown
1. Add Personal Info:
   - Name and preferred address
   - Location and timezone
   - Work schedule and availability
   
2. Add Preferences:
   - Communication style ("formal" vs "casual")
   - Response length preference
   - Topics of interest
   
3. Add Tasks:
   - Recurring reminders
   - Important deadlines
   - Goals to track

4. Configure Settings:
   - Enable auto-extraction
   - Auto-inject memories: ON
   - Max memories: 15
```

### Workflow 2: Learning Companion

**Goal**: AI that remembers your learning progress

```markdown
1. Initial Setup:
   - Current skill level
   - Learning goals
   - Preferred learning style
   
2. During Learning:
   - AI extracts what you've learned
   - Tracks concepts you struggle with
   - Remembers preferred resources

3. Review Progress:
   - Search "What have I learned about X?"
   - View task completions
   - Check goal progress
```

### Workflow 3: Project Context Manager

**Goal**: Maintain context across coding sessions

```markdown
1. Project Setup:
   - Tech stack preferences
   - Coding standards
   - Project structure

2. During Development:
   - Design decisions made
   - Bug fixes applied
   - Features implemented

3. Context Recall:
   - "Why did we choose X library?"
   - "What was the solution to Y bug?"
   - "What features are planned?"
```

## 🔒 Privacy & Security

### Data Storage

- **Local Storage**: All memories stored in your local database
- **Embeddings**: Generated locally (sentence-transformers)
- **Vector DB**: ChromaDB persisted to disk
- **No Cloud**: Nothing sent to external services (except LLM API)

### What Gets Sent to LLMs

1. **For Extraction**: Conversation text only
2. **For Chat**: Selected relevant memories (10-15 max)
3. **API Keys**: Your own keys, your control
4. **No Training**: Your data isn't used to train models

### Security Best Practices

1. **Sensitive Data**: Don't store passwords, API keys, etc.
2. **Personal Info**: Be mindful of what you share
3. **Regular Cleanup**: Delete old/unnecessary memories
4. **Backup**: Database is in `chat_history.db`
5. **Access Control**: Only you can access your memories

## 🛠️ Troubleshooting

### Problem: No memories being extracted

**Solutions:**
1. Check auto-extraction is enabled (Settings tab)
2. Verify LLM provider is working
3. Try explicit statements: "I like..." "I prefer..."
4. Check extraction frequency setting

### Problem: Search returns no results

**Solutions:**
1. Try broader search terms
2. Lower minimum similarity threshold
3. Check if memories exist in "All Memories"
4. Verify embedding model is loaded

### Problem: AI not using memories

**Solutions:**
1. Enable auto-injection in Settings
2. Check if relevant memories exist (search first)
3. Increase max memories per request
4. Pin important memories
5. Verify memories have good importance scores

### Problem: Slow embedding generation

**Solutions:**
1. First run downloads model (~90MB) - be patient
2. Subsequent runs use cached model (fast)
3. Use smaller model: 'all-MiniLM-L6-v2' (default)
4. Batch operations instead of one-by-one

### Problem: Memory conflicts

**Solutions:**
1. System should auto-resolve
2. Manually verify conflicting memories
3. Delete outdated information
4. Update with correct info
5. Use version history to see changes

## 📊 Performance Tips

### For Speed

1. **Pin Sparingly**: Fewer pinned = faster context building
2. **Limit Search Results**: 5-10 is usually enough
3. **Use Local Embeddings**: Faster than API calls
4. **Cache ChromaDB**: Keep vector DB warm

### For Accuracy

1. **High-Quality Memories**: Clear, specific content
2. **Good Tags**: Better organization = better search
3. **Verify Important Info**: Mark as verified
4. **Update Regularly**: Keep information current
5. **Remove Outdated**: Clean up old memories

### For Organization

1. **Consistent Categories**: Use same category names
2. **Tag Standards**: Define tag naming convention
3. **Regular Reviews**: Monthly cleanup
4. **Export/Import**: Backup important memories (future feature)

## 🔮 Future Enhancements

Planned features (not yet implemented):

- [ ] **Memory Templates**: Pre-made memory sets
- [ ] **Memory Sharing**: Share memory sets with others
- [ ] **Advanced Analytics**: Memory usage insights
- [ ] **Memory Export/Import**: Backup and restore
- [ ] **Knowledge Graphs**: Visual memory relationships
- [ ] **Memory Recommendations**: Suggest what to remember
- [ ] **Multi-user Memory**: Shared team memories
- [ ] **Memory Compression**: Auto-summarize old memories
- [ ] **Custom Embedding Models**: Choose your own
- [ ] **Memory Webhooks**: Auto-extract from external sources

## 📞 Support

### Getting Help

1. **Check Logs**: Look for error messages
2. **Test Components**: Try each feature individually
3. **Database**: Verify tables created (`chat_history.db`)
4. **Dependencies**: Ensure all packages installed

### Reporting Issues

Include:
1. What you were trying to do
2. What happened instead
3. Error messages
4. Steps to reproduce
5. Your setup (OS, Python version)

---

**🎉 You're ready to use the Memory System!**

Your AI now has long-term memory - it will remember your preferences, learn from conversations, and provide increasingly personalized responses. Enjoy! 🧠✨

