"""
Main chat interface component
"""
import streamlit as st
import asyncio
from backend.core.chat_manager import ChatManager
from backend.database.operations import MessageDB

def render_chat(settings: dict):
    """
    Render the main chat interface
    
    Args:
        settings: Settings dict from sidebar
    """
    st.title("🧠 Mathanoshto AI")
    
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
    
    # Initialize chat manager if needed
    if st.session_state.chat_manager is None:
        st.session_state.chat_manager = ChatManager()
        st.session_state.current_conversation_id = st.session_state.chat_manager.conversation_id
        st.session_state.messages = []
    
    # Token counter in header
    if st.session_state.current_conversation_id:
        usage = st.session_state.chat_manager.get_token_usage()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Input Tokens", f"{usage['input_tokens']:,}")
        with col2:
            st.metric("Output Tokens", f"{usage['output_tokens']:,}")
        with col3:
            st.metric("Total Tokens", f"{usage['total_tokens']:,}")
        with col4:
            st.metric("Total Cost", f"${usage['total_cost']:.4f}")
        
        st.divider()
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        # Skip system messages
        if role == "system":
            continue
        
        with st.chat_message(role):
            st.markdown(content)
    
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
            
            with st.spinner("Thinking..."):
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
                    
                    st.markdown(response.content)
                    
                    # Show token info
                    st.caption(
                        f"🔢 {response.input_tokens} + {response.output_tokens} = "
                        f"{response.total_tokens} tokens | "
                        f"💰 ${response.cost:.6f} | "
                        f"🤖 {response.provider}/{response.model}"
                    )
                    
                    # Add assistant message to display
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response.content
                    })
                    
                    # Auto-generate title after first exchange
                    if len(st.session_state.messages) == 2:
                        asyncio.run(
                            st.session_state.chat_manager.auto_generate_title(
                                provider=settings["provider"],
                                model=settings["model"]
                            )
                        )
                    
                except Exception as e:
                    error_msg = str(e)
                    st.error(f"❌ Error: {error_msg}")
                    
                    # Show detailed error information
                    with st.expander("🔍 Error Details"):
                        st.code(error_msg, language=None)
                        
                        # Model-specific help
                        if "model" in error_msg.lower() or "not found" in error_msg.lower():
                            st.warning("""
                            **Model Not Found Error**
                            
                            This model might not be available in your OpenAI account. 
                            
                            **Note:** GPT-5 is not yet released by OpenAI.
                            
                            Try these models instead:
                            - **gpt-4o** - Latest multimodal model
                            - **gpt-4o-mini** - Fast and affordable
                            - **gpt-4-turbo** - Previous generation flagship
                            """)
                        else:
                            st.info("""
                            **Common issues:**
                            - Invalid API key in .env file
                            - Insufficient API credits
                            - Model not available in your account
                            - Network connectivity issues
                            
                            **To fix:**
                            1. Check your .env file has valid API keys
                            2. Verify you have credits on your API account
                            3. Try a different model (gpt-4o, gpt-4o-mini)
                            4. Check if the model exists in OpenAI's API
                            """)
        
        st.rerun()

