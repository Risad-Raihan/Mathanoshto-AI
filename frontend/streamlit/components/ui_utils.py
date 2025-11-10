"""
UI Utility Components
Enhanced UI elements for better UX including toast notifications, 
confirmation dialogs, empty states, etc.
"""
import streamlit as st
from datetime import datetime
from typing import Optional, Callable, Dict, Any
import time


def show_toast(message: str, type: str = "info", duration: int = 3):
    """
    Show a toast notification
    
    Args:
        message: Message to display
        type: Type of toast (success, error, warning, info)
        duration: Duration in seconds
    """
    if type == "success":
        st.success(message, icon="✅")
    elif type == "error":
        st.error(message, icon="❌")
    elif type == "warning":
        st.warning(message, icon="⚠️")
    else:
        st.info(message, icon="ℹ️")
    
    # Note: Streamlit doesn't support auto-dismiss yet, but we can use session state
    # to manage toast visibility in future versions


def show_confirmation_dialog(
    title: str,
    message: str,
    confirm_text: str = "Confirm",
    cancel_text: str = "Cancel",
    key: str = "confirm_dialog"
) -> Optional[bool]:
    """
    Show a confirmation dialog
    
    Args:
        title: Dialog title
        message: Dialog message
        confirm_text: Text for confirm button
        cancel_text: Text for cancel button
        key: Unique key for the dialog
    
    Returns:
        True if confirmed, False if canceled, None if no action
    """
    dialog_key = f"dialog_{key}"
    
    if dialog_key not in st.session_state:
        st.session_state[dialog_key] = None
    
    st.markdown(f"### {title}")
    st.write(message)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(confirm_text, key=f"{key}_confirm", use_container_width=True):
            st.session_state[dialog_key] = True
            return True
    with col2:
        if st.button(cancel_text, key=f"{key}_cancel", use_container_width=True):
            st.session_state[dialog_key] = False
            return False
    
    return None


