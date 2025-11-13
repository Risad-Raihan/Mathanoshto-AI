"""
Memory Manager UI Component for Streamlit
Beautiful interface for viewing, managing, and organizing long-term memories
"""
import streamlit as st
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime, timedelta
import json

from backend.core.memory_manager import MemoryManager, MemoryEmbedder, VectorStore
from backend.database.memory_operations import MemoryDB
from backend.database.operations import get_db
from frontend.streamlit.components.ui_utils import (
    show_toast,
    render_empty_state,
    show_confirmation_dialog
)


class MemoryManagerUI:
    """Memory management interface with modern UI"""
    
    # Memory type configurations
    MEMORY_TYPES = {
        'personal_info': {
            'name': 'Personal Info',
            'icon': '👤',
            'color': '#4a7c59',
            'description': 'Name, age, location, occupation, family'
        },
        'preference': {
            'name': 'Preferences',
            'icon': '⭐',
            'color': '#6b8e23',
            'description': 'Likes, dislikes, interests, hobbies'
        },
        'fact': {
            'name': 'Facts',
            'icon': '💡',
            'color': '#8fbc8f',
            'description': 'Important facts and knowledge'
        },
        'task': {
            'name': 'Tasks',
            'icon': '✅',
            'color': '#52b788',
            'description': 'Things to do, reminders'
        },
        'goal': {
            'name': 'Goals',
            'icon': '🎯',
            'color': '#7fa99b',
            'description': 'Aspirations and objectives'
        },
        'relationship': {
            'name': 'Relationships',
            'icon': '👥',
            'color': '#5a6352',
            'description': 'Information about people'
        },
        'conversation_summary': {
            'name': 'Past Discussions',
            'icon': '💬',
            'color': '#d4c5a9',
            'description': 'Summaries of previous conversations'
        }
    }
    
    @staticmethod
    def render():
        """Main render method for memory manager"""
        if 'user_id' not in st.session_state:
            st.warning("⚠️ Please log in to access memory management.")
            return
        
        user_id = st.session_state.user_id
        
        # Initialize session state
        MemoryManagerUI._init_session_state()
        
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>🧠 Memory System</h1>
            <p style='color: var(--color-text-secondary);'>
                Your AI's long-term memory - Remembers important context across conversations
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Get database session
        db = get_db()
        
        # Create tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "💾 All Memories",
            "➕ Add Memory",
            "🔍 Search",
            "⚙️ Settings"
        ])
        
        with tab1:
            MemoryManagerUI.render_overview(db, user_id)
        
        with tab2:
            MemoryManagerUI.render_memories_list(db, user_id)
        
        with tab3:
            MemoryManagerUI.render_add_memory(db, user_id)
        
        with tab4:
            MemoryManagerUI.render_search(db, user_id)
        
        with tab5:
            MemoryManagerUI.render_settings(db, user_id)
    
    @staticmethod
    def _init_session_state():
        """Initialize session state variables"""
        defaults = {
            'memory_filter_type': 'all',
            'memory_sort': 'importance',
            'show_inactive': False
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    @staticmethod
    def render_overview(db, user_id: int):
        """Render overview dashboard"""
        st.markdown("### 📊 Memory Dashboard")
        
        # Get statistics
        stats = MemoryDB.get_memory_stats(db, user_id)
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Memories",
                stats['total_memories'],
                help="Total number of active memories"
            )
        
        with col2:
            st.metric(
                "Pinned",
                stats['pinned_count'],
                help="Always included in context"
            )
        
        with col3:
            st.metric(
                "Verified",
                stats['verified_count'],
                help="User-confirmed memories"
            )
        
        with col4:
            st.metric(
                "Avg. Importance",
                f"{stats['average_importance']:.2f}",
                help="Average importance score"
            )
        
        st.divider()
        
        # Memory breakdown by type
        st.markdown("#### 📈 Memory Distribution")
        
        by_type = stats['by_type']
        if by_type:
            # Create columns for each type
            type_cols = st.columns(len(MemoryManagerUI.MEMORY_TYPES))
            
            for idx, (type_key, type_config) in enumerate(MemoryManagerUI.MEMORY_TYPES.items()):
                with type_cols[idx]:
                    count = by_type.get(type_key, 0)
                    st.markdown(f"""
                    <div style='text-align: center; padding: 1rem; background: rgba(74, 124, 89, 0.1); border-radius: 10px;'>
                        <div style='font-size: 2rem;'>{type_config['icon']}</div>
                        <div style='font-size: 1.5rem; font-weight: bold; color: {type_config['color']};'>{count}</div>
                        <div style='font-size: 0.8rem; color: var(--color-text-secondary);'>{type_config['name']}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            render_empty_state(
                icon="🧠",
                title="No Memories Yet",
                description="Start by adding your first memory or have a conversation!"
            )
        
        st.divider()
        
        # Most accessed memories
        if stats['most_accessed']:
            st.markdown("#### 🔥 Most Accessed Memories")
            
            for memory in stats['most_accessed']:
                MemoryManagerUI._render_memory_card(memory, compact=True)
    
    @staticmethod
    def render_memories_list(db, user_id: int):
        """Render list of all memories"""
        st.markdown("### 💾 All Memories")
        
        # Filters
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            filter_type = st.selectbox(
                "Filter by Type",
                options=['all'] + list(MemoryManagerUI.MEMORY_TYPES.keys()),
                format_func=lambda x: 'All Types' if x == 'all' else MemoryManagerUI.MEMORY_TYPES[x]['name']
            )
        
        with col2:
            sort_by = st.selectbox(
                "Sort By",
                options=['importance', 'recent', 'accessed', 'oldest'],
                format_func=lambda x: {
                    'importance': 'Importance',
                    'recent': 'Most Recent',
                    'accessed': 'Most Accessed',
                    'oldest': 'Oldest First'
                }[x]
            )
        
        with col3:
            show_inactive = st.checkbox("Show Deleted", value=False)
        
        # Get memories
        memory_types = None if filter_type == 'all' else [filter_type]
        memories = MemoryDB.get_user_memories(
            db=db,
            user_id=user_id,
            memory_types=memory_types,
            is_active=not show_inactive,
            limit=100
        )
        
        # Sort memories
        if sort_by == 'recent':
            memories = sorted(memories, key=lambda m: m.created_at, reverse=True)
        elif sort_by == 'accessed':
            memories = sorted(memories, key=lambda m: m.access_count, reverse=True)
        elif sort_by == 'oldest':
            memories = sorted(memories, key=lambda m: m.created_at)
        # importance is default from query
        
        st.divider()
        
        if not memories:
            render_empty_state(
                icon="💭",
                title="No Memories Found",
                description="Try adjusting the filters or add some new memories"
            )
        else:
            st.markdown(f"**Found {len(memories)} memories**")
            
            for memory in memories:
                MemoryManagerUI._render_memory_card(
                    memory.to_dict(),
                    memory_obj=memory,
                    db=db,
                    compact=False
                )
    
    @staticmethod
    def _render_memory_card(memory_dict: Dict, memory_obj=None, db=None, compact: bool = False):
        """Render a single memory card"""
        mem_type = memory_dict['memory_type']
        type_config = MemoryManagerUI.MEMORY_TYPES.get(mem_type, {
            'name': mem_type,
            'icon': '📌',
            'color': '#52b788'
        })
        
        # Importance indicator
        importance = memory_dict['importance_score']
        importance_icon = "🔴" if importance > 0.8 else "🟡" if importance > 0.5 else "⚪"
        
        # Card style
        card_style = f"""
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(157, 78, 221, 0.05));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-left: 4px solid {type_config['color']};
        border-radius: 15px;
        padding: {'0.75rem' if compact else '1rem'};
        margin-bottom: 1rem;
        """
        
        with st.container():
            st.markdown(f'<div style="{card_style}">', unsafe_allow_html=True)
            
            # Header
            col1, col2 = st.columns([5, 1])
            
            with col1:
                pinned_badge = "📌 " if memory_dict.get('is_pinned') else ""
                verified_badge = "✅ " if memory_dict.get('is_verified') else ""
                
                st.markdown(f"""
                <div style='display: flex; align-items: center; gap: 0.5rem;'>
                    <span style='font-size: 1.5rem;'>{type_config['icon']}</span>
                    <span style='font-weight: 600; color: {type_config['color']};'>{type_config['name']}</span>
                    <span>{pinned_badge}{verified_badge}{importance_icon}</span>
                </div>
                """, unsafe_allow_html=True)
            
            # Content
            st.markdown(f"**{memory_dict['content']}**")
            
            if not compact:
                # Metadata
                metadata_parts = []
                
                if memory_dict.get('category'):
                    metadata_parts.append(f"📁 {memory_dict['category']}")
                
                if memory_dict.get('tags'):
                    tags_html = ' '.join([f'`{tag}`' for tag in memory_dict['tags']])
                    metadata_parts.append(f"🏷️ {tags_html}")
                
                metadata_parts.append(f"🔢 Importance: {importance:.2f}")
                metadata_parts.append(f"📊 Accessed {memory_dict.get('access_count', 0)} times")
                
                created = datetime.fromisoformat(memory_dict['created_at'])
                metadata_parts.append(f"📅 Created: {created.strftime('%Y-%m-%d')}")
                
                st.caption(" • ".join(metadata_parts))
                
                # Actions
                if memory_obj and db:
                    action_cols = st.columns([1, 1, 1, 1, 4])
                    
                    with action_cols[0]:
                        if st.button("✏️", key=f"edit_{memory_dict['id']}", help="Edit"):
                            st.session_state[f"editing_{memory_dict['id']}"] = True
                            st.rerun()
                    
                    with action_cols[1]:
                        pin_icon = "📌" if not memory_dict.get('is_pinned') else "📍"
                        if st.button(pin_icon, key=f"pin_{memory_dict['id']}", help="Toggle Pin"):
                            MemoryDB.update_memory(
                                db, memory_dict['id'],
                                is_pinned=not memory_dict.get('is_pinned')
                            )
                            show_toast("Memory updated!", "success")
                            st.rerun()
                    
                    with action_cols[2]:
                        verify_icon = "✅" if not memory_dict.get('is_verified') else "❎"
                        if st.button(verify_icon, key=f"verify_{memory_dict['id']}", help="Toggle Verify"):
                            MemoryDB.update_memory(
                                db, memory_dict['id'],
                                is_verified=not memory_dict.get('is_verified')
                            )
                            show_toast("Memory updated!", "success")
                            st.rerun()
                    
                    with action_cols[3]:
                        if st.button("🗑️", key=f"delete_{memory_dict['id']}", help="Delete"):
                            MemoryDB.delete_memory(db, memory_dict['id'], soft_delete=True)
                            show_toast("Memory deleted!", "success")
                            st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    @staticmethod
    def render_add_memory(db, user_id: int):
        """Render add memory form"""
        st.markdown("### ➕ Add New Memory")
        
        with st.form("add_memory_form"):
            # Memory content
            content = st.text_area(
                "Memory Content",
                placeholder="Enter what you want the AI to remember...",
                help="Describe the information clearly and concisely",
                height=100,
                key="memory_content_input"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                memory_type = st.selectbox(
                    "Type",
                    options=list(MemoryManagerUI.MEMORY_TYPES.keys()),
                    format_func=lambda x: f"{MemoryManagerUI.MEMORY_TYPES[x]['icon']} {MemoryManagerUI.MEMORY_TYPES[x]['name']}",
                    key="memory_type_select"
                )
            
            with col2:
                category = st.text_input(
                    "Category (Optional)",
                    placeholder="e.g., hobby, work, family",
                    key="memory_category_input"
                )
            
            # Tags
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="tag1, tag2, tag3",
                key="memory_tags_input"
            )
            
            # Importance slider
            importance = st.slider(
                "Importance",
                min_value=0.0,
                max_value=1.0,
                value=0.5,
                step=0.1,
                help="How important is this memory? (0=low, 1=critical)",
                key="memory_importance_slider"
            )
            
            # Options
            col3, col4 = st.columns(2)
            with col3:
                is_pinned = st.checkbox(
                    "📌 Pin this memory",
                    help="Always include in AI context",
                    key="memory_is_pinned_checkbox"
                )
            with col4:
                is_verified = st.checkbox(
                    "✅ Mark as verified",
                    help="Confirm this information is accurate",
                    key="memory_is_verified_checkbox"
                )
            
            # Submit
            submitted = st.form_submit_button(
                "💾 Save Memory",
                use_container_width=True,
                type="primary"
            )
            
            if submitted:
                if not content.strip():
                    st.error("❌ Memory content cannot be empty!")
                else:
                    # Parse tags
                    tags = [t.strip() for t in tags_input.split(',') if t.strip()]
                    
                    # Create memory
                    try:
                        from backend.core.memory_manager import get_memory_manager
                        memory_manager = get_memory_manager(db)
                        
                        memory = memory_manager.create_memory(
                            user_id=user_id,
                            content=content.strip(),
                            memory_type=memory_type,
                            category=category.strip() if category else None,
                            tags=tags,
                            importance_score=importance,
                            source_type='manual',
                            is_pinned=is_pinned,
                            meta_data={'is_verified': is_verified}
                        )
                        
                        if memory:
                            st.success("✅ Memory saved successfully!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Failed to save memory. Please try again.")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
    
    @staticmethod
    def render_search(db, user_id: int):
        """Render semantic search interface"""
        st.markdown("### 🔍 Search Memories")
        st.caption("Semantic search - finds memories by meaning, not just keywords")
        
        # Search input
        query = st.text_input(
            "Search Query",
            placeholder="What do you want to find?",
            help="Enter a question or description"
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_types = st.multiselect(
                "Filter by Type",
                options=list(MemoryManagerUI.MEMORY_TYPES.keys()),
                format_func=lambda x: f"{MemoryManagerUI.MEMORY_TYPES[x]['icon']} {MemoryManagerUI.MEMORY_TYPES[x]['name']}"
            )
        
        with col2:
            limit = st.number_input(
                "Max Results",
                min_value=5,
                max_value=50,
                value=10,
                step=5
            )
        
        if st.button("🔍 Search", use_container_width=True, type="primary"):
            if not query.strip():
                st.warning("⚠️ Please enter a search query")
            else:
                with st.spinner("Searching memories..."):
                    try:
                        from backend.core.memory_manager import get_memory_manager
                        memory_manager = get_memory_manager(db)
                        
                        results = memory_manager.search_memories(
                            user_id=user_id,
                            query=query,
                            memory_types=search_types if search_types else None,
                            limit=limit,
                            min_similarity=0.5
                        )
                        
                        if not results:
                            st.info("ℹ️ No memories found matching your query")
                        else:
                            st.success(f"✅ Found {len(results)} relevant memories")
                            st.divider()
                            
                            for memory, similarity in results:
                                # Similarity badge
                                similarity_pct = similarity * 100
                                similarity_color = "#52b788" if similarity > 0.8 else "#e9c46a" if similarity > 0.6 else "#e76f51"
                                
                                st.markdown(f"""
                                <div style='display: inline-block; background: {similarity_color}; color: white; padding: 0.2rem 0.5rem; border-radius: 5px; font-size: 0.8rem; font-weight: bold; margin-bottom: 0.5rem;'>
                                    {similarity_pct:.1f}% Match
                                </div>
                                """, unsafe_allow_html=True)
                                
                                MemoryManagerUI._render_memory_card(
                                    memory.to_dict(),
                                    memory_obj=memory,
                                    db=db,
                                    compact=False
                                )
                    
                    except Exception as e:
                        st.error(f"❌ Search error: {str(e)}")
    
    @staticmethod
    def render_settings(db, user_id: int):
        """Render memory system settings"""
        st.markdown("### ⚙️ Memory Settings")
        
        # Auto-extraction settings
        st.markdown("#### 🤖 Automatic Memory Extraction")
        
        auto_extract = st.checkbox(
            "Enable automatic memory extraction",
            value=st.session_state.get('auto_memory_extraction', True),
            help="Automatically extract important facts from conversations"
        )
        st.session_state.auto_memory_extraction = auto_extract
        
        if auto_extract:
            extract_frequency = st.selectbox(
                "Extraction Frequency",
                options=['every_message', 'every_5_messages', 'end_of_conversation'],
                format_func=lambda x: {
                    'every_message': 'After every message',
                    'every_5_messages': 'Every 5 messages',
                    'end_of_conversation': 'At end of conversation'
                }[x]
            )
            st.session_state.memory_extract_frequency = extract_frequency
        
        st.divider()
        
        # Context injection settings
        st.markdown("#### 💉 Memory Injection")
        
        auto_inject = st.checkbox(
            "Automatically inject relevant memories",
            value=st.session_state.get('auto_memory_injection', True),
            help="Include relevant memories in AI context automatically"
        )
        st.session_state.auto_memory_injection = auto_inject
        
        if auto_inject:
            max_memories = st.slider(
                "Max memories per request",
                min_value=3,
                max_value=20,
                value=10,
                help="Maximum number of memories to include in context"
            )
            st.session_state.max_memories_per_request = max_memories
        
        st.divider()
        
        # Danger zone
        st.markdown("#### ⚠️ Danger Zone")
        
        if st.button("🗑️ Delete All Memories", type="secondary"):
            st.warning("⚠️ This will delete ALL your memories. Are you sure?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Yes, delete all", key="confirm_delete_all"):
                    memories = MemoryDB.get_user_memories(
                        db, user_id, is_active=True, limit=1000
                    )
                    for memory in memories:
                        MemoryDB.delete_memory(db, memory.id, soft_delete=True)
                    st.success("✅ All memories deleted")
                    st.rerun()
            with col2:
                if st.button("Cancel", key="cancel_delete_all"):
                    st.rerun()


def render_memory_manager():
    """Wrapper function to render memory manager UI"""
    MemoryManagerUI.render()

