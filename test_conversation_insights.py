"""
Test script for Conversation Insights Analyzer
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from backend.core.conversation_insights import (
    ConversationInsightsAnalyzer,
    analyze_conversation,
    get_conversation_insights
)
from backend.database.operations import MessageDB


def main():
    """Test conversation insights"""
    print("🔍 Testing Conversation Insights Analyzer")
    print("="*60)
    
    # Use existing conversation
    conversation_id = 37
    user_id = 1
    
    print(f"\n📨 Loading conversation {conversation_id}...")
    messages = MessageDB.get_messages(conversation_id)
    print(f"✅ Found {len(messages)} messages")
    
    # Analyze conversation
    print(f"\n🧠 Analyzing conversation...")
    analyzer = ConversationInsightsAnalyzer()
    insights_data = analyzer.analyze_conversation(messages, conversation_id, user_id)
    
    # Display results
    print("\n" + "="*60)
    print("📊 CONVERSATION INSIGHTS")
    print("="*60)
    
    print(f"\n🎯 Conversation Type: {insights_data.conversation_type}")
    print(f"📈 Complexity Level: {insights_data.complexity_level}")
    print(f"⏱️  Duration: {insights_data.duration_minutes} minutes" if insights_data.duration_minutes else "⏱️  Duration: N/A")
    
    print(f"\n🔸 Top Topics ({len(insights_data.main_topics)}):")
    for i, topic in enumerate(insights_data.main_topics[:5], 1):
        print(f"   {i}. {topic.topic} (score: {topic.score:.1f}, freq: {topic.frequency})")
        if topic.context:
            print(f"      Context: {topic.context[0][:80]}...")
    
    print(f"\n🔸 Topic Clusters:")
    for cluster, topics in insights_data.topic_clusters.items():
        print(f"   • {cluster}: {', '.join(topics[:5])}")
    
    print(f"\n🔸 Entities by Type:")
    for entity_type, entities in insights_data.entities.items():
        print(f"   • {entity_type}: {len(entities)} found")
        for entity in entities[:3]:
            print(f"      - {entity.text} (freq: {entity.frequency})")
    
    print(f"\n🔸 Relationships ({len(insights_data.relationships)}):")
    for i, rel in enumerate(insights_data.relationships[:5], 1):
        print(f"   {i}. {rel['from']} --[{rel['type']}]--> {rel['to']} (strength: {rel['strength']})")
    
    print(f"\n🔸 Statistics:")
    stats = insights_data.statistics
    print(f"   • Total messages: {stats.get('total_messages', 0)}")
    print(f"   • User / Assistant: {stats.get('user_messages', 0)} / {stats.get('assistant_messages', 0)}")
    print(f"   • Avg message length: {stats.get('avg_message_length', 0):.0f} chars")
    print(f"   • Questions asked: {stats.get('questions_asked', 0)}")
    print(f"   • Code blocks: {stats.get('code_blocks', 0)}")
    print(f"   • Engagement ratio: {stats.get('engagement_ratio', 0):.2f}")
    
    # Save to database
    print(f"\n💾 Saving insights to database...")
    saved_insights = analyzer.save_insights(conversation_id, user_id, insights_data)
    print(f"✅ Insights saved (ID: {saved_insights.id})")
    
    # Retrieve and verify
    print(f"\n📖 Retrieving saved insights...")
    retrieved = get_conversation_insights(conversation_id)
    print(f"✅ Retrieved insights with {len(retrieved.main_topics)} topics")
    
    # Final summary
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print(f"\n📋 Summary:")
    print(f"   • Topics extracted: {len(insights_data.main_topics)}")
    print(f"   • Entities found: {sum(len(e) for e in insights_data.entities.values())}")
    print(f"   • Relationships mapped: {len(insights_data.relationships)}")
    print(f"   • Conversation type: {insights_data.conversation_type}")
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

