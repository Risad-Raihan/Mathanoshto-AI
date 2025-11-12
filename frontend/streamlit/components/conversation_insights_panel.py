"""
Conversation Insights Panel
Beautiful UI for all smart features: summarization, suggestions, prompts, insights, export
"""

import streamlit as st
from typing import Optional
from pathlib import Path
import json

# Import backend modules
from backend.core.conversation_summarizer import (
    summarize_conversation,
    get_conversation_summary
)
from backend.core.conversation_suggestions import (
    generate_conversation_suggestions,
    get_active_suggestions
)
from backend.core.prompt_library import (
    SmartPromptLibrary,
    generate_follow_up_questions,
    get_smart_prompts
)
from backend.core.conversation_insights import (
    analyze_conversation,
    get_conversation_insights
)
from backend.core.conversation_exporter import export_conversation
from backend.database.operations import MessageDB


def render_conversation_insights_panel():
    """Render the main conversation insights panel"""
    
    st.markdown("# 🧠 Conversation Insights")
    st.markdown("*AI-powered analysis, suggestions, and smart features*")
    st.markdown("---")
    
    # Get current conversation
    conversation_id = st.session_state.get('current_conversation_id')
    user_id = st.session_state.get('user_id', 1)
    
    if not conversation_id:
        st.info("💬 Start or select a conversation to see insights!")
        st.markdown("### 📚 Meanwhile, explore the Smart Prompt Library below:")
        _render_prompt_library_standalone()
        return
    
    # Get messages
    messages = MessageDB.get_messages(conversation_id)
    
    if not messages or len(messages) < 2:
        st.info("💬 Have a conversation first to generate insights!")
        return
    
    # Create tabs for different features
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📊 Summary",
        "💡 Suggestions", 
        "📚 Smart Prompts",
        "🔍 Deep Insights",
        "📄 Export"
    ])
    
    with tab1:
        _render_summary_tab(conversation_id, user_id, messages)
    
    with tab2:
        _render_suggestions_tab(conversation_id, user_id, messages)
    
    with tab3:
        _render_prompts_tab(conversation_id, user_id, messages)
    
    with tab4:
        _render_insights_tab(conversation_id, user_id, messages)
    
    with tab5:
        _render_export_tab(conversation_id, user_id)


def _render_summary_tab(conversation_id: int, user_id: int, messages: list):
    """Render the conversation summary tab"""
    
    st.markdown("## 📊 Conversation Summary")
    st.markdown("*AI-generated multi-level summaries with key insights*")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Regenerate Summary", use_container_width=True):
            with st.spinner("Generating summary..."):
                summary = summarize_conversation(conversation_id, user_id, use_ai=False)
                st.success("✅ Summary generated!")
                st.rerun()
    
    # Get or generate summary
    summary = get_conversation_summary(conversation_id)
    
    if not summary:
        with st.spinner("Generating summary for the first time..."):
            summary = summarize_conversation(conversation_id, user_id, use_ai=False)
    
    if not summary:
        st.error("❌ Could not generate summary")
        return
    
    # Display summary in elegant cards
    st.markdown("---")
    
    # Short Summary
    st.markdown("### 🎯 Quick Summary")
    st.info(f"💬 {summary.short_summary}")
    
    # Medium Summary  
    with st.expander("📝 Detailed Overview", expanded=True):
        st.markdown(summary.medium_summary)
    
    # Key Points
    if summary.key_points:
        st.markdown("### ⭐ Key Points")
        for i, point in enumerate(summary.key_points, 1):
            st.markdown(f"**{i}.** {point}")
    
    # Two columns for decisions and actions
    col1, col2 = st.columns(2)
    
    with col1:
        if summary.decisions_made:
            st.markdown("### ✅ Decisions Made")
            for i, decision in enumerate(summary.decisions_made, 1):
                st.success(f"**{i}.** {decision}")
    
    with col2:
        if summary.action_items:
            st.markdown("### 📋 Action Items")
            for i, action in enumerate(summary.action_items, 1):
                st.warning(f"☐ {action}")
    
    # Questions
    if summary.questions_asked:
        st.markdown("### ❓ Questions Addressed")
        for i, question in enumerate(summary.questions_asked, 1):
            st.markdown(f"**Q{i}:** {question}")
    
    # Stats
    st.markdown("---")
    metrics = st.columns(4)
    with metrics[0]:
        st.metric("📨 Messages", summary.message_count)
    with metrics[1]:
        st.metric("⭐ Key Points", len(summary.key_points))
    with metrics[2]:
        st.metric("✅ Decisions", len(summary.decisions_made))
    with metrics[3]:
        st.metric("📋 Actions", len(summary.action_items))


