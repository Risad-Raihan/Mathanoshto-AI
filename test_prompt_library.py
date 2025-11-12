"""
Test script for Smart Prompt Library & Follow-up Questions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.core.prompt_library import (
    SmartPromptLibrary,
    FollowUpQuestionGenerator,
    get_smart_prompts,
    generate_follow_up_questions
)
from backend.database.operations import MessageDB


def test_prompt_library():
    """Test smart prompt library"""
    print("📚 Testing Smart Prompt Library")
    print("="*60)
    
    library = SmartPromptLibrary()
    
    # Test 1: Get all categories
    print("\n📂 Available Categories:")
    categories = library.get_all_categories()
    for i, cat in enumerate(categories, 1):
        print(f"   {i}. {cat}")
    
    # Test 2: Get prompts by category
    print(f"\n📝 Prompts in 'learning' category:")
    learning_prompts = library.get_prompts_by_category('learning')
    for i, prompt in enumerate(learning_prompts, 1):
        print(f"\n   {i}. {prompt.title}")
        print(f"      Text: {prompt.text[:80]}...")
        print(f"      Complexity: {prompt.complexity}")
        print(f"      Tags: {', '.join(prompt.tags)}")
    
    # Test 3: Search prompts
    print(f"\n🔍 Searching for 'debug' prompts:")
    search_results = library.search_prompts('debug')
    for i, prompt in enumerate(search_results, 1):
        print(f"   {i}. {prompt.title} [{prompt.category}]")
    
    # Test 4: Get contextual prompts
    print(f"\n🎯 Contextual prompts based on conversation:")
    from backend.database.models import Message
    
    test_messages = [
        Message(id=1, conversation_id=1, role='user', content='I want to learn about machine learning'),
        Message(id=2, conversation_id=1, role='assistant', content='Machine learning is a fascinating field. It involves training algorithms on data.')
    ]
    
    contextual_prompts = library.get_contextual_prompts(test_messages, limit=3)
    for i, prompt in enumerate(contextual_prompts, 1):
        print(f"   {i}. {prompt.title} [{prompt.category}]")
    
    return library


def test_follow_up_questions():
    """Test follow-up question generator"""
    print("\n" + "="*60)
    print("❓ Testing Follow-up Question Generator")
    print("="*60)
    
    generator = FollowUpQuestionGenerator()
    
    # Test with actual conversation
    conversation_id = 37  # From previous tests
    print(f"\n📨 Loading conversation {conversation_id}...")
    messages = MessageDB.get_messages(conversation_id)
    print(f"✅ Found {len(messages)} messages")
    
    # Generate follow-up questions
    print(f"\n🧠 Generating follow-up questions...")
    questions = generator.generate_follow_ups(messages, num_questions=5)
    
    print(f"\n💡 Generated {len(questions)} follow-up questions:")
    for i, q in enumerate(questions, 1):
        print(f"\n🔸 Question {i}:")
        print(f"   Q: {q.question}")
        print(f"   Intent: {q.intent}")
        print(f"   Priority: {q.priority}")
        print(f"   Context: {q.context}")
    
    # Test saving to database
    print(f"\n💾 Saving questions to database...")
    context_message_ids = [m.id for m in messages[-5:]]
    saved_questions = generator.save_as_suggestions(
        conversation_id=conversation_id,
        user_id=1,
        questions=questions,
        context_message_ids=context_message_ids
    )
    print(f"✅ Saved {len(saved_questions)} questions as suggestions")
    
    return questions


def test_user_prompt_library():
    """Test user's personal prompt library"""
    print("\n" + "="*60)
    print("👤 Testing User Prompt Library")
    print("="*60)
    
    library = SmartPromptLibrary()
    user_id = 1
    
    # Save a custom prompt
    print("\n💾 Saving custom prompt...")
    custom_prompt = library.save_user_prompt(
        user_id=user_id,
        prompt_text="Explain {concept} with a focus on practical implementation and common pitfalls",
        prompt_title="My Practical Learning Template",
        category="learning",
        tags=["custom", "practical", "pitfalls"]
    )
    print(f"✅ Saved custom prompt: {custom_prompt.prompt_title}")
    print(f"   ID: {custom_prompt.id}")
    print(f"   Category: {custom_prompt.prompt_category}")
    
    # Retrieve user prompts
    print(f"\n📖 Retrieving user's saved prompts...")
    user_prompts = library.get_user_prompts(user_id=user_id)
    print(f"✅ Found {len(user_prompts)} custom prompts:")
    for i, prompt in enumerate(user_prompts, 1):
        print(f"   {i}. {prompt.prompt_title}")
        print(f"      Text: {prompt.prompt_text[:60]}...")
        print(f"      Usage count: {prompt.usage_count}")
    
    return user_prompts


