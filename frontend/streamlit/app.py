"""
Personal LLM Assistant - Streamlit Frontend
Main application entry point
"""
import sys
from pathlib import Path

# Add project root to Python path FIRST
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st

# Page config MUST be first Streamlit command
st.set_page_config(
    page_title="Mathanoshto AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Now import other modules after path is set
import asyncio
import base64

# Initialize database
from backend.database.operations import init_database
init_database()

# Initialize Firebase (if enabled)
from backend.auth.firebase_auth import initialize_firebase
initialize_firebase()

# Import session state manager FIRST
from frontend.streamlit.utils.session_state import init_session_state, SessionStateManager

# Import components
from frontend.streamlit.components.sidebar import render_sidebar
from frontend.streamlit.components.chat import render_chat
from frontend.streamlit.components.login import require_login
from frontend.streamlit.components.profile import render_user_profile
from frontend.streamlit.components.api_keys import render_api_key_management
from frontend.streamlit.components.file_manager import render_file_manager
from frontend.streamlit.components.diagram_generator import render_diagram_generator
from frontend.streamlit.components.memory_manager import render_memory_manager
from frontend.streamlit.components.agent_manager import render_agent_manager
from frontend.streamlit.components.conversation_insights_panel import render_conversation_insights_panel
from frontend.streamlit.components.image_gallery import render_image_gallery
from frontend.streamlit.styles.custom_css import get_custom_css

# Load and encode background image
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

bg_image_path = Path(__file__).parent / "bg.jpg"
bg_image_base64 = get_base64_image(bg_image_path)

# Initialize dark mode from session state
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Initialize session state (centralized, prevents race conditions)
init_session_state()

# Apply custom CSS with selected theme
theme_name = SessionStateManager.get('theme_name', 'midnight_ocean')
st.markdown(
    get_custom_css(bg_image_base64, theme_name),
    unsafe_allow_html=True
)

# Check if user is logged in
if not require_login():
    # Login page is rendered by require_login()
    st.stop()

# Render sidebar (returns settings)
settings = render_sidebar()

# Check which page to show
if st.session_state.get('show_profile', False):
    render_user_profile()
    
    # Add close button
    if st.button("← Back to Chat", key="close_profile"):
        st.session_state.show_profile = False
        st.rerun()
elif st.session_state.get('show_api_keys', False):
    render_api_key_management()
    
    # Add close button
    if st.button("← Back to Chat", key="close_api_keys"):
        st.session_state.show_api_keys = False
        st.rerun()
elif st.session_state.get('show_file_manager', False):
    render_file_manager()
    
    # Add close button
    if st.button("← Back to Chat", key="close_file_manager"):
        st.session_state.show_file_manager = False
        st.rerun()
elif st.session_state.get('show_diagram_generator', False):
    render_diagram_generator()
    
    # Add close button
    if st.button("← Back to Chat", key="close_diagram_generator"):
        st.session_state.show_diagram_generator = False
        st.rerun()
elif st.session_state.get('show_memory_manager', False):
    render_memory_manager()
    
    # Add close button
    if st.button("← Back to Chat", key="close_memory_manager"):
        st.session_state.show_memory_manager = False
        st.rerun()
elif st.session_state.get('show_agent_manager', False):
    render_agent_manager()
    
    # Add close button
    if st.button("← Back to Chat", key="close_agent_manager"):
        st.session_state.show_agent_manager = False
        st.rerun()
elif st.session_state.get('show_insights_panel', False):
    render_conversation_insights_panel()
    
    # Add close button
    if st.button("← Back to Chat", key="close_insights_panel"):
        st.session_state.show_insights_panel = False
        st.rerun()
elif st.session_state.get('show_image_gallery', False):
    render_image_gallery()
    
    # Add close button
    if st.button("← Back to Chat", key="close_image_gallery"):
        st.session_state.show_image_gallery = False
        st.rerun()
else:
    # Render main chat interface
    render_chat(settings)