def _render_suggestions_tab(conversation_id: int, user_id: int, messages: list):
    """Render conversation suggestions tab"""
    
    st.markdown("## 💡 Smart Suggestions")
    st.markdown("*AI-powered conversation continuations and follow-up questions*")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        num_suggestions = st.selectbox("Count", [3, 5, 7, 10], index=1)
        if st.button("🔄 Generate New", use_container_width=True):
            with st.spinner("Generating suggestions..."):
                suggestions = generate_conversation_suggestions(
                    conversation_id, user_id, num_suggestions
                )
                st.success(f"✅ Generated {len(suggestions)} suggestions!")
                st.rerun()
    
    # Get active suggestions
    suggestions = get_active_suggestions(conversation_id)
    
    if not suggestions:
        with st.spinner("Generating suggestions..."):
            suggestions = generate_conversation_suggestions(
                conversation_id, user_id, 5
            )
    
    if not suggestions:
        st.info("💬 Continue the conversation to get suggestions!")
        return
    
    st.markdown("---")
    
    # Group by category
    categories = {}
    for sug in suggestions:
        cat = sug.suggestion_category or 'general'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(sug)
    
    # Display by category with icons
    category_icons = {
        'clarification': '🔍',
        'expansion': '📖',
        'deep-dive': '🎯',
        'related': '🔗',
        'next-step': '➡️',
        'continuation': '💬',
        'followup': '❓',
        'general': '💡'
    }
    
    for cat, cat_suggestions in categories.items():
        icon = category_icons.get(cat, '💡')
        st.markdown(f"### {icon} {cat.replace('-', ' ').title()}")
        
        for i, sug in enumerate(cat_suggestions[:5]):
            priority_color = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(sug.priority, '⚪')
            
            with st.container():
                col1, col2 = st.columns([20, 1])
                with col1:
                    if st.button(
                        f"{priority_color} {sug.suggestion_text}",
                        key=f"sug_{sug.id}",
                        use_container_width=True
                    ):
                        # Copy to clipboard functionality
                        st.session_state.selected_suggestion = sug.suggestion_text
                        st.info(f"💬 Suggestion copied! Paste it in the chat.")
                
                with col2:
                    st.caption(f"{sug.relevance_score:.0%}")
        
        st.markdown("")


