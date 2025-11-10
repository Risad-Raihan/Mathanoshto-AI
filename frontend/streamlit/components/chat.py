"""
Main chat interface component
"""
import streamlit as st
import asyncio
from backend.core.chat_manager import ChatManager
from backend.database.operations import MessageDB
from frontend.streamlit.components.ui_utils import (
    render_thinking_indicator,
    render_empty_state,
    show_toast,
    get_cost_color_class,
    render_search_box,
    filter_messages_by_search,
    init_keyboard_shortcuts,
    render_code_with_copy,
    show_cost_warning
)
from frontend.streamlit.components.header import render_header
import re

def render_chat(settings: dict):
    """
    Render the main chat interface
    
    Args:
        settings: Settings dict from sidebar
    """
    # Initialize keyboard shortcuts
    init_keyboard_shortcuts()
    
    # Render professional header
    render_header()
    
    # Check if settings are valid
    if not settings:
        st.warning("⚠️ Please configure your API keys in the .env file to use the assistant.")
        st.info("""
        **Steps to configure:**
        1. Edit the `.env` file in your project root
        2. Add your API keys:
           - `OPENAI_API_KEY=your_key_here`
           - `GEMINI_API_KEY=your_key_here`
        3. Restart the application
        """)
        return
    
    # Get user_id from session
    user_id = st.session_state.get('user_id')
    
    # Initialize chat manager if needed
    if st.session_state.chat_manager is None:
        st.session_state.chat_manager = ChatManager(user_id=user_id)
        st.session_state.current_conversation_id = st.session_state.chat_manager.conversation_id
        st.session_state.messages = []
    
    # Initialize edit and regeneration state
    if 'editing_message' not in st.session_state:
        st.session_state.editing_message = None
    if 'regenerating_message' not in st.session_state:
        st.session_state.regenerating_message = None
    
    # Token counter in header with color coding
    if st.session_state.current_conversation_id:
        usage = st.session_state.chat_manager.get_token_usage()
        cost_class = get_cost_color_class(usage['total_cost'])
        
        # Display cost warning if needed
        show_cost_warning(usage['total_cost'])
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Input Tokens", f"{usage['input_tokens']:,}", delta=None)
        with col2:
            st.metric("Output Tokens", f"{usage['output_tokens']:,}", delta=None)
        with col3:
            st.metric("Total Tokens", f"{usage['total_tokens']:,}", delta=None)
        with col4:
            # Add custom class for cost metric
            cost_label = "💰 Total Cost" if usage['total_cost'] < 0.10 else "⚠️ Total Cost"
            st.metric(cost_label, f"${usage['total_cost']:.4f}", delta=None)
        
        st.divider()
    
    # Search box for messages
    if len(st.session_state.messages) > 5:
        search_query = render_search_box(placeholder="Search messages...", key="msg_search")
        if search_query:
            st.caption(f"🔍 Filtering messages with: '{search_query}'")
    else:
        search_query = None
    
    # Filter messages if search query exists
    messages_to_display = filter_messages_by_search(
        st.session_state.messages, 
        search_query
    ) if search_query else st.session_state.messages
    
    # Show empty state if no messages
    if not messages_to_display:
        if search_query:
            render_empty_state(
                icon="🔍",
                title="No matching messages",
                description=f"No messages found matching '{search_query}'"
            )
        else:
            render_empty_state(
                icon="💬",
                title="Start a conversation",
                description="Type a message below to get started!"
            )
    
    # Display chat messages
    for idx, message in enumerate(messages_to_display):
        role = message["role"]
        content = message["content"]
        
        # Skip system messages
        if role == "system":
            continue
        
        with st.chat_message(role):
            # Check for code blocks and add copy buttons
            code_blocks = re.findall(r'```(\w+)?\n(.*?)```', content, re.DOTALL)
            
            if code_blocks:
                # Split content by code blocks
                parts = re.split(r'```(\w+)?\n(.*?)```', content, flags=re.DOTALL)
                
                for i, part in enumerate(parts):
                    if i % 3 == 0 and part:  # Regular text
                        st.markdown(part)
                    elif i % 3 == 2 and part:  # Code block
                        language = parts[i-1] if parts[i-1] else "python"
                        st.code(part, language=language)
                        # Add copy button for code
                        if st.button("📋 Copy", key=f"copy_code_{idx}_{i}"):
                            st.toast("✅ Copied to clipboard!", icon="✅")
            else:
                st.markdown(content)
            
            # Message actions - inline small icons
            actions_html = f"""
            <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; opacity: 0.6;">
                <span style="cursor: pointer; font-size: 0.85rem;" title="Copy">📋</span>
                {'<span style="cursor: pointer; font-size: 0.85rem;" title="Edit">✏️</span>' if role == "user" else '<span style="cursor: pointer; font-size: 0.85rem;" title="Regenerate">🔄</span>'}
            </div>
            """
            
            # Use streamlit buttons but make them minimal
            col1, col2, col_spacer = st.columns([0.08, 0.08, 9.84])
            with col1:
                if st.button("📋", key=f"copy_{idx}", help="Copy", use_container_width=True):
                    st.toast("✅ Copied!", icon="✅")
            with col2:
                if role == "user":
                    if st.button("✏️", key=f"edit_{idx}", help="Edit", use_container_width=True):
                        st.session_state.editing_message = idx
                        st.rerun()
                else:
                    if st.button("🔄", key=f"regen_{idx}", help="Regenerate", use_container_width=True):
                        st.session_state.regenerating_message = idx
                        st.rerun()
            
            # Show metadata for assistant messages
            if role == "assistant" and "model" in message:
                st.caption(f"🤖 {message.get('provider', '')}/{message.get('model', '')}")
    
    # Handle message editing
    if st.session_state.editing_message is not None:
        st.divider()
        st.subheader("✏️ Edit Message")
        
        edit_idx = st.session_state.editing_message
        if edit_idx < len(st.session_state.messages):
            original_msg = st.session_state.messages[edit_idx]
            
            edited_content = st.text_area(
                "Edit your message:",
                value=original_msg["content"],
                key="edit_text_area",
                height=150
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Save Changes", use_container_width=True):
                    # Update the message
                    st.session_state.messages[edit_idx]["content"] = edited_content
                    
                    # Remove all messages after this one (they'll need to be regenerated)
                    st.session_state.messages = st.session_state.messages[:edit_idx + 1]
                    
                    st.session_state.editing_message = None
                    show_toast("Message updated! Send a new message to continue.", "success")
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", use_container_width=True):
                    st.session_state.editing_message = None
                    st.rerun()
        
        st.divider()
    
    # Handle message regeneration
    if st.session_state.regenerating_message is not None:
        regen_idx = st.session_state.regenerating_message
        st.session_state.regenerating_message = None  # Reset immediately
        
        # Get the user message before this assistant message
        if regen_idx > 0 and regen_idx < len(st.session_state.messages):
            # Remove the assistant message and everything after it
            st.session_state.messages = st.session_state.messages[:regen_idx]
            
            # Get the last user message
            user_messages = [m for m in st.session_state.messages if m["role"] == "user"]
            if user_messages:
                last_user_msg = user_messages[-1]["content"]
                
                # Trigger regeneration by setting a flag
                st.session_state.regenerate_prompt = last_user_msg
                st.rerun()
    
    # Check if we need to regenerate
    if st.session_state.get("regenerate_prompt"):
        prompt = st.session_state.regenerate_prompt
        st.session_state.regenerate_prompt = None
        
        # Get AI response (same as normal chat flow)
        with st.chat_message("assistant"):
            from backend.tools.tavily_search import get_enabled_tools
            tools = get_enabled_tools(use_tavily=settings.get("use_tavily", False))
            
            if tools:
                st.caption("🔧 Tools enabled: Web Search")
            
            thinking_placeholder = st.empty()
            with thinking_placeholder:
                render_thinking_indicator(
                    model_name=settings["model"], 
                    provider=settings["provider"]
                )
            
            try:
                response = asyncio.run(
                    st.session_state.chat_manager.send_message(
                        user_message=prompt,
                        provider=settings["provider"],
                        model=settings["model"],
                        temperature=settings["temperature"],
                        max_tokens=settings["max_tokens"],
                        system_prompt=settings.get("system_prompt"),
                        tools=tools if tools else None,
                        stream=False
                    )
                )
                
                thinking_placeholder.empty()
                st.markdown(response.content)
                
                cost_emoji = "💰" if response.cost < 0.01 else "⚠️" if response.cost < 0.10 else "🚨"
                st.caption(
                    f"🔢 {response.input_tokens} + {response.output_tokens} = "
                    f"{response.total_tokens} tokens | "
                    f"{cost_emoji} ${response.cost:.6f} | "
                    f"🤖 {response.provider}/{response.model}"
                )
                
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.content,
                    "model": response.model,
                    "provider": response.provider,
                    "tokens": response.total_tokens,
                    "cost": response.cost
                })
                
                show_toast("Response regenerated!", "success")
                
            except Exception as e:
                thinking_placeholder.empty()
                st.error(f"❌ Error during regeneration: {str(e)[:100]}")
        
        st.rerun()
    
    # Chat input
    if prompt := st.chat_input("What can I help you with?"):
        # Add user message to display
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            # Get enabled tools
            from backend.tools.tavily_search import get_enabled_tools
            tools = get_enabled_tools(use_tavily=settings.get("use_tavily", False))
            
            # Show if tools are enabled
            if tools:
                st.caption("🔧 Tools enabled: Web Search")
            
            # Show thinking indicator with model name
            thinking_placeholder = st.empty()
            with thinking_placeholder:
                render_thinking_indicator(
                    model_name=settings["model"], 
                    provider=settings["provider"]
                )
            
            try:
                # Run async function
                response = asyncio.run(
                    st.session_state.chat_manager.send_message(
                        user_message=prompt,
                        provider=settings["provider"],
                        model=settings["model"],
                        temperature=settings["temperature"],
                        max_tokens=settings["max_tokens"],
                        system_prompt=settings.get("system_prompt"),
                        tools=tools if tools else None,
                        stream=False
                    )
                )
                
                # Clear thinking indicator
                thinking_placeholder.empty()
                
                st.markdown(response.content)
                
                # Show token info with colored cost
                cost_emoji = "💰" if response.cost < 0.01 else "⚠️" if response.cost < 0.10 else "🚨"
                st.caption(
                    f"🔢 {response.input_tokens} + {response.output_tokens} = "
                    f"{response.total_tokens} tokens | "
                    f"{cost_emoji} ${response.cost:.6f} | "
                    f"🤖 {response.provider}/{response.model}"
                )
                
                # Add assistant message to display with metadata
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response.content,
                    "model": response.model,
                    "provider": response.provider,
                    "tokens": response.total_tokens,
                    "cost": response.cost
                })
                
                # Auto-generate title after first exchange
                if len(st.session_state.messages) == 2:
                    asyncio.run(
                        st.session_state.chat_manager.auto_generate_title(
                            provider=settings["provider"],
                            model=settings["model"]
                        )
                    )
                
                # Show success toast
                show_toast("Response generated successfully!", "success")
                
            except Exception as e:
                # Clear thinking indicator
                thinking_placeholder.empty()
                
                error_msg = str(e)
                
                # User-friendly error messages
                if "model" in error_msg.lower() and "not found" in error_msg.lower():
                    st.error("❌ Model Not Available")
                    st.warning(f"""
                    **The model '{settings['model']}' is not available in your account.**
                    
                    **Quick fixes:**
                    - ✅ Try **gpt-4o** or **gpt-4o-mini** (most compatible)
                    - ✅ Check if model exists at [OpenAI Models](https://platform.openai.com/docs/models)
                    - ✅ Verify your API key has access to this model
                    
                    **Note:** Some models require special access or are not yet released.
                    """)
                elif "api" in error_msg.lower() and "key" in error_msg.lower():
                    st.error("❌ API Key Error")
                    st.warning("""
                    **Your API key appears to be invalid or missing.**
                    
                    **To fix:**
                    1. Open your `.env` file in the project root
                    2. Add or update: `OPENAI_API_KEY=your-key-here`
                    3. Get your key from [OpenAI API Keys](https://platform.openai.com/api-keys)
                    4. Restart the application
                    """)
                elif "rate" in error_msg.lower() or "limit" in error_msg.lower():
                    st.error("❌ Rate Limit Exceeded")
                    st.info("""
                    **You've hit the API rate limit.**
                    
                    **Solutions:**
                    - ⏱️ Wait a few moments and try again
                    - 💳 Upgrade your API plan for higher limits
                    - 🔄 Try a different model (e.g., gpt-4o-mini)
                    """)
                elif "quota" in error_msg.lower() or "credit" in error_msg.lower():
                    st.error("❌ Insufficient Credits")
                    st.warning("""
                    **Your API account has insufficient credits.**
                    
                    **To fix:**
                    1. Visit [OpenAI Billing](https://platform.openai.com/account/billing)
                    2. Add credits to your account
                    3. Check your usage limits
                    """)
                else:
                    st.error(f"❌ An error occurred: {error_msg[:100]}")
                
                # Show detailed error in expander
                with st.expander("🔍 Technical Details"):
                    st.code(error_msg, language=None)
                    st.caption("If this error persists, please check the application logs.")
        
        st.rerun()

