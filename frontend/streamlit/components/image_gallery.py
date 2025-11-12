"""
Image Gallery Component
Rich image viewer with zoom, download, and management features
"""
import streamlit as st
from pathlib import Path
from typing import List, Dict, Any, Optional
import base64
from datetime import datetime

from backend.core.image_handler import image_handler
from frontend.streamlit.components.ui_utils import (
    show_toast,
    render_empty_state
)


class ImageGalleryUI:
    """Image gallery interface with modern UI"""
    
    @staticmethod
    def render():
        """Main render method for image gallery"""
        if 'user_id' not in st.session_state:
            st.warning("⚠️ Please log in to access the image gallery.")
            return
        
        user_id = st.session_state.user_id
        
        # Header
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h1>🖼️ Image Gallery</h1>
            <p style='color: var(--color-text-secondary);'>
                View and manage your uploaded and generated images
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Tabs for different image sources
        tab1, tab2, tab3, tab4 = st.tabs([
            "📤 All Images",
            "📁 Uploaded",
            "🎨 Generated",
            "🔍 From Search"
        ])
        
        with tab1:
            ImageGalleryUI._render_images(user_id, source='all')
        
        with tab2:
            ImageGalleryUI._render_images(user_id, source='upload')
        
        with tab3:
            ImageGalleryUI._render_images(user_id, source='generated')
        
        with tab4:
            ImageGalleryUI._render_images(user_id, source='search')
    
    @staticmethod
    def _render_images(user_id: int, source: str = 'all'):
        """Render image grid"""
        
        # Filter and sort options
        col1, col2, col3 = st.columns([2, 2, 1])
        
        with col1:
            sort_by = st.selectbox(
                "Sort by",
                options=["Newest First", "Oldest First", "Largest", "Smallest"],
                key=f"sort_{source}"
            )
        
        with col2:
            limit = st.slider(
                "Images per page",
                min_value=10,
                max_value=100,
                value=30,
                step=10,
                key=f"limit_{source}"
            )
        
        with col3:
            if st.button("🔄 Refresh", use_container_width=True, key=f"refresh_{source}"):
                st.rerun()
        
        st.divider()
        
        # Get images
        images = image_handler.list_user_images(user_id, source=source, limit=limit)
        
        if not images:
            render_empty_state(
                icon="🖼️",
                title="No Images Found",
                description="Upload or generate images to see them here"
            )
            return
        
        # Sort images
        if sort_by == "Newest First":
            images = sorted(images, key=lambda x: x['modified_at'], reverse=True)
        elif sort_by == "Oldest First":
            images = sorted(images, key=lambda x: x['modified_at'])
        elif sort_by == "Largest":
            images = sorted(images, key=lambda x: x['size_bytes'], reverse=True)
        elif sort_by == "Smallest":
            images = sorted(images, key=lambda x: x['size_bytes'])
        
        # Display count
        st.markdown(f"**Found {len(images)} image(s)**")
        
        # Display images in grid (3 columns)
        for i in range(0, len(images), 3):
            cols = st.columns(3)
            
            for col_idx, col in enumerate(cols):
                if i + col_idx < len(images):
                    image_info = images[i + col_idx]
                    with col:
                        ImageGalleryUI._render_image_card(image_info, source)
    
    @staticmethod
    def _render_image_card(image_info: Dict[str, Any], source: str = 'all'):
        """Render a single image card"""
        
        with st.container():
            # Image container with hover effect
            st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(157, 78, 221, 0.05));
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 0.5rem;
                margin-bottom: 1rem;
                transition: all 0.3s ease;
            '>
            </div>
            """, unsafe_allow_html=True)
            
            # Display image
            try:
                st.image(image_info['file_path'], width='stretch', caption=image_info['filename'])
            except Exception as e:
                st.error(f"Failed to load image: {str(e)}")
                return
            
            # Image info
            st.caption(
                f"📐 {image_info['dimensions'][0]}×{image_info['dimensions'][1]} | "
                f"📦 {image_info['size_kb']} KB | "
                f"📅 {image_info['modified_at'][:10]}"
            )
            
            # Actions
            action_cols = st.columns([1, 1, 1])
            
            with action_cols[0]:
                # View full size
                with st.expander("👁️ View"):
                    st.image(image_info['file_path'], width='stretch')
            
            with action_cols[1]:
                # Download
                try:
                    with open(image_info['file_path'], 'rb') as f:
                        image_bytes = f.read()
                    
                    st.download_button(
                        "⬇️",
                        data=image_bytes,
                        file_name=image_info['filename'],
                        mime=f"image/{image_info['format'].lower()}",
                        use_container_width=True,
                        key=f"download_{source}_{image_info['filename']}"
                    )
                except Exception as e:
                    st.button("⬇️", disabled=True, use_container_width=True, key=f"download_disabled_{source}_{image_info['filename']}")
            
            with action_cols[2]:
                # Delete
                if st.button(
                    "🗑️",
                    key=f"delete_{source}_{image_info['filename']}",
                    use_container_width=True,
                    help="Delete image"
                ):
                    if image_handler.delete_image(image_info['file_path']):
                        show_toast("Image deleted successfully!", "success")
                        st.rerun()
                    else:
                        show_toast("Failed to delete image", "error")
    
    @staticmethod
    def render_compact_selector(user_id: int, key_prefix: str = "img_select") -> Optional[str]:
        """
        Render a compact image selector for use in other components
        
        Args:
            user_id: User ID
            key_prefix: Prefix for widget keys
            
        Returns:
            Selected image path or None
        """
        images = image_handler.list_user_images(user_id, source='all', limit=20)
        
        if not images:
            st.info("No images available. Upload or generate images first.")
            return None
        
        # Create options dict
        image_options = {
            f"{img['filename']} ({img['size_kb']} KB)": img['file_path']
            for img in images
        }
        
        selected_display = st.selectbox(
            "Select an image",
            options=["None"] + list(image_options.keys()),
            key=f"{key_prefix}_select"
        )
        
        if selected_display == "None":
            return None
        
        selected_path = image_options[selected_display]
        
        # Show preview
        st.image(selected_path, width=200, caption="Preview")
        
        return selected_path


def render_image_gallery():
    """Wrapper function to render image gallery"""
    ImageGalleryUI.render()