def _render_prompts_tab(conversation_id: int, user_id: int, messages: list):
    """Render smart prompts library tab"""
    
    st.markdown("## 📚 Smart Prompt Library")
    st.markdown("*Pre-built and contextual prompt templates*")
    
    library = SmartPromptLibrary()
    
    # Tabs for different views
    prompt_tab1, prompt_tab2, prompt_tab3 = st.tabs([
        "🎯 Contextual",
        "📁 By Category", 
        "❓ Follow-up Questions"
    ])
    
    with prompt_tab1:
        st.markdown("### 🎯 Contextual Prompts for This Conversation")
        contextual = library.get_contextual_prompts(messages, limit=8)
        
        if contextual:
            for prompt in contextual:
                with st.expander(f"{prompt.title} - {prompt.complexity.title()}", expanded=False):
                    st.markdown(f"**Category:** {prompt.category}")
                    st.markdown(f"**Template:**")
                    st.code(prompt.text, language=None)
                    st.markdown(f"*Tags: {', '.join(prompt.tags)}*")
                    
                    if st.button(f"📋 Use This Prompt", key=f"ctx_{prompt.title}"):
                        st.session_state.selected_prompt = prompt.text
                        st.info("✅ Prompt ready! Fill in the placeholders and use in chat.")
        else:
            st.info("No contextual prompts available yet.")
    
    with prompt_tab2:
        st.markdown("### 📁 Browse by Category")
        
        categories = library.get_all_categories()
        selected_cat = st.selectbox("Select Category", categories, key="cat_select")
        complexity = st.radio(
            "Complexity Level",
            ["All", "beginner", "intermediate", "advanced"],
            horizontal=True,
            key="complexity_select"
        )
        
        complexity_filter = None if complexity == "All" else complexity
        prompts = library.get_prompts_by_category(selected_cat, complexity_filter)
        
        st.markdown(f"**{len(prompts)} prompts in {selected_cat}**")
        
        for prompt in prompts:
            with st.expander(f"📝 {prompt.title} ({prompt.complexity})", expanded=False):
                st.code(prompt.text, language=None)
                st.caption(f"Tags: {', '.join(prompt.tags)}")
                
                if st.button(f"Use This Prompt", key=f"cat_{prompt.title}_{prompt.complexity}"):
                    st.session_state.selected_prompt = prompt.text
                    st.success("✅ Prompt ready to use!")
    
    with prompt_tab3:
        st.markdown("### ❓ Intelligent Follow-up Questions")
        
        col1, col2 = st.columns([3, 1])
        with col2:
            if st.button("🔄 Generate", use_container_width=True):
                with st.spinner("Generating..."):
                    questions = generate_follow_up_questions(
                        conversation_id, user_id, num_questions=5, save_to_db=True
                    )
                    st.success(f"✅ {len(questions)} questions generated!")
                    st.rerun()
        
        # Get or generate questions
        questions = generate_follow_up_questions(
            conversation_id, user_id, num_questions=5, save_to_db=False
        )
        
        if questions:
            # Group by intent
            intents = {}
            for q in questions:
                if q.intent not in intents:
                    intents[q.intent] = []
                intents[q.intent].append(q)
            
            intent_icons = {
                'clarify': '🔍',
                'expand': '📖',
                'validate': '✅',
                'explore': '🌐',
                'apply': '⚙️'
            }
            
            for intent, intent_questions in intents.items():
                icon = intent_icons.get(intent, '❓')
                st.markdown(f"#### {icon} {intent.title()}")
                
                for q in intent_questions:
                    priority_badge = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[q.priority]
                    
                    if st.button(
                        f"{priority_badge} {q.question}",
                        key=f"fq_{intent}_{q.question[:30]}",
                        use_container_width=True
                    ):
                        st.session_state.selected_question = q.question
                        st.info("💬 Question ready to ask!")
                    
                    st.caption(f"*{q.context}*")
                    st.markdown("")
        else:
            st.info("No follow-up questions generated yet.")


