"""
Sidebar component with settings and controls
"""
import streamlit as st
from backend.core.model_factory import model_factory
from backend.database.operations import ConversationDB

def render_sidebar() -> dict:
    """
    Render sidebar with settings
    
    Returns:
        dict: Current settings (provider, model, temperature, etc.)
    """
    with st.sidebar:
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
            help="Allow assistant to search the web"
        )
        
        st.divider()
        
        # Conversation management
        st.subheader("💬 Conversations")
        
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.chat_manager = None
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        # List recent conversations
        conversations = ConversationDB.list_conversations(limit=10)
        
        if conversations:
            st.write("**Recent:**")
            for conv in conversations:
                col1, col2 = st.columns([4, 1])
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
                        st.session_state.chat_manager = ChatManager(conversation_id=conv.id)
                        st.session_state.current_conversation_id = conv.id
                        st.session_state.messages = st.session_state.chat_manager.get_conversation_history()
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv.id}"):
                        ConversationDB.delete_conversation(conv.id)
                        st.rerun()
    
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system_prompt": system_prompt if system_prompt else None,
        "use_tavily": use_tavily
    }

