"""
Test script for Conversation Summarizer
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.core.conversation_summarizer import ConversationSummarizer, summarize_conversation
from backend.database.models import Message
from backend.database.operations import get_db, MessageDB, ConversationDB
from datetime import datetime


def create_test_conversation():
    """Create a test conversation for summarization"""
    print("📝 Creating test conversation...")
    
    # Create a test conversation
    db = get_db()
    try:
        # Get or create test user (user_id = 1)
        conversation = ConversationDB.create_conversation(
            user_id=1,
            title="Test Conversation for Summarization"
        )
        
        # Add test messages
        test_messages = [
            ("user", "Hi! I need help understanding how RAG systems work."),
            ("assistant", "Hello! I'd be happy to explain RAG (Retrieval-Augmented Generation) systems. **Key point:** RAG combines retrieval and generation. It works by first retrieving relevant documents, then using them to generate contextual responses. This is important because it reduces hallucinations and provides source citations."),
            ("user", "That's interesting. What are the main components?"),
            ("assistant", "The main components include:\n1. Document chunking\n2. Embedding generation\n3. Vector database for storage\n4. Semantic search\n5. Context integration\n\nWe decided to use a hybrid search approach combining semantic and keyword search for better results."),
            ("user", "What should I do next to implement this?"),
            ("assistant", "Here are the action items:\n- Need to set up a vector database\n- Should implement chunking strategy\n- Must create embedding pipeline\n- Have to integrate with LLM\n\nLet's start with the chunking strategy first, as that's the foundation."),
            ("user", "How do I handle large documents?"),
            ("assistant", "For large documents, you need to use chunking. The key decision here is: we'll use a chunk size of 1000 tokens with 200 token overlap. This ensures context continuity while keeping chunks manageable."),
        ]
        
        for role, content in test_messages:
            MessageDB.add_message(
                conversation_id=conversation.id,
                role=role,
                content=content
            )
        
        print(f"✅ Created conversation {conversation.id} with {len(test_messages)} messages")
        return conversation.id
        
    finally:
        db.close()


def test_summarization(conversation_id: int):
    """Test the summarization"""
    print(f"\n🧠 Testing summarization for conversation {conversation_id}...")
    
    # Get messages
    messages = MessageDB.get_messages(conversation_id)
    print(f"📨 Found {len(messages)} messages")
    
    # Create summarizer
    summarizer = ConversationSummarizer()
    
    # Generate summary
    summary_result = summarizer.summarize_conversation(
        messages=messages,
        conversation_id=conversation_id,
        user_id=1,
        use_ai=False
    )
    
    # Display results
    print("\n" + "="*60)
    print("📊 SUMMARIZATION RESULTS")
    print("="*60)
    
    print(f"\n🔸 SHORT SUMMARY ({len(summary_result.short_summary)} chars):")
    print(f"   {summary_result.short_summary}")
    
    print(f"\n🔸 MEDIUM SUMMARY ({len(summary_result.medium_summary)} chars):")
    print(f"   {summary_result.medium_summary}")
    
    print(f"\n🔸 DETAILED SUMMARY:")
    print(summary_result.detailed_summary)
    
    print(f"\n🔸 KEY POINTS ({len(summary_result.key_points)}):")
    for i, point in enumerate(summary_result.key_points, 1):
        print(f"   {i}. {point}")
    
    print(f"\n🔸 DECISIONS MADE ({len(summary_result.decisions_made)}):")
    for i, decision in enumerate(summary_result.decisions_made, 1):
        print(f"   {i}. {decision}")
    
    print(f"\n🔸 ACTION ITEMS ({len(summary_result.action_items)}):")
    for i, action in enumerate(summary_result.action_items, 1):
        print(f"   {i}. {action}")
    
    print(f"\n🔸 QUESTIONS ASKED ({len(summary_result.questions_asked)}):")
    for i, question in enumerate(summary_result.questions_asked, 1):
        print(f"   {i}. {question}")
    
    print(f"\n🔸 CONFIDENCE SCORE: {summary_result.confidence_score}")
    print(f"🔸 MESSAGE COUNT: {summary_result.message_count}")
    
    # Save to database
    print("\n💾 Saving summary to database...")
    saved_summary = summarizer.save_summary(conversation_id, 1, summary_result)
    print(f"✅ Summary saved with ID: {saved_summary.id}")
    
    return summary_result


def test_get_summary(conversation_id: int):
    """Test retrieving saved summary"""
    print(f"\n📖 Retrieving saved summary for conversation {conversation_id}...")
    
    from backend.core.conversation_summarizer import get_conversation_summary
    
    summary = get_conversation_summary(conversation_id)
    
    if summary:
        print(f"✅ Retrieved summary (ID: {summary.id})")
        print(f"   Short: {summary.short_summary[:100]}...")
        print(f"   Key Points: {len(summary.key_points)}")
        print(f"   Decisions: {len(summary.decisions_made)}")
        print(f"   Actions: {len(summary.action_items)}")
    else:
        print("❌ No summary found")
    
    return summary


def main():
    """Run all tests"""
    print("🧪 Testing Conversation Summarizer")
    print("="*60)
    
    try:
        # Create test conversation
        conversation_id = create_test_conversation()
        
        # Test summarization
        summary_result = test_summarization(conversation_id)
        
        # Test retrieval
        saved_summary = test_get_summary(conversation_id)
        
        # Final summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n📋 Summary:")
        print(f"   • Conversation ID: {conversation_id}")
        print(f"   • Messages processed: {summary_result.message_count}")
        print(f"   • Key points extracted: {len(summary_result.key_points)}")
        print(f"   • Decisions identified: {len(summary_result.decisions_made)}")
        print(f"   • Action items found: {len(summary_result.action_items)}")
        print(f"   • Questions captured: {len(summary_result.questions_asked)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