def _render_insights_tab(conversation_id: int, user_id: int, messages: list):
    """Render deep insights tab"""
    
    st.markdown("## 🔍 Deep Conversation Insights")
    st.markdown("*Topic extraction, entity recognition, and analytics*")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if st.button("🔄 Analyze", use_container_width=True):
            with st.spinner("Analyzing conversation..."):
                insights = analyze_conversation(conversation_id, user_id)
                st.success("✅ Analysis complete!")
                st.rerun()
    
    # Get or generate insights
    insights = get_conversation_insights(conversation_id)
    
    if not insights:
        with st.spinner("Analyzing conversation..."):
            insights = analyze_conversation(conversation_id, user_id)
    
    if not insights:
        st.error("❌ Could not analyze conversation")
        return
    
    st.markdown("---")
    
    # Overview metrics
    st.markdown("### 📊 Overview")
    metrics = st.columns(4)
    with metrics[0]:
        st.metric("🎭 Type", insights.conversation_type.title())
    with metrics[1]:
        st.metric("📈 Complexity", insights.complexity_level.title())
    with metrics[2]:
        st.metric("📨 Messages", insights.total_messages)
    with metrics[3]:
        duration = insights.conversation_duration_minutes
        st.metric("⏱️ Duration", f"{duration}m" if duration else "N/A")
    
    st.markdown("---")
    
    # Topics
    if insights.main_topics:
        st.markdown("### 🎯 Main Topics")
        
        # Show top topics with scores
        for i, topic_data in enumerate(insights.main_topics[:10], 1):
            topic = topic_data['topic']
            score = topic_data.get('score', 0)
            freq = topic_data.get('frequency', 0)
            
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{i}. {topic}**")
            with col2:
                st.caption(f"Score: {score:.1f}")
            with col3:
                st.caption(f"Freq: {freq}")
    
    # Topic Clusters
    if insights.topic_clusters:
        st.markdown("### 🗂️ Topic Clusters")
        
        for cluster_name, topics in insights.topic_clusters.items():
            with st.expander(f"📁 {cluster_name.replace('_', ' ').title()} ({len(topics)} topics)"):
                st.markdown(", ".join(topics))
    
    # Entities
    if insights.entities:
        st.markdown("### 🏷️ Entities Recognized")
        
        entity_cols = st.columns(len(insights.entities))
        for idx, (entity_type, entities) in enumerate(insights.entities.items()):
            with entity_cols[idx]:
                st.markdown(f"**{entity_type.replace('_', ' ').title()}**")
                for entity_data in entities[:5]:
                    entity_text = entity_data.get('text', '')
                    freq = entity_data.get('frequency', 0)
                    st.caption(f"• {entity_text} ({freq})")
    
    # Statistics
    st.markdown("---")
    st.markdown("### 📊 Statistics")
    
    stats_cols = st.columns(3)
    with stats_cols[0]:
        st.metric("User Messages", insights.user_messages)
        st.metric("Questions Asked", insights.total_messages // 2)  # Approximation
    with stats_cols[1]:
        st.metric("Assistant Messages", insights.assistant_messages)
        st.metric("Avg Message Length", f"{insights.avg_message_length:.0f} chars")
    with stats_cols[2]:
        engagement = insights.user_messages / insights.total_messages if insights.total_messages > 0 else 0
        st.metric("Engagement Ratio", f"{engagement:.0%}")
    
    # Relationships
    if insights.relationships:
        st.markdown("---")
        st.markdown("### 🔗 Topic Relationships")
        
        with st.expander(f"View {len(insights.relationships)} relationships"):
            for rel in insights.relationships[:10]:
                st.markdown(
                    f"**{rel['from']}** --[{rel['type']}]--> **{rel['to']}** "
                    f"*(strength: {rel['strength']})*"
                )


def _render_export_tab(conversation_id: int, user_id: int):
    """Render export tab"""
    
    st.markdown("## 📄 Export Conversation")
    st.markdown("*Export with AI-generated summaries in multiple formats*")
    st.markdown("---")
    
    # Export options
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "📁 Format",
            ["markdown", "html", "json"],
            format_func=lambda x: {
                'markdown': '📝 Markdown (.md)',
                'html': '🌐 HTML (.html)',
                'json': '📊 JSON (.json)'
            }[x]
        )
    
    with col2:
        template = st.selectbox(
            "📋 Template",
            ["standard", "business", "technical", "meeting_notes"],
            format_func=lambda x: x.replace('_', ' ').title()
        )
    
    include_summary = st.checkbox("✅ Include Executive Summary", value=True)
    privacy_mode = st.checkbox("🔒 Privacy Mode (redact sensitive info)", value=False)
    
    st.markdown("---")
    
    if st.button("📥 Export Conversation", type="primary", use_container_width=True):
        try:
            with st.spinner(f"Exporting as {export_format.upper()}..."):
                filepath = export_conversation(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    export_format=export_format,
                    template=template,
                    include_summary=include_summary,
                    privacy_mode=privacy_mode
                )
                
                # Read file for download
                with open(filepath, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                
                # Get filename
                filename = Path(filepath).name
                
                # Offer download
                st.success(f"✅ Export successful!")
                
                st.download_button(
                    label=f"⬇️ Download {export_format.upper()}",
                    data=file_content,
                    file_name=filename,
                    mime={
                        'markdown': 'text/markdown',
                        'html': 'text/html',
                        'json': 'application/json'
                    }[export_format],
                    use_container_width=True
                )
                
                # Show preview
                with st.expander("👀 Preview"):
                    if export_format == 'json':
                        st.json(json.loads(file_content))
                    else:
                        st.code(file_content[:1000] + "..." if len(file_content) > 1000 else file_content)
                
        except Exception as e:
            st.error(f"❌ Export failed: {str(e)}")


def _render_prompt_library_standalone():
    """Render standalone prompt library when no conversation is active"""
    
    st.markdown("### 📚 Browse Smart Prompts")
    
    library = SmartPromptLibrary()
    categories = library.get_all_categories()
    
    selected_cat = st.selectbox("Category", categories)
    prompts = library.get_prompts_by_category(selected_cat)
    
    st.markdown(f"**{len(prompts)} prompts available**")
    
    for prompt in prompts:
        with st.expander(f"{prompt.title} - {prompt.complexity.title()}"):
            st.code(prompt.text, language=None)
            st.caption(f"Tags: {', '.join(prompt.tags)}")
            
            if st.button(f"📋 Copy Template", key=f"standalone_{prompt.title}"):
                st.session_state.selected_prompt = prompt.text
                st.success("✅ Template copied!")

