"""
Professional header/navbar component
"""
import streamlit as st


def render_header():
    """
    Render a professional header/navbar with branding and quick actions
    """
    # Create header layout
    col1, col2, col3 = st.columns([6, 3, 1])
    
    with col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 1rem;">
            <h1 style="margin: 0; padding: 0;">🧠 Mathanoshto AI</h1>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Your Personal AI Assistant with Advanced Tools")
    
    with col2:
        # Quick stats or info
        if st.session_state.get('current_conversation_id'):
            msg_count = len(st.session_state.get('messages', []))
            st.metric("Messages", msg_count, delta=None, label_visibility="visible")
    
    with col3:
        # Action buttons
        if st.button("❓", key="header_help", help="Help & Shortcuts"):
            st.session_state.show_help = not st.session_state.get("show_help", False)
    
    # Help dialog
    if st.session_state.get("show_help", False):
        with st.expander("❓ Help & Keyboard Shortcuts", expanded=True):
            st.markdown("""
            ### Keyboard Shortcuts
            
            | Shortcut | Action |
            |----------|--------|
            | `Ctrl+Enter` | Send message |
            | `Ctrl+K` | Search messages |
            | `Ctrl+N` | New conversation |
            | `Esc` | Close dialog |
            
            ### Features
            
            - **🔍 Search**: Use the search box to find messages in long conversations
            - **📋 Copy**: Click copy buttons on messages and code blocks
            - **🔧 Tools**: Enable web search in the sidebar for real-time information
            - **💰 Cost Tracking**: Monitor token usage and costs in real-time
            - **🌙 Dark Mode**: Toggle between light and dark themes
            - **🗑️ Delete**: Conversations can be deleted with confirmation
            
            ### Tips
            
            - Start each conversation with a clear goal
            - Use system prompts for specialized behavior
            - Adjust temperature for creativity vs. precision
            - Enable web search for current information
            """)
            
            if st.button("Close Help", use_container_width=True):
                st.session_state.show_help = False
                st.rerun()
    
    st.divider()


def render_footer():
    """
    Render a footer with additional information
    """
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("© 2025 Mathanoshto AI")
    
    with col2:
        st.caption("Built with Streamlit & OpenAI")
    
    with col3:
        st.caption("[Documentation](#) • [GitHub](#) • [Support](#)")