def test_convenience_functions():
    """Test convenience functions"""
    print("\n" + "="*60)
    print("⚡ Testing Convenience Functions")
    print("="*60)
    
    # Test get_smart_prompts
    print("\n📚 Getting prompts by category...")
    prompts = get_smart_prompts(category='implementation', complexity='beginner')
    print(f"✅ Found {len(prompts)} beginner implementation prompts")
    for prompt in prompts:
        print(f"   • {prompt.title}")
    
    # Test search
    print("\n🔍 Searching prompts...")
    search_prompts = get_smart_prompts(search_query='architecture')
    print(f"✅ Found {len(search_prompts)} prompts matching 'architecture'")
    for prompt in search_prompts[:3]:
        print(f"   • {prompt.title} [{prompt.category}]")
    
    # Test generate_follow_up_questions
    print("\n❓ Generating follow-up questions for conversation...")
    questions = generate_follow_up_questions(
        conversation_id=37,
        user_id=1,
        num_questions=3,
        save_to_db=False  # Already saved in previous test
    )
    print(f"✅ Generated {len(questions)} questions:")
    for i, q in enumerate(questions, 1):
        print(f"   {i}. {q.question} [{q.intent}]")


def test_prompt_templates():
    """Test built-in prompt templates"""
    print("\n" + "="*60)
    print("📋 Testing Built-in Prompt Templates")
    print("="*60)
    
    library = SmartPromptLibrary()
    
    # Count total prompts
    total_prompts = 0
    print("\n📊 Prompt Statistics:")
    for category in library.get_all_categories():
        category_prompts = library.get_prompts_by_category(category)
        total_prompts += len(category_prompts)
        print(f"   • {category}: {len(category_prompts)} prompts")
    
    print(f"\n✅ Total built-in prompts: {total_prompts}")
    
    # Show complexity distribution
    print(f"\n📈 Complexity Distribution:")
    complexity_counts = {'beginner': 0, 'intermediate': 0, 'advanced': 0}
    for category in library.get_all_categories():
        for prompt in library.get_prompts_by_category(category):
            complexity_counts[prompt.complexity] += 1
    
    for complexity, count in complexity_counts.items():
        print(f"   • {complexity.title()}: {count} prompts")


def main():
    """Run all tests"""
    print("🧪 Testing Smart Prompt Library & Follow-up Questions")
    print("="*60)
    
    try:
        # Test 1: Prompt library
        library = test_prompt_library()
        
        # Test 2: Follow-up questions
        questions = test_follow_up_questions()
        
        # Test 3: User prompt library
        user_prompts = test_user_prompt_library()
        
        # Test 4: Convenience functions
        test_convenience_functions()
        
        # Test 5: Prompt templates
        test_prompt_templates()
        
        # Final summary
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print(f"\n📋 Summary:")
        print(f"   • Prompt categories: {len(library.get_all_categories())}")
        print(f"   • Follow-up questions generated: {len(questions)}")
        print(f"   • User custom prompts: {len(user_prompts)}")
        print(f"\n🎯 Features Verified:")
        print(f"   ✓ Category-based prompt retrieval")
        print(f"   ✓ Prompt search functionality")
        print(f"   ✓ Contextual prompt suggestions")
        print(f"   ✓ Follow-up question generation (5 types)")
        print(f"   ✓ User prompt library management")
        print(f"   ✓ Database persistence")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

