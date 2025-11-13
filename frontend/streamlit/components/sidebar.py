"""
Sidebar component with settings and controls
"""
import streamlit as st
from backend.core.model_factory import model_factory
from backend.database.operations import ConversationDB, MessageDB, get_db
from backend.core.agent_manager import get_agent_manager
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
        
        # Minimal icon buttons (two rows)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        with col1:
            if st.button("👤", key="profile_btn", use_container_width=True, help="Profile"):
                st.session_state.show_profile = True
                st.session_state.show_file_manager = False
                st.session_state.show_diagram_generator = False
                st.session_state.show_memory_manager = False
                st.session_state.show_insights_panel = False
                st.session_state.show_image_gallery = False
        with col2:
            if st.button("📁", key="files_btn", use_container_width=True, help="Files"):
                st.session_state.show_file_manager = True
                st.session_state.show_profile = False
                st.session_state.show_diagram_generator = False
                st.session_state.show_memory_manager = False
                st.session_state.show_insights_panel = False
                st.session_state.show_image_gallery = False
        with col3:
            if st.button("📊", key="diagram_btn", use_container_width=True, help="Diagrams"):
                st.session_state.show_diagram_generator = True
                st.session_state.show_profile = False
                st.session_state.show_file_manager = False
                st.session_state.show_memory_manager = False
                st.session_state.show_insights_panel = False
                st.session_state.show_image_gallery = False
        with col4:
            if st.button("🖼️", key="gallery_btn", use_container_width=True, help="Image Gallery"):
                st.session_state.show_image_gallery = True
                st.session_state.show_profile = False
                st.session_state.show_file_manager = False
                st.session_state.show_diagram_generator = False
                st.session_state.show_memory_manager = False
                st.session_state.show_insights_panel = False
        
        col5, col6, col7, col8 = st.columns([1, 1, 1, 1])
        with col5:
            if st.button("🧠", key="memory_btn", use_container_width=True, help="Memory"):
                st.session_state.show_memory_manager = True
                st.session_state.show_profile = False
                st.session_state.show_file_manager = False
                st.session_state.show_diagram_generator = False
                st.session_state.show_insights_panel = False
                st.session_state.show_image_gallery = False
        with col6:
            if st.button("💡", key="insights_btn", use_container_width=True, help="Insights"):
                st.session_state.show_insights_panel = True
                st.session_state.show_profile = False
                st.session_state.show_file_manager = False
                st.session_state.show_diagram_generator = False
                st.session_state.show_memory_manager = False
                st.session_state.show_image_gallery = False
        with col7:
            # Placeholder for future features
            pass
        with col8:
            if st.button("🚪", key="logout_btn", use_container_width=True, help="Logout"):
                logout()
        
        st.divider()
        
        # 🤖 AI Agent Selection
        st.subheader("🤖 AI Agent")
        
        # Load agents from database
        try:
            db = get_db()
            agent_manager = get_agent_manager(db)
            agents = agent_manager.get_all_agents(
                is_active=True,
                include_custom=True,
                user_id=user_id
            )
            db.close()
            
            if agents:
                # Group agents by category
                categories = {}
                for agent in agents:
                    if agent.category not in categories:
                        categories[agent.category] = []
                    categories[agent.category].append(agent)
                
                # Agent selection dropdown with emoji and name
                agent_options = {
                    f"{agent.emoji} {agent.name}": agent.id
                    for agent in agents
                }
                
                # Add "None" option for custom settings
                agent_options = {"⚙️ Custom Settings (Manual)": None, **agent_options}
                
                # Get currently selected agent from session state
                current_selection = st.session_state.get('selected_agent_id', None)
                current_agent_name = None
                
                if current_selection:
                    for name, agent_id in agent_options.items():
                        if agent_id == current_selection:
                            current_agent_name = name
                            break
                
                if not current_agent_name:
                    current_agent_name = "⚙️ Custom Settings (Manual)"
                
                selected_agent_name = st.selectbox(
                    "Select Agent",
                    list(agent_options.keys()),
                    index=list(agent_options.keys()).index(current_agent_name),
                    help="Choose a specialized AI agent for your task"
                )
                
                selected_agent_id = agent_options[selected_agent_name]
                st.session_state.selected_agent_id = selected_agent_id
                
                # Show agent info if agent selected
                if selected_agent_id:
                    selected_agent = next((a for a in agents if a.id == selected_agent_id), None)
                    if selected_agent:
                        with st.expander("ℹ️ Agent Info", expanded=False):
                            st.markdown(f"**{selected_agent.emoji} {selected_agent.name}**")
                            st.write(selected_agent.description)
                            st.caption(f"**Category:** {selected_agent.category.title()}")
                            st.caption(f"**Tone:** {selected_agent.tone.title()}")
                            st.caption(f"**Temperature:** {selected_agent.temperature}")
                            if selected_agent.allowed_tools:
                                st.caption(f"**Allowed Tools:** {', '.join(selected_agent.allowed_tools)}")
                            if selected_agent.usage_count:
                                st.caption(f"**Used:** {selected_agent.usage_count} times")
                            if selected_agent.rating > 0:
                                st.caption(f"**Rating:** {'⭐' * int(selected_agent.rating)}")
                
                # Button to manage agents (opens agent manager UI)
                if st.button("✏️ Manage Agents", use_container_width=True):
                    st.session_state.show_agent_manager = True
                    st.session_state.show_profile = False
                    st.session_state.show_file_manager = False
                    st.session_state.show_diagram_generator = False
                    st.session_state.show_memory_manager = False
                    st.rerun()
            
            else:
                st.info("No agents available. Initialize agents first.")
                
        except Exception as e:
            st.error(f"Error loading agents: {e}")
            st.session_state.selected_agent_id = None
        
        st.divider()
        
        st.title("⚙️ Settings")
        
        # Provider selection - Get user-specific providers based on their API keys
        available_providers = model_factory.get_user_available_providers(user_id)
        
        if not available_providers:
            st.error("❌ No LLM providers available. Please add your API keys.")
            st.info("Go to 👤 Profile → API Keys to add your OpenAI, Gemini, or Anthropic API keys")
            return {}
        
        provider = st.selectbox(
            "Provider",
            available_providers,
            format_func=lambda x: x.upper()
        )
        
        # Model selection (dynamic based on provider) - Use user-specific provider
        models = model_factory.get_models_for_provider(provider, user_id=user_id)
        model_options = {m.display_name: m.name for m in models}
        
        if not model_options:
            st.error(f"No models available for {provider.upper()}")
            st.info(f"Please ensure you have added your {provider.upper()} API key in Profile → API Keys")
            return {}
        
        # Key ensures model selection resets when provider changes
        selected_display_name = st.selectbox(
            "Model",
            list(model_options.keys()),
            key=f"model_select_{provider}"
        )
        model = model_options.get(selected_display_name, list(model_options.values())[0])
        
        # Show model info (user-specific)
        model_info = model_factory.get_model_info(provider, model, user_id=user_id)
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
        
        use_image_generator = st.checkbox(
            "Enable AI Image Generator",
            value=False,
            help="Generate images from text descriptions using DALL-E 3, Stability AI, and other AI models"
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
    
    # Get selected agent settings if agent is selected
    selected_agent_id = st.session_state.get('selected_agent_id', None)
    agent_settings = {}
    
    if selected_agent_id:
        try:
            db = get_db()
            agent_manager = get_agent_manager(db)
            agent = agent_manager.get_agent_by_id(selected_agent_id)
            db.close()
            
            if agent:
                agent_settings = {
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "agent_emoji": agent.emoji,
                    "agent_system_prompt": agent.system_prompt,
                    "agent_temperature": agent.temperature,
                    "agent_max_tokens": agent.max_tokens,
                    "agent_allowed_tools": agent.allowed_tools or []
                }
        except Exception as e:
            print(f"Error getting agent settings: {e}")
    
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system_prompt": system_prompt if system_prompt else None,
        "use_tavily": use_tavily,
        "use_web_scraper": use_web_scraper,
        "use_youtube": use_youtube,
        "use_data_analyzer": use_data_analyzer,
        "use_image_generator": use_image_generator,
        **agent_settings  # Merge agent settings
    }

