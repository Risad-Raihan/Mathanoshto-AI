"""
Custom CSS styles for the Streamlit application
Includes color palette system, animations, and component styles
"""

def get_custom_css(bg_image_base64: str = None, dark_mode: bool = True) -> str:
    """
    Generate custom CSS with color palette system
    
    Args:
        bg_image_base64: Base64 encoded background image
        dark_mode: Whether to use dark mode colors
    
    Returns:
        str: Complete CSS string
    """
    
    # Color palette based on theme - Green & Beige
    if dark_mode:
        colors = {
            'primary': '#4a7c59',        # Forest green
            'secondary': '#6b8e23',      # Olive green
            'accent': '#8fbc8f',         # Light sea green
            'bg-dark': '#2a3426',        # Dark olive
            'bg-medium': '#3d4a36',      # Medium olive
            'bg-light': '#4f5d46',       # Light olive
            'text-primary': '#f5f5dc',   # Beige
            'text-secondary': '#d4c5a9', # Light beige
            'success': '#52b788',        # Green success
            'warning': '#e9c46a',        # Beige warning
            'error': '#e76f51',          # Coral error
            'info': '#7fa99b'            # Teal info
        }
    else:
        colors = {
            'primary': '#52b788',        # Medium green
            'secondary': '#8fbc8f',      # Light green
            'accent': '#6b8e23',         # Olive
            'bg-dark': '#faf8f3',        # Light beige
            'bg-medium': '#f5f1e8',      # Medium beige
            'bg-light': '#ede8dc',       # Dark beige
            'text-primary': '#2a3426',   # Dark olive
            'text-secondary': '#5a6352', # Medium olive
            'success': '#52b788',        # Green
            'warning': '#e9c46a',        # Beige warning
            'error': '#e76f51',          # Coral
            'info': '#7fa99b'            # Teal
        }
    
    # Background CSS
    bg_css = f"""
    /* Background image for main chat area */
    .stApp {{
        background: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.7)), 
                    url('data:image/jpeg;base64,{bg_image_base64}') no-repeat center center fixed;
        background-size: cover;
    }}
    
    .main .block-container {{
        background-color: rgba(30, 30, 46, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }}
    """ if bg_image_base64 else ""
    
    css = f"""
    <style>
    /* ============================================
       CSS VARIABLES - Color Palette System
       ============================================ */
    :root {{
        --color-primary: {colors['primary']};
        --color-secondary: {colors['secondary']};
        --color-accent: {colors['accent']};
        --color-bg-dark: {colors['bg-dark']};
        --color-bg-medium: {colors['bg-medium']};
        --color-bg-light: {colors['bg-light']};
        --color-text-primary: {colors['text-primary']};
        --color-text-secondary: {colors['text-secondary']};
        --color-success: {colors['success']};
        --color-warning: {colors['warning']};
        --color-error: {colors['error']};
        --color-info: {colors['info']};
        
        --border-radius-sm: 10px;
        --border-radius-md: 15px;
        --border-radius-lg: 20px;
        --border-radius-xl: 25px;
        
        --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.2);
        --shadow-neon: 0 0 20px rgba(0, 212, 255, 0.3);
        
        --transition-fast: 0.15s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.5s ease;
    }}
    
    /* ============================================
       FONTS
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    
    .stApp {{
        font-family: 'Poppins', sans-serif;
    }}
    
    /* ============================================
       BACKGROUND
       ============================================ */
    {bg_css}
    
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: rgba(30, 30, 46, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: var(--border-radius-lg);
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: var(--shadow-lg);
    }}
    
    /* ============================================
       SIDEBAR STYLING
       ============================================ */
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--color-bg-dark) 0%, var(--color-bg-medium) 100%);
        border-right: 2px solid var(--color-primary);
    }}
    
    [data-testid="stSidebar"] * {{
        color: var(--color-text-primary) !important;
    }}
    
    [data-testid="stSidebar"] .element-container {{
        margin-bottom: 0.75rem;
    }}
    
    [data-testid="stSidebar"] h1 {{
        font-size: 1.5rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }}
    
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }}
    
    /* Sidebar buttons - clean style */
    [data-testid="stSidebar"] .stButton button {{
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important;
        border: none !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }}
    
    [data-testid="stSidebar"] .stButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(74, 124, 89, 0.3) !important;
    }}
    
    /* ============================================
       CHAT MESSAGES - Glassmorphism
       ============================================ */
    .stChatMessage {{
        background: rgba(255, 255, 255, 0.08) !important;
        backdrop-filter: blur(15px) !important;
        -webkit-backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: var(--border-radius-lg) !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: var(--shadow-lg) !important;
        transition: transform var(--transition-normal) !important;
    }}
    
    .stChatMessage:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3) !important;
    }}
    
    /* User message - Gradient accent */
    .stChatMessage[data-testid="user-message"] {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(157, 78, 221, 0.15)) !important;
        border-left: 4px solid var(--color-primary) !important;
    }}
    
    /* Assistant message - Different gradient */
    .stChatMessage[data-testid="assistant-message"] {{
        background: linear-gradient(135deg, rgba(157, 78, 221, 0.15), rgba(255, 107, 107, 0.15)) !important;
        border-left: 4px solid var(--color-secondary) !important;
    }}
    
    /* ============================================
       CODE BLOCKS with Copy Button
       ============================================ */
    .stChatMessage code {{
        font-family: 'JetBrains Mono', monospace !important;
        background: rgba(0, 0, 0, 0.3) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 6px !important;
        padding: 0.2em 0.4em !important;
    }}
    
    .stChatMessage pre {{
        position: relative;
        background: rgba(0, 0, 0, 0.4) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 1rem !important;
        margin: 0.5rem 0 !important;
    }}
    
    .stChatMessage pre code {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
    }}
    
    /* Copy button styling */
    .copy-button {{
        position: absolute;
        top: 8px;
        right: 8px;
        background: var(--color-primary);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 4px 10px;
        font-size: 0.75rem;
        cursor: pointer;
        opacity: 0;
        transition: opacity var(--transition-fast);
    }}
    
    .stChatMessage pre:hover .copy-button {{
        opacity: 1;
    }}
    
    .copy-button:hover {{
        background: var(--color-secondary);
    }}
    
    /* ============================================
       HEADERS with Gradient Text
       ============================================ */
    h1, h2, h3 {{
        background: linear-gradient(90deg, var(--color-primary), var(--color-secondary), var(--color-accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700 !important;
        text-shadow: 0 0 30px rgba(0, 212, 255, 0.3);
    }}
    
    /* ============================================
       METRICS/TOKEN COUNTER - Animated
       ============================================ */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(157, 78, 221, 0.08));
        border: 2px solid rgba(0, 212, 255, 0.25);
        border-radius: var(--border-radius-md);
        padding: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: var(--shadow-neon);
        transition: all var(--transition-normal);
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.5);
        border-color: var(--color-primary);
    }}
    
    [data-testid="metric-container"] [data-testid="stMetricValue"] {{
        font-size: 1.5rem !important;
        font-weight: 700 !important;
        color: var(--color-primary) !important;
    }}
    
    /* Color-coded cost warnings */
    .metric-low {{
        border-color: var(--color-success) !important;
    }}
    
    .metric-medium {{
        border-color: var(--color-warning) !important;
    }}
    
    .metric-high {{
        border-color: var(--color-error) !important;
    }}
    
    /* ============================================
       BUTTONS - Neon Style
       ============================================ */
    .stButton button {{
        background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--border-radius-xl) !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-neon) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stButton button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 30px rgba(0, 212, 255, 0.6) !important;
    }}
    
    .stButton button:active {{
        transform: scale(0.98);
    }}
    
    /* Small buttons (delete, etc.) */
    .stButton.small-button button {{
        padding: 0.4rem 0.8rem !important;
        font-size: 0.85rem !important;
    }}
    
    /* Compact action buttons in chat messages */
    .stChatMessage .stButton button {{
        padding: 0.15rem 0.3rem !important;
        font-size: 0.75rem !important;
        min-width: 1.8rem !important;
        height: 1.8rem !important;
        border-radius: 6px !important;
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        opacity: 0.5 !important;
        transition: all 0.2s ease !important;
    }}
    
    .stChatMessage .stButton button:hover {{
        opacity: 1 !important;
        background: rgba(255, 255, 255, 0.1) !important;
        transform: scale(1.1) !important;
        box-shadow: none !important;
    }}
    
    /* Danger button */
    .stButton.danger-button button {{
        background: linear-gradient(135deg, var(--color-error), #c03546) !important;
    }}
    
    /* Success button */
    .stButton.success-button button {{
        background: linear-gradient(135deg, var(--color-success), #05b488) !important;
    }}
    
    /* ============================================
       INPUT BOXES
       ============================================ */
    .stTextInput input, .stTextArea textarea, .stSelectbox select, .stNumberInput input {{
        background: rgba(255, 255, 255, 0.08) !important;
        border: 2px solid rgba(0, 212, 255, 0.25) !important;
        border-radius: var(--border-radius-md) !important;
        color: var(--color-text-primary) !important;
        backdrop-filter: blur(10px) !important;
        transition: all var(--transition-fast) !important;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {{
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 20px rgba(0, 212, 255, 0.3) !important;
    }}
    
    /* ============================================
       CHAT INPUT at Bottom
       ============================================ */
    .stChatInput {{
        background: rgba(30, 30, 46, 0.95) !important;
        border: 2px solid var(--color-primary) !important;
        border-radius: var(--border-radius-xl) !important;
        backdrop-filter: blur(10px) !important;
        padding: 0.5rem !important;
    }}
    
    .stChatInput input {{
        background: transparent !important;
        border: none !important;
        color: var(--color-text-primary) !important;
    }}
    
    /* ============================================
       SCROLLBAR Styling
       ============================================ */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: rgba(30, 30, 46, 0.5);
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, var(--color-primary), var(--color-secondary));
        border-radius: 10px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, var(--color-secondary), var(--color-accent));
    }}
    
    /* ============================================
       EXPANDER Styling
       ============================================ */
    .streamlit-expanderHeader {{
        background: rgba(0, 212, 255, 0.08) !important;
        border-radius: var(--border-radius-md) !important;
        border: 1px solid rgba(0, 212, 255, 0.25) !important;
        transition: all var(--transition-fast) !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: rgba(0, 212, 255, 0.12) !important;
        border-color: var(--color-primary) !important;
    }}
    
    /* ============================================
       TOAST NOTIFICATIONS
       ============================================ */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: var(--border-radius-md) !important;
        backdrop-filter: blur(10px) !important;
        border-left: 4px solid !important;
        padding: 1rem !important;
        animation: slideIn var(--transition-normal) ease-out;
    }}
    
    .stSuccess {{
        background: rgba(6, 214, 160, 0.1) !important;
        border-left-color: var(--color-success) !important;
    }}
    
    .stInfo {{
        background: rgba(17, 138, 178, 0.1) !important;
        border-left-color: var(--color-info) !important;
    }}
    
    .stWarning {{
        background: rgba(255, 209, 102, 0.1) !important;
        border-left-color: var(--color-warning) !important;
    }}
    
    .stError {{
        background: rgba(239, 71, 111, 0.1) !important;
        border-left-color: var(--color-error) !important;
    }}
    
    /* ============================================
       LOADING SKELETONS
       ============================================ */
    .skeleton {{
        background: linear-gradient(
            90deg,
            rgba(255, 255, 255, 0.05) 0%,
            rgba(255, 255, 255, 0.1) 50%,
            rgba(255, 255, 255, 0.05) 100%
        );
        background-size: 200% 100%;
        animation: shimmer 1.5s infinite;
        border-radius: var(--border-radius-md);
    }}
    
    @keyframes shimmer {{
        0% {{ background-position: -200% 0; }}
        100% {{ background-position: 200% 0; }}
    }}
    
    .skeleton-text {{
        height: 1rem;
        margin: 0.5rem 0;
    }}
    
    .skeleton-card {{
        height: 120px;
        margin: 1rem 0;
    }}
    
    /* ============================================
       CONVERSATION CARDS
       ============================================ */
    .conversation-card {{
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.05), rgba(157, 78, 221, 0.05));
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: var(--border-radius-md);
        padding: 1rem;
        margin: 0.75rem 0;
        cursor: pointer;
        transition: all var(--transition-normal);
        position: relative;
        overflow: hidden;
    }}
    
    .conversation-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(180deg, var(--color-primary), var(--color-secondary));
        transform: scaleY(0);
        transition: transform var(--transition-normal);
    }}
    
    .conversation-card:hover {{
        transform: translateX(5px);
        border-color: var(--color-primary);
        box-shadow: var(--shadow-neon);
    }}
    
    .conversation-card:hover::before {{
        transform: scaleY(1);
    }}
    
    .conversation-card-title {{
        font-weight: 600;
        font-size: 1rem;
        color: var(--color-text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .conversation-card-meta {{
        font-size: 0.75rem;
        color: var(--color-text-secondary);
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;
    }}
    
    .conversation-card-meta span {{
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
    }}
    
    /* ============================================
       EMPTY STATES
       ============================================ */
    .empty-state {{
        text-align: center;
        padding: 3rem 1rem;
        color: var(--color-text-secondary);
    }}
    
    .empty-state-icon {{
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.3;
    }}
    
    .empty-state-title {{
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--color-text-primary);
        margin-bottom: 0.5rem;
    }}
    
    .empty-state-description {{
        font-size: 1rem;
        color: var(--color-text-secondary);
    }}
    
    /* ============================================
       ANIMATIONS
       ============================================ */
    @keyframes slideIn {{
        from {{
            transform: translateX(100%);
            opacity: 0;
        }}
        to {{
            transform: translateX(0);
            opacity: 1;
        }}
    }}
    
    @keyframes fadeIn {{
        from {{ opacity: 0; }}
        to {{ opacity: 1; }}
    }}
    
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}
    
    @keyframes spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    
    /* Thinking indicator */
    .thinking-indicator {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(0, 212, 255, 0.1);
        border: 1px solid rgba(0, 212, 255, 0.3);
        border-radius: var(--border-radius-lg);
        animation: pulse 2s infinite;
    }}
    
    .thinking-spinner {{
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-top-color: var(--color-primary);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }}
    
    /* ============================================
       RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {{
        .main .block-container {{
            margin: 0.5rem;
            padding: 1rem;
        }}
        
        h1 {{
            font-size: 1.5rem !important;
        }}
        
        h2 {{
            font-size: 1.25rem !important;
        }}
        
        .stChatMessage {{
            padding: 1rem !important;
        }}
    }}
    
    /* ============================================
       UTILITY CLASSES
       ============================================ */
    .text-center {{ text-align: center; }}
    .text-right {{ text-align: right; }}
    .mt-1 {{ margin-top: 0.5rem; }}
    .mt-2 {{ margin-top: 1rem; }}
    .mb-1 {{ margin-bottom: 0.5rem; }}
    .mb-2 {{ margin-bottom: 1rem; }}
    .p-1 {{ padding: 0.5rem; }}
    .p-2 {{ padding: 1rem; }}
    
    .fade-in {{
        animation: fadeIn var(--transition-normal);
    }}
    
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    </style>
    """
    
    return css

