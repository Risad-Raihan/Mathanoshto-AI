"""
Sidebar component with settings and controls
"""
import streamlit as st
from backend.core.model_factory import model_factory
from backend.database.operations import ConversationDB, MessageDB
from frontend.streamlit.components.ui_utils import (
    render_conversation_card,
    render_empty_state,
    show_confirmation_dialog,
    show_toast,
    render_dark_mode_toggle
)
from frontend.streamlit.components.login import logout
from frontend.streamlit.components.api_keys import render_api_key_management
from frontend.streamlit.components.profile import render_user_profile
from datetime import datetime

def render_sidebar() -> dict:
    """
    Render sidebar with settings
    
    Returns:
        dict: Current settings (provider, model, temperature, etc.)
    """
    # Get user info from session
    user_id = st.session_state.get('user_id')
    username = st.session_state.get('username', 'User')
    full_name = st.session_state.get('full_name', username)
    
    with st.sidebar:
        # User info header with clean icons
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; padding: 0.5rem 0; margin-bottom: 0.5rem;">
            <div style="flex-grow: 1;">
                <div style="font-size: 1.1rem; font-weight: 600; color: var(--color-text-primary);">
                    {full_name}
                </div>
                <div style="font-size: 0.85rem; color: var(--color-text-secondary); opacity: 0.8;">
                    @{username}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Minimal icon buttons
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button("👤", key="profile_btn", use_container_width=True, help="Profile"):
                st.session_state.show_profile = True
                st.session_state.show_file_manager = False
                st.session_state.show_diagram_generator = False
        with col2:
            if st.button("📁", key="files_btn", use_container_width=True, help="Files"):
                st.session_state.show_file_manager = True
                st.session_state.show_profile = False
                st.session_state.show_diagram_generator = False
        with col3:
            if st.button("📊", key="diagram_btn", use_container_width=True, help="Diagram Generator"):
                st.session_state.show_diagram_generator = True
                st.session_state.show_profile = False
                st.session_state.show_file_manager = False
        with col4:
            if st.button("🚪", key="logout_btn", use_container_width=True, help="Logout"):
                logout()
        
        st.divider()
        
        st.title("⚙️ Settings")
        
        # Provider selection
        available_providers = model_factory.get_available_providers()
        
        if not available_providers:
            st.error("❌ No LLM providers available. Please check your API keys in .env file.")
            st.info("Add OPENAI_API_KEY and/or GEMINI_API_KEY to your .env file")
            return {}
        
        provider = st.selectbox(
            "Provider",
            available_providers,
            format_func=lambda x: x.upper()
        )
        
        # Model selection (dynamic based on provider)
        models = model_factory.get_models_for_provider(provider)
        model_options = {m.display_name: m.name for m in models}
        
        selected_display_name = st.selectbox(
            "Model",
            list(model_options.keys())
        )
        model = model_options[selected_display_name]
        
        # Show model info
        model_info = model_factory.get_model_info(provider, model)
        if model_info:
            with st.expander("ℹ️ Model Info"):
                st.write(f"**Description:** {model_info.description}")
                st.write(f"**Context Window:** {model_info.context_window:,} tokens")
                st.write(f"**Max Output:** {model_info.max_output_tokens:,} tokens")
                st.write(f"**Vision Support:** {'✅' if model_info.supports_vision else '❌'}")
                st.write(f"**Tools Support:** {'✅' if model_info.supports_tools else '❌'}")
                st.write(f"**Cost:** ${model_info.cost_per_1m_input_tokens:.2f} / ${model_info.cost_per_1m_output_tokens:.2f} per 1M tokens")
        
        st.divider()
        
        # Advanced settings
        with st.expander("🎛️ Advanced Settings"):
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Higher values make output more random"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=4000,
                value=2000,
                step=100,
                help="Maximum tokens to generate"
            )
            
            system_prompt = st.text_area(
                "System Prompt (Optional)",
                placeholder="You are a helpful assistant...",
                help="Set the behavior of the assistant"
            )
        
        st.divider()
        
        # Tools
        st.subheader("🛠️ Tools")
        use_tavily = st.checkbox(
            "Enable Web Search (Tavily)",
            value=False,
            help="Search the web for current information and real-time data"
        )
        
        use_web_scraper = st.checkbox(
            "Enable Web Scraper",
            value=False,
            help="Scrape and extract content from any URL, including articles, documentation, and web pages"
        )
        
        use_youtube = st.checkbox(
            "Enable YouTube Summarizer",
            value=False,
            help="Summarize YouTube videos, extract transcripts, and get key moments with timestamps"
        )
        
        use_data_analyzer = st.checkbox(
            "Enable Data Analyzer",
            value=False,
            help="Analyze CSV/Excel files, create visualizations, get statistics, and generate pandas code"
        )
        
        st.divider()
        
        # API Key Management
        with st.expander("🔑 API Keys", expanded=False):
            render_api_key_management()
        
        st.divider()
        
        # Dark Mode Toggle
        render_dark_mode_toggle()
        
        st.divider()
        
        # Conversation management
        st.subheader("💬 Conversations")
        
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.chat_manager = None
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        # List recent conversations for this user
        conversations = ConversationDB.list_conversations(user_id=user_id, limit=10)
        
        if conversations:
            st.write("**Recent:**")
            
            for conv in conversations:
                # Check if delete confirmation is needed
                if st.session_state.get(f"confirm_delete_{conv.id}", False):
                    with st.container():
                        st.warning(f"Delete '{conv.title[:20]}...'?")
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Yes, delete", key=f"confirm_yes_{conv.id}", use_container_width=True):
                                ConversationDB.delete_conversation(conv.id)
                                st.session_state[f"confirm_delete_{conv.id}"] = False
                                show_toast("Conversation deleted", "success")
                                st.rerun()
                        with col2:
                            if st.button("Cancel", key=f"confirm_no_{conv.id}", use_container_width=True):
                                st.session_state[f"confirm_delete_{conv.id}"] = False
                                st.rerun()
                    continue
                
                # Get conversation metadata
                message_count = MessageDB.get_message_count(conv.id)
                token_usage = MessageDB.get_conversation_tokens(conv.id)
                
                # Render conversation card with actions
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    # Truncate long titles
                    display_title = conv.title[:30] + "..." if len(conv.title) > 30 else conv.title
                    if st.button(
                        f"📝 {display_title}",
                        key=f"conv_{conv.id}",
                        use_container_width=True
                    ):
                        # Load conversation
                        from backend.core.chat_manager import ChatManager
                        st.session_state.chat_manager = ChatManager(user_id=user_id, conversation_id=conv.id)
                        st.session_state.current_conversation_id = conv.id
                        st.session_state.messages = st.session_state.chat_manager.get_conversation_history()
                        st.rerun()
                    
                    # Display metadata
                    time_diff = datetime.now() - conv.created_at
                    if time_diff.days == 0:
                        if time_diff.seconds < 3600:
                            time_str = f"{time_diff.seconds // 60}m ago"
                        else:
                            time_str = f"{time_diff.seconds // 3600}h ago"
                    elif time_diff.days == 1:
                        time_str = "Yesterday"
                    elif time_diff.days < 7:
                        time_str = f"{time_diff.days}d ago"
                    else:
                        time_str = conv.created_at.strftime("%b %d")
                    
                    st.caption(
                        f"🕒 {time_str} • 💬 {message_count} • "
                        f"🔢 {token_usage['total_tokens']:,} • "
                        f"💰 ${token_usage['total_cost']:.4f}"
                    )
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv.id}", help="Delete conversation"):
                        st.session_state[f"confirm_delete_{conv.id}"] = True
                        st.rerun()
        else:
            # Empty state for no conversations
            st.markdown("""
            <div class="empty-state">
                <div class="empty-state-icon">💬</div>
                <div class="empty-state-description">No conversations yet</div>
            </div>
            """, unsafe_allow_html=True)
    
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system_prompt": system_prompt if system_prompt else None,
        "use_tavily": use_tavily,
        "use_web_scraper": use_web_scraper,
        "use_youtube": use_youtube,
        "use_data_analyzer": use_data_analyzer
    }

