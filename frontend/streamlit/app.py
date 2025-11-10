"""
Personal LLM Assistant - Streamlit Frontend
Main application entry point
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import asyncio
import base64

# Page config
st.set_page_config(
    page_title="Mathanoshto AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
from backend.database.operations import init_database
init_database()

# Import components
from frontend.streamlit.components.sidebar import render_sidebar
from frontend.streamlit.components.chat import render_chat

# Load and encode background image
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

bg_image_path = Path(__file__).parent / "bg.jpg"
bg_image_base64 = get_base64_image(bg_image_path)

# Custom CSS with background image and funky design
bg_css = f"""
    /* Background image for main chat area */
    .main {{
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), 
                    url('data:image/jpeg;base64,{bg_image_base64}') no-repeat center center fixed;
        background-size: cover;
    }}
""" if bg_image_base64 else ""

st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
    
    /* Main app styling */
    .stApp {{
        font-family: 'Poppins', sans-serif;
    }}
    
    {bg_css}
    
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }}
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #1e1e2e 0%, #2d2d44 100%);
        border-right: 2px solid #00d4ff;
    }}
    
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    
    /* Chat messages - Funky glassmorphism style */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.1) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 20px !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37) !important;
    }}
    
    /* User message - Gradient accent */
    .stChatMessage[data-testid="user-message"] {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(157, 78, 221, 0.2)) !important;
        border-left: 4px solid #00d4ff !important;
    }}
    
    /* Assistant message - Different gradient */
    .stChatMessage[data-testid="assistant-message"] {{
        background: linear-gradient(135deg, rgba(157, 78, 221, 0.2), rgba(255, 107, 107, 0.2)) !important;
        border-left: 4px solid #9d4edd !important;
    }}
    
    /* Headers with gradient text */
    h1, h2, h3 {{
        background: linear-gradient(90deg, #00d4ff, #9d4edd, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    }}
    
    /* Metrics/Token counter - Neon style */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(157, 78, 221, 0.1));
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
    }}
    
    /* Buttons - Neon style */
    .stButton button {{
        background: linear-gradient(135deg, #00d4ff, #9d4edd) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px !important;
        padding: 0.5rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.4) !important;
        transition: all 0.3s ease !important;
    }}
    
    .stButton button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6) !important;
    }}
    
    /* Input boxes */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {{
        background: rgba(255, 255, 255, 0.1) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 15px !important;
        color: white !important;
        backdrop-filter: blur(10px) !important;
    }}
    
    /* Chat input at bottom */
    .stChatInput {{
        background: rgba(30, 30, 46, 0.9) !important;
        border: 2px solid #00d4ff !important;
        border-radius: 25px !important;
        backdrop-filter: blur(10px) !important;
    }}
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {{
        width: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(30, 30, 46, 0.5);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, #00d4ff, #9d4edd);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, #9d4edd, #ff6b6b);
    }}
    
    /* Expander styling */
    .streamlit-expanderHeader {{
        background: rgba(0, 212, 255, 0.1) !important;
        border-radius: 10px !important;
        border: 1px solid rgba(0, 212, 255, 0.3) !important;
    }}
    
    /* Success/Info/Warning messages */
    .stSuccess, .stInfo, .stWarning {{
        border-radius: 15px !important;
        backdrop-filter: blur(10px) !important;
    }}
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'chat_manager' not in st.session_state:
    st.session_state.chat_manager = None
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Render sidebar (returns settings)
settings = render_sidebar()

# Render main chat interface
render_chat(settings)

