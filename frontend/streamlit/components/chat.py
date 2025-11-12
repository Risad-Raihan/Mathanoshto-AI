"""
Main chat interface component
"""
import streamlit as st
import asyncio
from backend.core.chat_manager import ChatManager
from backend.database.operations import MessageDB
from backend.core.file_manager import file_manager
from backend.core.file_rag import FileRAG
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
from pathlib import Path


def display_message_with_images(content: str):
    """Display message content and extract/show any embedded images"""
    if not content:
        return
    
    # Pattern to match image paths in various formats:
    # - ![alt text](path/to/image.png)  [MARKDOWN]
    # - sandbox:/path/to/image.png
    # - uploads/visualizations/image.png
    # - [text](sandbox:/path/to/image.png)
    # - Direct paths to images
    
    image_patterns = [
        # Markdown image syntax: ![alt](path)
        r'!\[([^\]]*)\]\(([^\)]+\.(?:png|jpg|jpeg|gif|webp|bmp))\)',
        # sandbox: prefix
        r'sandbox:/([\w/\-_.]+\.(?:png|jpg|jpeg|gif|webp|bmp))',
        # Markdown links with sandbox
        r'\[([^\]]+)\]\(sandbox:/([\w/\-_.]+\.(?:png|jpg|jpeg|gif|webp|bmp))\)',
        # Markdown links with direct path
        r'\[([^\]]+)\]\((uploads/[\w/\-_.]+\.(?:png|jpg|jpeg|gif|webp|bmp))\)',
        # Direct paths
        r'(?:^|\s)(uploads/[\w/\-_.]+\.(?:png|jpg|jpeg|gif|webp|bmp))(?:\s|$)',
    ]
    
    # Find all image paths in content
    found_images = []
    for pattern_idx, pattern in enumerate(image_patterns):
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            # Extract image path based on pattern
            if pattern_idx == 0:  # Markdown image: ![alt](path)
                img_path = match.group(2)
                alt_text = match.group(1)
            elif pattern_idx == 1:  # sandbox:/path
                img_path = match.group(1)
                alt_text = None
            elif pattern_idx == 2:  # [text](sandbox:/path)
                img_path = match.group(2)
                alt_text = match.group(1)
            elif pattern_idx == 3:  # [text](uploads/path)
                img_path = match.group(2)
                alt_text = match.group(1)
            else:  # Direct path
                img_path = match.group(1)
                alt_text = None
            
            img_path = img_path.strip()
            
            # Clean up the path
            if img_path.startswith('sandbox:/'):
                img_path = img_path[9:]  # Remove 'sandbox:/'
            
            # Convert to absolute path if relative
            if not Path(img_path).is_absolute():
                # Get project root (four levels up from frontend/streamlit/components/)
                # chat.py is at: frontend/streamlit/components/chat.py
                project_root = Path(__file__).parent.parent.parent.parent
                full_path = (project_root / img_path).resolve()
            else:
                full_path = Path(img_path)
            
            # Check if file exists
            if full_path.exists():
                found_images.append((str(full_path), match.span(), alt_text))
    
    # Remove duplicates while preserving order
    unique_images = []
    seen = set()
    for img, span, alt in found_images:
        if img not in seen:
            unique_images.append((img, span, alt))
            seen.add(img)
    
    # Display the text content (with image markdown removed for clarity)
    display_content = content
    
    # Remove markdown image syntax
    display_content = re.sub(r'!\[([^\]]*)\]\(([^\)]+\.(?:png|jpg|jpeg|gif|webp|bmp))\)', '', display_content)
    # Remove sandbox: links from display
    display_content = re.sub(r'\[([^\]]+)\]\(sandbox:/[^\)]+\)', r'\1', display_content)
    # Remove direct upload path links
    display_content = re.sub(r'\[([^\]]+)\]\((uploads/[^\)]+\.(?:png|jpg|jpeg|gif|webp|bmp))\)', r'\1', display_content)
    
    # Display the text
    st.markdown(display_content)
    
    # Display all found images
    if unique_images:
        st.divider()
        for img_path, _, alt_text in unique_images:
            # Check if file exists before trying to display
            if Path(img_path).exists():
                st.image(img_path, width='stretch')
                caption = alt_text if alt_text else Path(img_path).name
                st.caption(f"🖼️ {caption}")
            else:
                st.warning(f"⚠️ Image file not found: {Path(img_path).name}")


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
    
    # Initialize attached files state
    if 'attached_files' not in st.session_state:
        st.session_state.attached_files = []
    
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
        
        # Export buttons
        export_col1, export_col2, export_col3 = st.columns([4, 1, 1])
        with export_col1:
            st.markdown("")  # Spacer
        with export_col2:
            if st.button("📥 Export as JSON", use_container_width=True, key="export_json_btn"):
                _export_conversation_json(st.session_state.current_conversation_id, st.session_state.user_id)
        with export_col3:
            if st.button("📄 Export as MD", use_container_width=True, key="export_md_btn"):
                _export_conversation_markdown(st.session_state.current_conversation_id, st.session_state.user_id)
        
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
                
                # Check if there are images anywhere in the content
                has_images = bool(re.search(r'sandbox:/[\w/\-_.]+\.(?:png|jpg|jpeg|gif|webp)', content, re.IGNORECASE))
                
                for i, part in enumerate(parts):
                    if i % 3 == 0 and part:  # Regular text
                        st.markdown(part)
                    elif i % 3 == 2 and part:  # Code block
                        language = parts[i-1] if parts[i-1] else "python"
                        st.code(part, language=language)
                        # Add copy button for code
                        if st.button("📋 Copy", key=f"copy_code_{idx}_{i}"):
                            st.toast("✅ Copied to clipboard!", icon="✅")
                
                # Display images if any
                if has_images and role == "assistant":
                    image_pattern = r'sandbox:/([\w/\-_.]+\.(?:png|jpg|jpeg|gif|webp))'
                    images = re.findall(image_pattern, content, re.IGNORECASE)
                    if images:
                        st.divider()
                        for img_path in images:
                            if Path(img_path).exists():
                                st.image(img_path, width='stretch')
                                st.caption(f"📊 {Path(img_path).name}")
            else:
                # Use image display function for assistant messages
                if role == "assistant":
                    display_message_with_images(content)
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
            tools = get_enabled_tools(
                use_tavily=settings.get("use_tavily", False),
                use_web_scraper=settings.get("use_web_scraper", False),
                use_youtube=settings.get("use_youtube", False),
                use_data_analyzer=settings.get("use_data_analyzer", False),
                use_image_generator=settings.get("use_image_generator", False)
            )
            
            if tools:
                enabled_tools = []
                if settings.get("use_tavily"):
                    enabled_tools.append("Web Search")
                if settings.get("use_web_scraper"):
                    enabled_tools.append("Web Scraper")
                if settings.get("use_youtube"):
                    enabled_tools.append("YouTube")
                if settings.get("use_data_analyzer"):
                    enabled_tools.append("Data Analyzer")
                if settings.get("use_image_generator"):
                    enabled_tools.append("Image Generator")
                st.caption(f"🔧 Tools enabled: {', '.join(enabled_tools)}")
            
            thinking_placeholder = st.empty()
            with thinking_placeholder:
                render_thinking_indicator(
                    model_name=settings["model"], 
                    provider=settings["provider"]
                )
            
            try:
                # Use agent settings if agent selected, otherwise use manual settings
                agent_id = settings.get("agent_id")
                if agent_id:
                    system_prompt = settings.get("agent_system_prompt", "")
                    temperature = settings.get("agent_temperature", 0.7)
                    max_tokens = settings.get("agent_max_tokens", 2000)
                else:
                    system_prompt = settings.get("system_prompt")
                    temperature = settings.get("temperature", 0.7)
                    max_tokens = settings.get("max_tokens", 2000)
                
                response = asyncio.run(
                    st.session_state.chat_manager.send_message(
                        user_message=prompt,
                        provider=settings["provider"],
                        model=settings["model"],
                        temperature=temperature,
                        max_tokens=max_tokens,
                        system_prompt=system_prompt,
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
    
    # File and Image attachment section (before chat input)
    st.divider()
    
    # Initialize attached images state
    if 'attached_images' not in st.session_state:
        st.session_state.attached_images = []
    
    # Show helpful tip if user has files but nothing attached
    user_files = file_manager.list_files(user_id, limit=100)
    
    if user_files and not st.session_state.attached_files and not st.session_state.attached_images:
        st.info("💡 **Tip:** Attach files or images below to have the AI analyze them in your conversation!")
    
    # Image upload section
    st.markdown("### 🖼️ Image Attachments")
    
    img_col1, img_col2, img_col3 = st.columns([2, 2, 1])
    
    with img_col1:
        # Multiple image upload
        uploaded_images = st.file_uploader(
            "Upload images",
            type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp'],
            accept_multiple_files=True,
            key="image_uploader",
            help="Upload one or more images for the AI to analyze"
        )
        
        if uploaded_images:
            from backend.core.image_handler import image_handler
            for uploaded_file in uploaded_images:
                # Check if already attached
                if uploaded_file.name not in [img.get('original_filename') for img in st.session_state.attached_images]:
                    # Save uploaded image
                    file_data = uploaded_file.read()
                    result = image_handler.save_uploaded_image(
                        file_data,
                        uploaded_file.name,
                        user_id,
                        metadata={'source': 'upload', 'conversation_id': st.session_state.current_conversation_id}
                    )
                    
                    if result['success']:
                        st.session_state.attached_images.append(result)
                        show_toast(f"✅ Image attached: {uploaded_file.name}", "success")
                    else:
                        st.error(f"❌ Failed to attach {uploaded_file.name}: {result['error']}")
    
    with img_col2:
        # Clipboard paste option (instructions)
        st.markdown("""
        **📋 Paste from Clipboard:**
        
        Use Ctrl+V (Cmd+V on Mac) in the chat input below to paste images directly!
        """)
    
    with img_col3:
        if st.button("🗑️ Clear Images", help="Remove all attached images", use_container_width=True):
            st.session_state.attached_images = []
            show_toast("Cleared image attachments", "info")
            st.rerun()
    
    # Display attached images
    if st.session_state.attached_images:
        st.success(f"🖼️ **AI will analyze {len(st.session_state.attached_images)} image(s) in your next message**")
        
        # Show image previews
        img_preview_cols = st.columns(min(len(st.session_state.attached_images), 4))
        for idx, img_info in enumerate(st.session_state.attached_images):
            with img_preview_cols[idx % 4]:
                st.image(img_info['file_path'], caption=img_info.get('original_filename', img_info['filename']), width=150)
                size_mb = img_info['size_bytes'] / (1024 * 1024)
                st.caption(f"{img_info['dimensions'][0]}×{img_info['dimensions'][1]} | {size_mb:.2f} MB")
                if st.button("✖", key=f"remove_img_{idx}", help="Remove"):
                    st.session_state.attached_images.pop(idx)
                    st.rerun()
    
    st.divider()
    
    # File selector for mentions
    col_file1, col_file2 = st.columns([3, 1])
    
    with col_file1:        
        if user_files:
            file_options = {f"{f['original_filename']} ({f['file_type']})": f['id'] for f in user_files}
            
            selected_file_display = st.selectbox(
                "📎 Select a file to attach",
                options=["None"] + list(file_options.keys()),
                key="file_selector",
                help="The AI will automatically read the file content and use it to answer your questions."
            )
            
            if selected_file_display != "None" and selected_file_display:
                selected_file_id = file_options[selected_file_display]
                
                # Add file to attached list if not already there
                if selected_file_id not in [f['id'] for f in st.session_state.attached_files]:
                    # Get full file info
                    file_info = file_manager.get_file(selected_file_id, user_id)
                    if file_info:
                        st.session_state.attached_files.append(file_info)
                        show_toast(f"✅ Attached: {file_info['original_filename']}", "success")
                        st.rerun()
    
    with col_file2:
        if st.button("🗑️ Clear All", help="Remove all attached files", use_container_width=True):
            st.session_state.attached_files = []
            show_toast("Cleared all attachments", "info")
            st.rerun()
    
    # Display currently attached files
    if st.session_state.attached_files:
        st.success(f"🤖 **AI will read {len(st.session_state.attached_files)} file(s) in your next message**")
        
        for idx, file in enumerate(st.session_state.attached_files):
            col_a, col_b, col_c = st.columns([0.5, 8, 1.5])
            
            with col_a:
                # File type icon
                icon_map = {
                    'pdf': '📄', 'docx': '📝', 'txt': '📃',
                    'csv': '📊', 'json': '🔤', 'xml': '📋',
                    'image': '🖼️', 'excel': '📈'
                }
                st.write(icon_map.get(file['file_type'], '📄'))
            
            with col_b:
                size_mb = file['file_size'] / (1024 * 1024)
                st.write(f"**{file['original_filename']}**")
                
                if file.get('has_text'):
                    st.caption(f"✅ {size_mb:.2f} MB • Text content available")
                else:
                    st.caption(f"⚠️ {size_mb:.2f} MB • No text content")
            
            with col_c:
                if st.button("✖", key=f"remove_file_{idx}", help="Remove", use_container_width=True):
                    st.session_state.attached_files.pop(idx)
                    st.rerun()
        
        st.divider()
    
    # Chat input
    if prompt := st.chat_input("What can I help you with?"):
        # Prepare the message with file and image context if attached
        final_prompt = prompt
        attached_file_names = []
        attached_image_data = []
        
        # Process attached images for vision models
        if st.session_state.attached_images:
            from backend.core.image_handler import image_handler as img_handler
            
            for img_info in st.session_state.attached_images:
                # Get base64 encoded image
                base64_data = img_handler.get_image_base64(img_info['file_path'])
                if base64_data:
                    attached_image_data.append({
                        'type': 'image',
                        'data': base64_data,
                        'filename': img_info.get('original_filename', img_info['filename']),
                        'format': img_info['format'],
                        'dimensions': img_info['dimensions']
                    })
        
        if st.session_state.attached_files:
            # Build file context
            file_context_parts = ["\n\n--- ATTACHED FILES CONTEXT ---\n"]
            
            for file in st.session_state.attached_files:
                attached_file_names.append(file['original_filename'])
                
                # Get file content (will try to extract on-demand if not already extracted)
                file_content = FileRAG.get_file_context(file['id'], user_id, max_chars=15000)
                
                # If no content and it's a PDF, try to extract now
                if not file_content and file['file_type'] in ['pdf', 'docx', 'txt', 'csv', 'json', 'xml']:
                    from backend.utils.file_storage import file_storage
                    from backend.utils.file_parser import file_parser
                    from backend.database.file_operations import FileDB
                    
                    # Get file record
                    file_record = FileDB.get_file(file['id'])
                    if file_record:
                        full_path = file_storage.get_file_path(file_record.file_path)
                        
                        # Try to extract text now
                        parse_result = file_parser.parse_file(full_path, file['file_type'], enable_ocr=False)
                        
                        if parse_result['success'] and parse_result.get('text'):
                            file_content = parse_result['text']
                            
                            # Save extracted text to database for future use
                            FileDB.update_file(file['id'], extracted_text=file_content)
                            
                            # Truncate if needed
                            if len(file_content) > 15000:
                                file_content = file_content[:15000] + "...\n[Content truncated]"
                
                if file_content:
                    file_context_parts.append(f"\n📎 **File: {file['original_filename']}** (Type: {file['file_type']})\n")
                    file_context_parts.append(f"File path for analysis: {file['file_path']}\n")
                    file_context_parts.append(f"```\n{file_content}\n```\n")
                else:
                    file_context_parts.append(f"\n📎 **File: {file['original_filename']}** (Type: {file['file_type']})\n")
                    file_context_parts.append(f"File path for analysis: {file['file_path']}\n")
                    file_context_parts.append(f"(Unable to extract text content preview, but file is available for analysis tools)\n")
            
            file_context_parts.append("\n--- END OF FILES ---\n\n")
            file_context_parts.append("📌 IMPORTANT: When using data analysis tools (analyze_dataset, create_visualization), use the 'File path for analysis' provided above as the file_path parameter.\n\n")
            file_context_parts.append(f"User's question about the above file(s): {prompt}")
            
            final_prompt = "".join(file_context_parts)
            
            # Attach files to conversation in database
            for file in st.session_state.attached_files:
                file_manager.attach_to_conversation(
                    file['id'], 
                    st.session_state.current_conversation_id,
                    user_id,
                    context_type='reference'
                )
        
        # Add user message to display (show original prompt + file + image indicators)
        display_content = prompt
        if attached_file_names:
            display_content += f"\n\n📎 **Attached files:** {', '.join(attached_file_names)}"
        if attached_image_data:
            image_names = [img['filename'] for img in attached_image_data]
            display_content += f"\n\n🖼️ **Attached images:** {', '.join(image_names)}"
        
        st.session_state.messages.append({"role": "user", "content": display_content})
        
        with st.chat_message("user"):
            st.markdown(display_content)
        
        # Get AI response
        with st.chat_message("assistant"):
            # Get enabled tools
            from backend.tools.tavily_search import get_enabled_tools
            tools = get_enabled_tools(
                use_tavily=settings.get("use_tavily", False),
                use_web_scraper=settings.get("use_web_scraper", False),
                use_youtube=settings.get("use_youtube", False),
                use_data_analyzer=settings.get("use_data_analyzer", False),
                use_image_generator=settings.get("use_image_generator", False)
            )
            
            # Show if tools are enabled
            if tools:
                enabled_tools = []
                if settings.get("use_tavily"):
                    enabled_tools.append("Web Search")
                if settings.get("use_web_scraper"):
                    enabled_tools.append("Web Scraper")
                if settings.get("use_youtube"):
                    enabled_tools.append("YouTube")
                if settings.get("use_data_analyzer"):
                    enabled_tools.append("Data Analyzer")
                if settings.get("use_image_generator"):
                    enabled_tools.append("Image Generator")
                st.caption(f"🔧 Tools enabled: {', '.join(enabled_tools)}")
            
            # Show thinking indicator with model name
            thinking_placeholder = st.empty()
            with thinking_placeholder:
                render_thinking_indicator(
                    model_name=settings["model"], 
                    provider=settings["provider"]
                )
            
            try:
                # 🤖 Check if agent is selected and apply agent settings
                agent_id = settings.get("agent_id")
                agent_name = settings.get("agent_name")
                
                # Use agent settings if agent selected, otherwise use manual settings
                if agent_id:
                    # Agent mode - use agent's system prompt and settings
                    enhanced_system_prompt = settings.get("agent_system_prompt", "")
                    temperature = settings.get("agent_temperature", 0.7)
                    max_tokens = settings.get("agent_max_tokens", 2000)
                    allowed_tools = settings.get("agent_allowed_tools", [])
                    
                    # Filter tools based on agent permissions
                    if allowed_tools:
                        # Map tool names to boolean flags
                        tool_mapping = {
                            "web_search": "use_tavily",
                            "tavily_search": "use_tavily",
                            "web_scraper": "use_web_scraper",
                            "youtube": "use_youtube",
                            "youtube_summarizer": "use_youtube",
                            "data_analyzer": "use_data_analyzer"
                        }
                        
                        # Only enable tools that the agent is allowed to use
                        for tool, setting_key in tool_mapping.items():
                            if tool not in allowed_tools:
                                settings[setting_key] = False
                        
                        # Rebuild tools with agent permissions
                        from backend.tools.tavily_search import get_enabled_tools
                        tools = get_enabled_tools(
                            use_tavily=settings.get("use_tavily", False),
                            use_web_scraper=settings.get("use_web_scraper", False),
                            use_youtube=settings.get("use_youtube", False),
                            use_data_analyzer=settings.get("use_data_analyzer", False),
                            use_image_generator=settings.get("use_image_generator", False)
                        )
                    
                    # Show agent indicator
                    agent_emoji = settings.get("agent_emoji", "🤖")
                    st.caption(f"{agent_emoji} **Agent: {agent_name}**")
                    
                    # Start agent session for tracking
                    try:
                        from backend.database.operations import get_db
                        from backend.core.agent_manager import get_agent_manager
                        
                        db = get_db()
                        agent_manager = get_agent_manager(db)
                        
                        # Start session if not already started for this conversation
                        if not st.session_state.get('agent_session_id'):
                            session = agent_manager.start_agent_session(
                                agent_id=agent_id,
                                conversation_id=st.session_state.current_conversation_id,
                                user_id=user_id
                            )
                            if session:
                                st.session_state.agent_session_id = session.id
                        
                        db.close()
                    except Exception as agent_error:
                        print(f"Agent session error: {agent_error}")
                
                else:
                    # Manual mode - use user-defined settings
                    enhanced_system_prompt = settings.get("system_prompt") or ""
                    temperature = settings.get("temperature", 0.7)
                    max_tokens = settings.get("max_tokens", 2000)
                
                # 🧠 Retrieve relevant memories for context
                try:
                    from backend.database.operations import get_db
                    from backend.core.memory_manager import get_memory_manager
                    
                    db = get_db()
                    memory_manager = get_memory_manager(db)
                    
                    # Search for relevant memories based on user query
                    relevant_memories = memory_manager.search_memories(
                        user_id=user_id,
                        query=prompt,  # Use original user message for search
                        limit=5,
                        min_similarity=0.0  # Lower threshold to catch more memories
                    )
                    
                    # Inject memories into system prompt
                    if relevant_memories and len(relevant_memories) > 0:
                        memory_context = "\n\n## 🧠 RELEVANT MEMORIES (Use this context to personalize your responses):\n"
                        for memory, similarity in relevant_memories:
                            memory_context += f"- [{memory.memory_type}] {memory.content} (similarity: {similarity:.2f})\n"
                        
                        enhanced_system_prompt = (enhanced_system_prompt or "") + memory_context
                        st.caption(f"🧠 Using {len(relevant_memories)} memories from long-term context")
                    
                    db.close()
                except Exception as mem_error:
                    # Silently fail if memory system has issues
                    print(f"Memory retrieval error: {mem_error}")
                    import traceback
                    traceback.print_exc()
                
                # Run async function (use final_prompt which includes file context)
                # Pass images if attached
                extra_kwargs = {}
                if attached_image_data:
                    extra_kwargs['images'] = attached_image_data
                
                response = asyncio.run(
                    st.session_state.chat_manager.send_message(
                        user_message=final_prompt,  # Use final_prompt with file context
                        provider=settings["provider"],
                        model=settings["model"],
                        temperature=temperature,  # Use agent or manual temperature
                        max_tokens=max_tokens,  # Use agent or manual max_tokens
                        system_prompt=enhanced_system_prompt,  # Use agent or manual system prompt with memories
                        tools=tools if tools else None,
                        stream=False,
                        **extra_kwargs
                    )
                )
                
                # Clear thinking indicator
                thinking_placeholder.empty()
                
                # Check if response is empty
                if not response.content or not response.content.strip():
                    st.error("⚠️ No response received from the model. The tool executed but the model didn't generate a response.")
                    st.info("This might be a model issue. Try asking again or use a different model.")
                else:
                    # Display response content with image support
                    display_message_with_images(response.content)
                
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
                
                # Clear attached files and images after successful response
                if st.session_state.attached_files:
                    st.session_state.attached_files = []
                if st.session_state.attached_images:
                    st.session_state.attached_images = []
                
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


def _export_conversation_json(conversation_id: int, user_id: int):
    """Export conversation as JSON and trigger download"""
    try:
        from backend.core.conversation_exporter import export_conversation
        from backend.database.operations import ConversationDB
        from pathlib import Path
        import json
        
        with st.spinner("Exporting as JSON..."):
            # Get conversation
            conversation = ConversationDB.get_conversation(conversation_id)
            
            # Export
            filepath = export_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                export_format='json',
                include_summary=True,
                privacy_mode=False
            )
            
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                json_content = f.read()
            
            # Create download button
            filename = f"{conversation.title.replace(' ', '_')}.json"
            
            st.download_button(
                label="⬇️ Download JSON",
                data=json_content,
                file_name=filename,
                mime='application/json',
                use_container_width=True
            )
            
            st.success(f"✅ Exported successfully!")
            
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")


def _export_conversation_markdown(conversation_id: int, user_id: int):
    """Export conversation as Markdown and trigger download"""
    try:
        from backend.core.conversation_exporter import export_conversation
        from backend.database.operations import ConversationDB
        from pathlib import Path
        
        with st.spinner("Exporting as Markdown..."):
            # Get conversation
            conversation = ConversationDB.get_conversation(conversation_id)
            
            # Export
            filepath = export_conversation(
                conversation_id=conversation_id,
                user_id=user_id,
                export_format='markdown',
                include_summary=True,
                privacy_mode=False
            )
            
            # Read file
            with open(filepath, 'r', encoding='utf-8') as f:
                md_content = f.read()
            
            # Create download button
            filename = f"{conversation.title.replace(' ', '_')}.md"
            
            st.download_button(
                label="⬇️ Download Markdown",
                data=md_content,
                file_name=filename,
                mime='text/markdown',
                use_container_width=True
            )
            
            st.success(f"✅ Exported successfully!")
            
    except Exception as e:
        st.error(f"❌ Export failed: {str(e)}")