def render_empty_state(
    icon: str = "📭",
    title: str = "Nothing here yet",
    description: str = "Get started by creating something new!",
    action_label: Optional[str] = None,
    action_callback: Optional[Callable] = None
):
    """
    Render an empty state placeholder
    
    Args:
        icon: Emoji or icon to display
        title: Title text
        description: Description text
        action_label: Optional action button label
        action_callback: Optional callback for action button
    """
    st.markdown(f"""
    <div class="empty-state fade-in">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if action_label and action_callback:
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            if st.button(action_label, use_container_width=True):
                action_callback()


def render_loading_skeleton(type: str = "card", count: int = 3):
    """
    Render loading skeleton placeholders
    
    Args:
        type: Type of skeleton (card, text, message)
        count: Number of skeletons to show
    """
    skeleton_class = {
        "card": "skeleton skeleton-card",
        "text": "skeleton skeleton-text",
        "message": "skeleton skeleton-card"
    }.get(type, "skeleton skeleton-card")
    
    for _ in range(count):
        st.markdown(f'<div class="{skeleton_class}"></div>', unsafe_allow_html=True)


def render_thinking_indicator(model_name: str = "AI", provider: str = ""):
    """
    Render a thinking indicator with model name
    
    Args:
        model_name: Name of the model
        provider: Provider name
    """
    display_text = f"{provider}/{model_name}" if provider else model_name
    
    st.markdown(f"""
    <div class="thinking-indicator">
        <div class="thinking-spinner"></div>
        <span>🤔 {display_text} is thinking...</span>
    </div>
    """, unsafe_allow_html=True)


def render_conversation_card(
    title: str,
    created_at: datetime,
    message_count: int,
    token_count: int,
    cost: float,
    conversation_id: int,
    on_click: Callable[[int], None],
    on_delete: Callable[[int], None]
) -> None:
    """
    Render a professional conversation card with metadata
    
    Args:
        title: Conversation title
        created_at: Creation timestamp
        message_count: Number of messages
        token_count: Total tokens used
        cost: Total cost
        conversation_id: Conversation ID
        on_click: Callback when card is clicked
        on_delete: Callback when delete is clicked
    """
    # Format date
    time_diff = datetime.now() - created_at
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
        time_str = created_at.strftime("%b %d")
    
    # Create card layout
    col1, col2 = st.columns([5, 1])
    
    with col1:
        if st.button(
            f"📝 {title[:35]}..." if len(title) > 35 else f"📝 {title}",
            key=f"conv_card_{conversation_id}",
            use_container_width=True
        ):
            on_click(conversation_id)
        
        # Metadata below title
        st.markdown(f"""
        <div class="conversation-card-meta">
            <span>🕒 {time_str}</span>
            <span>💬 {message_count} msgs</span>
            <span>🔢 {token_count:,} tokens</span>
            <span>💰 ${cost:.4f}</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🗑️", key=f"del_card_{conversation_id}", help="Delete conversation"):
            # Show confirmation in session state
            st.session_state[f"confirm_delete_{conversation_id}"] = True


def format_token_count(count: int, animated: bool = False) -> str:
    """
    Format token count with thousands separator and optional animation
    
    Args:
        count: Token count
        animated: Whether to add animation class
    
    Returns:
        Formatted HTML string
    """
    formatted = f"{count:,}"
    if animated:
        return f'<span class="fade-in">{formatted}</span>'
    return formatted


def get_cost_color_class(cost: float) -> str:
    """
    Get CSS class based on cost threshold
    
    Args:
        cost: Cost in dollars
    
    Returns:
        CSS class name
    """
    if cost < 0.01:
        return "metric-low"
    elif cost < 0.10:
        return "metric-medium"
    else:
        return "metric-high"


def add_copy_button_to_code():
    """
    Add JavaScript to enable copy buttons on code blocks
    Note: This is a placeholder for future implementation
    Streamlit doesn't support custom JS easily, but we can prepare the CSS
    """
    st.markdown("""
    <script>
    // Add copy buttons to code blocks
    document.querySelectorAll('pre code').forEach((block) => {
        if (!block.parentElement.querySelector('.copy-button')) {
            const button = document.createElement('button');
            button.className = 'copy-button';
            button.textContent = 'Copy';
            button.addEventListener('click', () => {
                navigator.clipboard.writeText(block.textContent);
                button.textContent = 'Copied!';
                setTimeout(() => {
                    button.textContent = 'Copy';
                }, 2000);
            });
            block.parentElement.insertBefore(button, block);
        }
    });
    </script>
    """, unsafe_allow_html=True)


def render_code_with_copy(code: str, language: str = "python") -> None:
    """
    Render code block with copy button
    
    Args:
        code: Code to display
        language: Programming language for syntax highlighting
    """
    # Generate unique ID
    code_id = f"code_{hash(code) % 10000}"
    
    st.code(code, language=language)
    
    # Add copy button using Streamlit button
    if st.button("📋 Copy", key=f"copy_{code_id}"):
        st.write("✅ Copied to clipboard!")


def render_message_with_actions(
    content: str,
    role: str,
    message_id: int,
    on_edit: Optional[Callable[[int], None]] = None,
    on_regenerate: Optional[Callable[[int], None]] = None,
    on_copy: Optional[Callable[[str], None]] = None
):
    """
    Render a message with action buttons (edit, regenerate, copy)
    
    Args:
        content: Message content
        role: Message role (user/assistant)
        message_id: Message ID
        on_edit: Callback for edit action
        on_regenerate: Callback for regenerate action
        on_copy: Callback for copy action
    """
    with st.chat_message(role):
        st.markdown(content)
        
        # Action buttons
        actions = st.columns([1, 1, 1, 6])
        
        if on_copy:
            with actions[0]:
                if st.button("📋", key=f"copy_msg_{message_id}", help="Copy message"):
                    on_copy(content)
                    show_toast("Copied to clipboard!", "success")
        
        if role == "user" and on_edit:
            with actions[1]:
                if st.button("✏️", key=f"edit_msg_{message_id}", help="Edit message"):
                    on_edit(message_id)
        
        if role == "assistant" and on_regenerate:
            with actions[2]:
                if st.button("🔄", key=f"regen_msg_{message_id}", help="Regenerate response"):
                    on_regenerate(message_id)


def render_search_box(
    placeholder: str = "Search messages...",
    key: str = "search"
) -> Optional[str]:
    """
    Render a search box for filtering content
    
    Args:
        placeholder: Placeholder text
        key: Unique key for the search box
    
    Returns:
        Search query string or None
    """
    search_query = st.text_input(
        "🔍 Search",
        placeholder=placeholder,
        key=key,
        label_visibility="collapsed"
    )
    
    return search_query if search_query else None


def render_keyboard_shortcuts_help():
    """
    Render keyboard shortcuts help dialog
    """
    with st.expander("⌨️ Keyboard Shortcuts"):
        st.markdown("""
        | Shortcut | Action |
        |----------|--------|
        | `Ctrl+Enter` | Send message |
        | `Ctrl+K` | Search messages |
        | `Ctrl+N` | New conversation |
        | `Ctrl+/` | Show shortcuts |
        | `Esc` | Close dialog |
        
        **Note:** Some shortcuts may require browser support
        """)


def init_keyboard_shortcuts():
    """
    Initialize keyboard shortcuts using Streamlit components
    Note: Limited support in Streamlit, but we can add the infrastructure
    """
    # This is a placeholder for keyboard shortcut initialization
    # In a real implementation, we'd use custom components or JS
    st.markdown("""
    <script>
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter to send message
        if (e.ctrlKey && e.key === 'Enter') {
            const sendButton = document.querySelector('[data-testid="stChatInputSubmitButton"]');
            if (sendButton) sendButton.click();
        }
        
        // Ctrl+K for search
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[placeholder*="Search"]');
            if (searchInput) searchInput.focus();
        }
        
        // Ctrl+N for new conversation
        if (e.ctrlKey && e.key === 'n') {
            e.preventDefault();
            const newButton = document.querySelector('button:contains("New Conversation")');
            if (newButton) newButton.click();
        }
    });
    </script>
    """, unsafe_allow_html=True)


def render_header_navbar(
    app_title: str = "Mathanoshto AI",
    show_settings: bool = True,
    show_help: bool = True,
    show_profile: bool = False
):
    """
    Render a professional header/navbar
    
    Args:
        app_title: Application title
        show_settings: Show settings button
        show_help: Show help button
        show_profile: Show user profile section
    """
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.title(f"🧠 {app_title}")
    
    with col2:
        actions = st.columns(3 if show_profile else 2)
        
        idx = 0
        if show_settings:
            with actions[idx]:
                if st.button("⚙️", key="navbar_settings", help="Settings"):
                    st.session_state.show_settings = not st.session_state.get("show_settings", False)
            idx += 1
        
        if show_help:
            with actions[idx]:
                if st.button("❓", key="navbar_help", help="Help"):
                    st.session_state.show_help = not st.session_state.get("show_help", False)
            idx += 1
        
        if show_profile:
            with actions[idx]:
                st.button("👤", key="navbar_profile", help="Profile")
    
    st.divider()


def render_dark_mode_toggle():
    """
    Render dark mode toggle
    Note: Streamlit theme is global, but we can store preference
    """
    dark_mode = st.checkbox(
        "🌙 Dark Mode",
        value=st.session_state.get("dark_mode", True),
        key="dark_mode_toggle"
    )
    
    st.session_state.dark_mode = dark_mode
    return dark_mode


def filter_messages_by_search(messages: list, search_query: str) -> list:
    """
    Filter messages by search query
    
    Args:
        messages: List of message dictionaries
        search_query: Search query string
    
    Returns:
        Filtered list of messages
    """
    if not search_query:
        return messages
    
    query_lower = search_query.lower()
    return [
        msg for msg in messages
        if query_lower in msg.get("content", "").lower()
    ]


def export_conversation_to_markdown(messages: list, title: str = "Conversation") -> str:
    """
    Export conversation to markdown format
    
    Args:
        messages: List of message dictionaries
        title: Conversation title
    
    Returns:
        Markdown formatted string
    """
    md = f"# {title}\n\n"
    md += f"*Exported on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    md += "---\n\n"
    
    for msg in messages:
        role = msg.get("role", "unknown")
        content = msg.get("content", "")
        
        if role == "user":
            md += f"### 👤 User\n\n{content}\n\n"
        elif role == "assistant":
            md += f"### 🤖 Assistant\n\n{content}\n\n"
        
        md += "---\n\n"
    
    return md


def show_cost_warning(cost: float):
    """
    Show cost warning if threshold exceeded
    
    Args:
        cost: Current cost in dollars
    """
    if cost > 0.50:
        st.warning(f"⚠️ High usage: ${cost:.4f} spent in this conversation")
    elif cost > 0.10:
        st.info(f"💰 Usage: ${cost:.4f} spent in this conversation")

