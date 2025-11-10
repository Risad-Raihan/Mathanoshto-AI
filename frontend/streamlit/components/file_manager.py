"""
File Manager UI Component for Streamlit
"""
import streamlit as st
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import base64

from backend.core.file_manager import file_manager
from backend.core.file_rag import file_summarizer


class FileManagerUI:
    """File management interface"""
    
    @staticmethod
    def render():
        """Main render method for file manager"""
        if 'user_id' not in st.session_state:
            st.warning("Please log in to access file management.")
            return
        
        user_id = st.session_state.user_id
        
        st.title("📁 File Manager")
        
        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "📤 Upload Files",
            "📂 My Files",
            "🔍 Search Files",
            "📊 Storage Stats"
        ])
        
        with tab1:
            FileManagerUI.render_upload_section(user_id)
        
        with tab2:
            FileManagerUI.render_files_list(user_id)
        
        with tab3:
            FileManagerUI.render_search_section(user_id)
        
        with tab4:
            FileManagerUI.render_storage_stats(user_id)
    
    @staticmethod
    def render_upload_section(user_id: int):
        """Render file upload interface"""
        st.header("Upload Files")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            help="Supported: PDF, DOCX, TXT, CSV, JSON, XML, Images"
        )
        
        # Upload options
        col1, col2 = st.columns(2)
        
        with col1:
            description = st.text_area(
                "Description (optional)",
                placeholder="Describe the files you're uploading..."
            )
        
        with col2:
            folder_path = st.text_input(
                "Folder Path",
                value="/",
                help="Virtual folder path (e.g., /documents/reports)"
            )
            
            enable_text_extraction = st.checkbox(
                "Extract text content",
                value=True,
                help="Extract text for search and analysis"
            )
            
            enable_thumbnail = st.checkbox(
                "Generate thumbnails",
                value=True,
                help="Generate preview thumbnails"
            )
            
            enable_ocr = st.checkbox(
                "Enable OCR for images",
                value=False,
                help="Extract text from images (slower)"
            )
        
        # Upload button
        if uploaded_files and st.button("📤 Upload Files", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            error_count = 0
            
            for i, uploaded_file in enumerate(uploaded_files):
                status_text.text(f"Uploading {uploaded_file.name}...")
                
                try:
                    file_data = uploaded_file.read()
                    
                    result = file_manager.upload_file(
                        file_data=file_data,
                        original_filename=uploaded_file.name,
                        user_id=user_id,
                        description=description,
                        folder_path=folder_path,
                        enable_text_extraction=enable_text_extraction,
                        enable_thumbnail=enable_thumbnail,
                        enable_ocr=enable_ocr
                    )
                    
                    if result['success']:
                        success_count += 1
                    else:
                        error_count += 1
                        st.error(f"Failed to upload {uploaded_file.name}: {result.get('error', 'Unknown error')}")
                
                except Exception as e:
                    error_count += 1
                    st.error(f"Error uploading {uploaded_file.name}: {str(e)}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
            
            status_text.empty()
            progress_bar.empty()
            
            if success_count > 0:
                st.success(f"✅ Successfully uploaded {success_count} file(s)")
            if error_count > 0:
                st.error(f"❌ Failed to upload {error_count} file(s)")
            
            # Clear the file uploader
            st.rerun()
    
    @staticmethod
    def render_files_list(user_id: int):
        """Render list of user's files"""
        st.header("My Files")
        
        # Filters
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            folders = file_manager.get_folders(user_id)
            folder_filter = st.selectbox(
                "Folder",
                options=["All"] + folders,
                key="folder_filter"
            )
        
        with col2:
            type_filter = st.selectbox(
                "File Type",
                options=["All", "pdf", "docx", "txt", "csv", "json", "xml", "image", "excel"],
                key="type_filter"
            )
        
        with col3:
            sort_order = st.selectbox(
                "Sort By",
                options=["Newest", "Oldest", "Name", "Size"],
                key="sort_order"
            )
        
        # Map sort options
        sort_mapping = {
            "Newest": ("uploaded_at", "desc"),
            "Oldest": ("uploaded_at", "asc"),
            "Name": ("filename", "asc"),
            "Size": ("file_size", "desc")
        }
        sort_by, order = sort_mapping[sort_order]
        
        # Get files
        files = file_manager.list_files(
            user_id=user_id,
            folder_path=None if folder_filter == "All" else folder_filter,
            file_type=None if type_filter == "All" else type_filter,
            sort_by=sort_by,
            sort_order=order
        )
        
        if not files:
            st.info("No files found. Upload some files to get started!")
            return
        
        st.write(f"**{len(files)} file(s) found**")
        
        # Display files in a grid
        for file in files:
            FileManagerUI.render_file_card(user_id, file)
    
    @staticmethod
    def render_file_card(user_id: int, file: dict):
        """Render a single file card"""
        with st.container():
            col1, col2, col3 = st.columns([1, 4, 2])
            
            with col1:
                # Display thumbnail or icon
                if file.get('thumbnail_path'):
                    try:
                        from backend.utils.file_storage import file_storage
                        thumb_data = file_storage.read_file(file['thumbnail_path'])
                        if thumb_data:
                            st.image(thumb_data, width=80)
                        else:
                            st.write(f"📄 {file['file_type'].upper()}")
                    except:
                        st.write(f"📄 {file['file_type'].upper()}")
                else:
                    st.write(f"📄 {file['file_type'].upper()}")
            
            with col2:
                st.write(f"**{file['original_filename']}**")
                
                # File info
                size_mb = file['file_size'] / (1024 * 1024)
                uploaded = datetime.fromisoformat(file['uploaded_at']).strftime("%Y-%m-%d %H:%M")
                st.caption(f"Size: {size_mb:.2f} MB | Uploaded: {uploaded}")
                
                # Tags
                if file.get('tags'):
                    tags_str = ", ".join([f"#{tag}" for tag in file['tags']])
                    st.caption(f"Tags: {tags_str}")
                
                # Description
                if file.get('description'):
                    with st.expander("Description"):
                        st.write(file['description'])
            
            with col3:
                # Action buttons
                if st.button("⬇️ Download", key=f"download_{file['id']}"):
                    FileManagerUI.download_file(user_id, file['id'], file['original_filename'])
                
                if st.button("🔍 View", key=f"view_{file['id']}"):
                    st.session_state[f"viewing_file_{file['id']}"] = True
                    st.rerun()
                
                if st.button("✏️ Edit", key=f"edit_{file['id']}"):
                    st.session_state[f"editing_file_{file['id']}"] = True
                    st.rerun()
                
                if st.button("🗑️ Delete", key=f"delete_{file['id']}"):
                    st.session_state[f"deleting_file_{file['id']}"] = True
                    st.rerun()
            
            # Handle file viewing
            if st.session_state.get(f"viewing_file_{file['id']}", False):
                FileManagerUI.render_file_viewer(user_id, file)
                if st.button("Close", key=f"close_view_{file['id']}"):
                    st.session_state[f"viewing_file_{file['id']}"] = False
                    st.rerun()
            
            # Handle file editing
            if st.session_state.get(f"editing_file_{file['id']}", False):
                FileManagerUI.render_file_editor(user_id, file)
                if st.button("Close", key=f"close_edit_{file['id']}"):
                    st.session_state[f"editing_file_{file['id']}"] = False
                    st.rerun()
            
            # Handle file deletion
            if st.session_state.get(f"deleting_file_{file['id']}", False):
                st.warning(f"Are you sure you want to delete **{file['original_filename']}**?")
                col_a, col_b = st.columns(2)
                with col_a:
                    if st.button("Yes, Delete", key=f"confirm_delete_{file['id']}", type="primary"):
                        if file_manager.delete_file(file['id'], user_id):
                            st.success("File deleted successfully!")
                            st.session_state[f"deleting_file_{file['id']}"] = False
                            st.rerun()
                        else:
                            st.error("Failed to delete file")
                with col_b:
                    if st.button("Cancel", key=f"cancel_delete_{file['id']}"):
                        st.session_state[f"deleting_file_{file['id']}"] = False
                        st.rerun()
            
            st.divider()
    
    @staticmethod
    def render_file_viewer(user_id: int, file: dict):
        """Render file content viewer"""
        with st.expander("📄 File Content", expanded=True):
            # Get file text
            text = file_manager.get_file_text(file['id'], user_id)
            
            if text:
                st.text_area(
                    "Extracted Text",
                    value=text,
                    height=300,
                    key=f"text_view_{file['id']}"
                )
                
                # Q&A Section
                st.subheader("Ask about this file")
                question = st.text_input(
                    "Your question",
                    key=f"question_{file['id']}",
                    placeholder="What is this document about?"
                )
                
                if st.button("Get Answer", key=f"ask_{file['id']}"):
                    with st.spinner("Analyzing file..."):
                        qa_data = file_summarizer.get_qa_for_file(
                            file['id'],
                            user_id,
                            question
                        )
                        
                        if qa_data:
                            st.session_state[f"qa_prompt_{file['id']}"] = qa_data['prompt']
                            st.info("Prompt ready! Use this in your chat to get an answer.")
                            st.code(qa_data['prompt'], language=None)
                
                # Summarization
                if st.button("📝 Summarize", key=f"summarize_{file['id']}"):
                    with st.spinner("Generating summary..."):
                        summary_data = file_summarizer.get_summary_for_file(file['id'], user_id)
                        
                        if summary_data:
                            st.session_state[f"summary_prompt_{file['id']}"] = summary_data['prompt']
                            st.info("Summary prompt ready! Use this in your chat.")
                            st.code(summary_data['prompt'], language=None)
            else:
                st.info("No text content available for this file.")
    
    @staticmethod
    def render_file_editor(user_id: int, file: dict):
        """Render file metadata editor"""
        with st.expander("✏️ Edit File Details", expanded=True):
            new_description = st.text_area(
                "Description",
                value=file.get('description', ''),
                key=f"new_desc_{file['id']}"
            )
            
            new_folder = st.text_input(
                "Folder Path",
                value=file.get('folder_path', '/'),
                key=f"new_folder_{file['id']}"
            )
            
            # Tags management
            current_tags = file.get('tags', [])
            st.write("**Current Tags:**", ", ".join([f"#{t}" for t in current_tags]) if current_tags else "None")
            
            new_tags_input = st.text_input(
                "Add Tags (comma-separated)",
                key=f"new_tags_{file['id']}",
                placeholder="tag1, tag2, tag3"
            )
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("💾 Save Changes", key=f"save_edit_{file['id']}", type="primary"):
                    # Update description
                    if new_description != file.get('description', ''):
                        file_manager.update_file_description(file['id'], user_id, new_description)
                    
                    # Update folder
                    if new_folder != file.get('folder_path', '/'):
                        file_manager.move_file(file['id'], user_id, new_folder)
                    
                    # Add tags
                    if new_tags_input:
                        new_tags = [t.strip() for t in new_tags_input.split(',') if t.strip()]
                        file_manager.add_tags(file['id'], user_id, new_tags)
                    
                    st.success("Changes saved!")
                    st.session_state[f"editing_file_{file['id']}"] = False
                    st.rerun()
            
            with col_b:
                # Remove tag
                if current_tags:
                    tag_to_remove = st.selectbox(
                        "Remove Tag",
                        options=[""] + current_tags,
                        key=f"remove_tag_{file['id']}"
                    )
                    
                    if tag_to_remove and st.button("Remove Tag", key=f"do_remove_tag_{file['id']}"):
                        file_manager.remove_tags(file['id'], user_id, [tag_to_remove])
                        st.success(f"Removed tag: {tag_to_remove}")
                        st.rerun()
    
    @staticmethod
    def download_file(user_id: int, file_id: int, filename: str):
        """Handle file download"""
        result = file_manager.download_file(file_id, user_id)
        
        if result:
            file_data, original_filename, mime_type = result
            
            # Encode for download
            b64 = base64.b64encode(file_data).decode()
            href = f'<a href="data:{mime_type};base64,{b64}" download="{original_filename}">Click here to download {original_filename}</a>'
            st.markdown(href, unsafe_allow_html=True)
            st.success("File ready for download!")
        else:
            st.error("Failed to download file")
    
    @staticmethod
    def render_search_section(user_id: int):
        """Render file search interface"""
        st.header("🔍 Search Files")
        
        # Search input
        search_query = st.text_input(
            "Search files",
            placeholder="Search by filename, description, or content...",
            key="search_query"
        )
        
        # Search filters
        col1, col2 = st.columns(2)
        
        with col1:
            search_type = st.selectbox(
                "File Type",
                options=["All", "pdf", "docx", "txt", "csv", "json", "xml", "image"],
                key="search_type"
            )
        
        with col2:
            # Get all user tags
            all_tags = file_manager.get_user_tags(user_id)
            tag_options = [tag[0] for tag in all_tags]
            
            search_tags = st.multiselect(
                "Filter by Tags",
                options=tag_options,
                key="search_tags"
            )
        
        # Perform search
        if search_query:
            files = file_manager.search_files(
                user_id=user_id,
                query=search_query,
                file_type=None if search_type == "All" else search_type,
                tags=search_tags if search_tags else None
            )
            
            if files:
                st.success(f"Found {len(files)} file(s)")
                for file in files:
                    FileManagerUI.render_file_card(user_id, file)
            else:
                st.info("No files found matching your search.")
        else:
            st.info("Enter a search query to find files.")
    
    @staticmethod
    def render_storage_stats(user_id: int):
        """Render storage statistics"""
        st.header("📊 Storage Statistics")
        
        stats = file_manager.get_storage_stats(user_id)
        
        # Main stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Files", stats['file_count'])
        
        with col2:
            st.metric("Total Storage", f"{stats['total_size_mb']} MB")
        
        with col3:
            # Calculate average file size
            avg_size = stats['total_size_mb'] / stats['file_count'] if stats['file_count'] > 0 else 0
            st.metric("Avg File Size", f"{avg_size:.2f} MB")
        
        # File type breakdown
        if stats['by_type']:
            st.subheader("Files by Type")
            
            # Create a simple bar chart representation
            for file_type, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats['file_count']) * 100
                st.write(f"**{file_type.upper()}**: {count} files ({percentage:.1f}%)")
                st.progress(percentage / 100)
        
        # Tags statistics
        st.subheader("Most Used Tags")
        all_tags = file_manager.get_user_tags(user_id)
        
        if all_tags:
            for tag, count in all_tags[:10]:  # Top 10 tags
                st.write(f"**#{tag}**: {count} files")
        else:
            st.info("No tags yet. Add tags to organize your files!")


def render_file_manager():
    """Convenience function to render file manager"""
    FileManagerUI.render()

