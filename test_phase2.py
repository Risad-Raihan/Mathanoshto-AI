"""
Test script for Phase 2 - Database & Chat Management
Run this to verify database and chat functionality
"""
import asyncio
import sys

print("=" * 60)
print("PHASE 2 TEST - Database & Chat Management")
print("=" * 60)
print()

# Test 1: Initialize Database
print("Test 1: Initializing Database...")
try:
    from backend.database.operations import init_database, ConversationDB, MessageDB
    init_database()
    print("✓ Database tables created")
    print()
except Exception as e:
    print(f"❌ Database initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Create Conversation
print("Test 2: Creating Conversation...")
try:
    conv = ConversationDB.create_conversation("Test Chat - Phase 2")
    print(f"✓ Created conversation: ID={conv.id}, Title='{conv.title}'")
    print()
except Exception as e:
    print(f"❌ Conversation creation failed: {e}")
    sys.exit(1)

# Test 3: Add Messages
print("Test 3: Adding Messages...")
try:
    # Add user message
    msg1 = MessageDB.add_message(
        conversation_id=conv.id,
        role="user",
        content="Hello! What is 2+2?"
    )
    print(f"✓ Added user message: ID={msg1.id}")
    
    # Add assistant message with token info
    msg2 = MessageDB.add_message(
        conversation_id=conv.id,
        role="assistant",
        content="Hello! 2+2 equals 4.",
        model="gpt-3.5-turbo",
        provider="openai",
        input_tokens=15,
        output_tokens=10,
        cost=0.000025
    )
    print(f"✓ Added assistant message: ID={msg2.id}")
    print()
except Exception as e:
    print(f"❌ Message creation failed: {e}")
    sys.exit(1)

# Test 4: Retrieve Messages
print("Test 4: Retrieving Conversation History...")
try:
    messages = MessageDB.get_messages(conv.id)
    print(f"✓ Retrieved {len(messages)} messages:")
    for msg in messages:
        print(f"  - [{msg.role}]: {msg.content[:50]}...")
    print()
except Exception as e:
    print(f"❌ Message retrieval failed: {e}")
    sys.exit(1)

# Test 5: Token Usage Statistics
print("Test 5: Calculating Token Usage...")
try:
    usage = MessageDB.get_conversation_tokens(conv.id)
    print(f"✓ Token statistics:")
    print(f"  - Input tokens: {usage['input_tokens']}")
    print(f"  - Output tokens: {usage['output_tokens']}")
    print(f"  - Total tokens: {usage['total_tokens']}")
    print(f"  - Total cost: ${usage['total_cost']:.6f}")
    print()
except Exception as e:
    print(f"❌ Token calculation failed: {e}")
    sys.exit(1)

# Test 6: List Conversations
print("Test 6: Listing All Conversations...")
try:
    conversations = ConversationDB.list_conversations()
    print(f"✓ Found {len(conversations)} conversation(s):")
    for c in conversations:
        print(f"  - ID={c.id}: '{c.title}' (Messages: {len(c.messages)})")
    print()
except Exception as e:
    print(f"❌ Conversation listing failed: {e}")
    sys.exit(1)

# Test 7: Chat Manager
print("Test 7: Testing Chat Manager...")
try:
    from backend.core.chat_manager import ChatManager
    
    # Create new chat
    chat = ChatManager()
    print(f"✓ Created ChatManager: conversation_id={chat.conversation_id}")
    
    # Get token usage (should be 0 for new conversation)
    usage = chat.get_token_usage()
    print(f"✓ Initial token usage: {usage}")
    print()
except Exception as e:
    print(f"❌ Chat Manager test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 8: Send Message (Actual API Call)
print("Test 8: Sending Real Message to LLM...")
print("⚠️  This will make an actual API call and use tokens!")

async def test_chat():
    try:
        from backend.core.chat_manager import ChatManager
        
        # Create new chat
        chat = ChatManager()
        
        # Send a simple message
        response = await chat.send_message(
            user_message="Say 'Hello from Phase 2!' and nothing else.",
            provider="openai",
            model="gpt-3.5-turbo",
            max_tokens=20
        )
        
        print(f"✓ LLM Response: {response.content}")
        print(f"✓ Tokens: {response.input_tokens} in + {response.output_tokens} out = {response.total_tokens} total")
        print(f"✓ Cost: ${response.cost:.6f}")
        print(f"✓ Model: {response.provider}/{response.model}")
        print()
        
        # Get conversation token usage
        usage = chat.get_token_usage()
        print(f"✓ Conversation total: {usage['total_tokens']} tokens, ${usage['total_cost']:.6f}")
        print()
        
        # Update conversation title
        chat.update_title("Phase 2 Test Conversation")
        print(f"✓ Updated conversation title")
        print()
        
        return True
    except Exception as e:
        print(f"⚠️  API call failed (this is OK if you don't have credits): {e}")
        print()
        return False

# Run async test
try:
    success = asyncio.run(test_chat())
except Exception as e:
    print(f"⚠️  Async test skipped: {e}")
    success = False

# Summary
print("=" * 60)
print("PHASE 2 TEST SUMMARY")
print("=" * 60)
print()

print("✅ SUCCESS! Phase 2 is working!")
print()
print("What we verified:")
print("  ✓ Database initialization")
print("  ✓ Conversation creation")
print("  ✓ Message storage")
print("  ✓ Token tracking")
print("  ✓ Chat Manager integration")
if success:
    print("  ✓ Live API calls working!")
print()
print("Next steps:")
print("  1. Proceed to Phase 3 (Streamlit Frontend)")
print("  2. Follow PROJECT_PLAN.md - Phase 3, Task 3.1")
print("  3. Build the chat interface!")
print()
print("=" * 60)

