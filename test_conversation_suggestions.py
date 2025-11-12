"""
Test script for Conversation Suggestions Engine
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.core.conversation_suggestions import (
    ConversationSuggestionEngine,
    generate_conversation_suggestions,
    get_active_suggestions
)
from backend.database.operations import MessageDB, ConversationDB
from backend.database.models import Message


def test_suggestion_generation():
    """Test suggestion generation on existing conversation"""
    print("🔮 Testing Conversation Suggestion Engine")
    print("="*60)
    
    # Use the conversation from the summarizer test (conversation_id = 37)
    conversation_id = 37
    user_id = 1
    
    print(f"\n📨 Loading conversation {conversation_id}...")
    messages = MessageDB.get_messages(conversation_id)
    print(f"✅ Found {len(messages)} messages")
    
    # Create suggestion engine
    engine = ConversationSuggestionEngine()
    
    # Generate suggestions
    print(f"\n🧠 Generating suggestions...")
    suggestions = engine.generate_suggestions(
        messages=messages,
        conversation_id=conversation_id,
        user_id=user_id,
        num_suggestions=5,
        use_ai=False
    )
    
    # Display results
    print("\n" + "="*60)
    print("💡 GENERATED SUGGESTIONS")
    print("="*60)
    
    for i, suggestion in enumerate(suggestions, 1):
        print(f"\n🔸 Suggestion {i}:")
        print(f"   Text: {suggestion.text}")
        print(f"   Category: {suggestion.category}")
        print(f"   Priority: {suggestion.priority}")
        print(f"   Relevance: {suggestion.relevance_score:.2f}")
        print(f"   Reason: {suggestion.reason}")
    
    # Save to database
    print("\n💾 Saving suggestions to database...")
    context_message_ids = [m.id for m in messages[-5:]]
    saved_suggestions = engine.save_suggestions(
        conversation_id,
        user_id,
        suggestions,
        context_message_ids
    )
    print(f"✅ Saved {len(saved_suggestions)} suggestions")
    
    return suggestions, saved_suggestions


def test_retrieve_suggestions():
    """Test retrieving saved suggestions"""
    print("\n" + "="*60)
    print("📖 Testing Suggestion Retrieval")
    print("="*60)
    
    conversation_id = 37
    
    # Retrieve active suggestions
    active_suggestions = get_active_suggestions(conversation_id)
    
    print(f"\n✅ Retrieved {len(active_suggestions)} active suggestions:")
    for i, sug in enumerate(active_suggestions, 1):
        print(f"\n   {i}. {sug.suggestion_text}")
        print(f"      Category: {sug.suggestion_category} | Priority: {sug.priority}")
        print(f"      Rank: {sug.rank} | Score: {sug.relevance_score:.2f}")
    
    return active_suggestions


def test_different_conversation_types():
    """Test with different conversation types"""
    print("\n" + "="*60)
    print("🎭 Testing Different Conversation Types")
    print("="*60)
    
    engine = ConversationSuggestionEngine()
    
    # Test 1: Problem-solving conversation
    print("\n🔧 Test 1: Problem-solving conversation")
    problem_messages = [
        Message(id=1, conversation_id=1, role='user', content='My code is throwing an error'),
        Message(id=2, conversation_id=1, role='assistant', content='Let me help you debug that. Can you share the error message?'),
        Message(id=3, conversation_id=1, role='user', content='It says "TypeError: undefined is not a function"'),
        Message(id=4, conversation_id=1, role='assistant', content='This error typically occurs when you try to call a method that doesn\'t exist. Check your function definitions.')
    ]
    
    context = engine._analyze_context(problem_messages)
    print(f"   Detected type: {context['conv_type']}")
    print(f"   Is complete: {context['is_complete']}")
    
    suggestions = engine._rule_based_suggestions(problem_messages, context, 3)
    print(f"   Generated {len(suggestions)} suggestions:")
    for sug in suggestions[:3]:
        print(f"      • {sug.text} [{sug.category}]")
    
    # Test 2: Exploratory conversation
    print("\n🔍 Test 2: Exploratory conversation")
    exploratory_messages = [
        Message(id=1, conversation_id=2, role='user', content='What is machine learning?'),
        Message(id=2, conversation_id=2, role='assistant', content='Machine learning is a subset of AI where algorithms learn from data. It includes supervised learning, unsupervised learning, and reinforcement learning.')
    ]
    
    context = engine._analyze_context(exploratory_messages)
    print(f"   Detected type: {context['conv_type']}")
    
    suggestions = engine._rule_based_suggestions(exploratory_messages, context, 3)
    print(f"   Generated {len(suggestions)} suggestions:")
    for sug in suggestions[:3]:
        print(f"      • {sug.text} [{sug.category}]")
    
    # Test 3: Implementation conversation
    print("\n⚙️ Test 3: Implementation conversation")
    implementation_messages = [
        Message(id=1, conversation_id=3, role='user', content='How do I build a REST API?'),
        Message(id=2, conversation_id=3, role='assistant', content='To build a REST API, you need to: 1. Choose a framework (Flask, FastAPI, Express), 2. Define your endpoints, 3. Implement CRUD operations, 4. Add authentication, 5. Deploy your API.')
    ]
    
    context = engine._analyze_context(implementation_messages)
    print(f"   Detected type: {context['conv_type']}")
    
    suggestions = engine._rule_based_suggestions(implementation_messages, context, 3)
    print(f"   Generated {len(suggestions)} suggestions:")
    for sug in suggestions[:3]:
        print(f"      • {sug.text} [{sug.category}]")


def main():
    """Run all tests"""
    print("🧪 Testing Conversation Suggestions System")
    print("="*60)
    
    try:
        # Test 1: Generate and save suggestions
        suggestions, saved_suggestions = test_suggestion_generation()
        
        # Test 2: Retrieve suggestions
        active_suggestions = test_retrieve_suggestions()
        
        # Test 3: Different conversation types
        test_different_conversation_types()
        
        # Final summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n📋 Summary:")
        print(f"   • Suggestions generated: {len(suggestions)}")
        print(f"   • Suggestions saved: {len(saved_suggestions)}")
        print(f"   • Active suggestions retrieved: {len(active_suggestions)}")
        print(f"\n🎯 Categories used:")
        categories = set(s.category for s in suggestions)
        for cat in categories:
            count = sum(1 for s in suggestions if s.category == cat)
            print(f"      • {cat}: {count}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

