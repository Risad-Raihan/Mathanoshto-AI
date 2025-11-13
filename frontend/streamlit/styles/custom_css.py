"""
Custom CSS styles for the Streamlit application
Multi-theme system with Google Font Outfit and glass morphism
"""

def get_theme_colors(theme_name: str) -> dict:
    """
    Get color palette for a specific theme
    
    Themes:
    - midnight_ocean: Blue GitHub-inspired (default)
    - mint_dream: Fresh mint green
    - warm_latte: Cozy tan/brown
    - electric_lime: Vibrant neon yellow
    - ruby_nights: Bold ruby red
    - forest_zen: Calm sage green
    - shadow_void: Pure dark charcoal
    - daylight: Clean light theme
    """
    
    themes = {
        'midnight_ocean': {
            'name': 'Midnight Ocean',
            'primary': '#58a6ff',
            'secondary': '#1f6feb',
            'accent': '#79c0ff',
            'bg-dark': '#0d1117',
            'bg-medium': '#161b22',
            'bg-light': '#21262d',
            'text-primary': '#f0f6fc',
            'text-secondary': '#8b949e',
            'success': '#3fb950',
            'warning': '#d29922',
            'error': '#f85149',
            'info': '#58a6ff',
            'border': '#30363d',
            'glass-bg': 'rgba(13, 17, 23, 0.85)',
            'glass-border': 'rgba(88, 166, 255, 0.2)',
            'gradient-start': '#1f6feb',
            'gradient-end': '#58a6ff',
            'neon-glow': 'rgba(88, 166, 255, 0.5)'
        },
        'mint_dream': {
            'name': 'Mint Dream',
            'primary': '#c8f4c8',
            'secondary': '#7ed97e',
            'accent': '#e8ffe8',
            'bg-dark': '#0a1f0a',
            'bg-medium': '#152815',
            'bg-light': '#1f361f',
            'text-primary': '#f0fff0',
            'text-secondary': '#8fb98f',
            'success': '#4ade80',
            'warning': '#fbbf24',
            'error': '#ef4444',
            'info': '#7ed97e',
            'border': '#2d4a2d',
            'glass-bg': 'rgba(10, 31, 10, 0.85)',
            'glass-border': 'rgba(200, 244, 200, 0.2)',
            'gradient-start': '#7ed97e',
            'gradient-end': '#c8f4c8',
            'neon-glow': 'rgba(200, 244, 200, 0.5)'
        },
        'warm_latte': {
            'name': 'Warm Latte',
            'primary': '#bd9a82',
            'secondary': '#8b6f5c',
            'accent': '#e0c9b5',
            'bg-dark': '#1a1410',
            'bg-medium': '#2a1f18',
            'bg-light': '#3d2e23',
            'text-primary': '#fef7f0',
            'text-secondary': '#b5a090',
            'success': '#86c06c',
            'warning': '#f4a460',
            'error': '#d9534f',
            'info': '#bd9a82',
            'border': '#4a3a2e',
            'glass-bg': 'rgba(26, 20, 16, 0.85)',
            'glass-border': 'rgba(189, 154, 130, 0.2)',
            'gradient-start': '#8b6f5c',
            'gradient-end': '#bd9a82',
            'neon-glow': 'rgba(189, 154, 130, 0.5)'
        },
        'electric_lime': {
            'name': 'Electric Lime',
            'primary': '#eaff7b',
            'secondary': '#d4e65a',
            'accent': '#f8ffb8',
            'bg-dark': '#1a1c0a',
            'bg-medium': '#252810',
            'bg-light': '#353a18',
            'text-primary': '#fffef5',
            'text-secondary': '#b8ba90',
            'success': '#84cc16',
            'warning': '#fb923c',
            'error': '#ef4444',
            'info': '#d4e65a',
            'border': '#4a4d2a',
            'glass-bg': 'rgba(26, 28, 10, 0.85)',
            'glass-border': 'rgba(234, 255, 123, 0.25)',
            'gradient-start': '#d4e65a',
            'gradient-end': '#eaff7b',
            'neon-glow': 'rgba(234, 255, 123, 0.6)'
        },
        'ruby_nights': {
            'name': 'Ruby Nights',
            'primary': '#d84242',
            'secondary': '#a83232',
            'accent': '#ff6b6b',
            'bg-dark': '#1a0a0a',
            'bg-medium': '#2a1515',
            'bg-light': '#3d2020',
            'text-primary': '#fff5f5',
            'text-secondary': '#ba8f8f',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ff4444',
            'info': '#d84242',
            'border': '#4a2a2a',
            'glass-bg': 'rgba(26, 10, 10, 0.85)',
            'glass-border': 'rgba(216, 66, 66, 0.25)',
            'gradient-start': '#a83232',
            'gradient-end': '#d84242',
            'neon-glow': 'rgba(216, 66, 66, 0.5)'
        },
        'forest_zen': {
            'name': 'Forest Zen',
            'primary': '#bed6c5',
            'secondary': '#8fb99e',
            'accent': '#dceee3',
            'bg-dark': '#0f1a13',
            'bg-medium': '#18281d',
            'bg-light': '#233628',
            'text-primary': '#f0faf4',
            'text-secondary': '#9bb5a5',
            'success': '#22c55e',
            'warning': '#fb923c',
            'error': '#ef4444',
            'info': '#8fb99e',
            'border': '#344a3a',
            'glass-bg': 'rgba(15, 26, 19, 0.85)',
            'glass-border': 'rgba(190, 214, 197, 0.2)',
            'gradient-start': '#8fb99e',
            'gradient-end': '#bed6c5',
            'neon-glow': 'rgba(190, 214, 197, 0.5)'
        },
        'shadow_void': {
            'name': 'Shadow Void',
            'primary': '#7a7a7a',
            'secondary': '#5a5a5a',
            'accent': '#9a9a9a',
            'bg-dark': '#0a0a0a',
            'bg-medium': '#1a1a1a',
            'bg-light': '#313131',
            'text-primary': '#f5f5f5',
            'text-secondary': '#9a9a9a',
            'success': '#10b981',
            'warning': '#f59e0b',
            'error': '#ef4444',
            'info': '#7a7a7a',
            'border': '#3a3a3a',
            'glass-bg': 'rgba(10, 10, 10, 0.85)',
            'glass-border': 'rgba(122, 122, 122, 0.2)',
            'gradient-start': '#5a5a5a',
            'gradient-end': '#7a7a7a',
            'neon-glow': 'rgba(122, 122, 122, 0.5)'
        },
        'daylight': {
            'name': 'Daylight',
            'primary': '#0969da',
            'secondary': '#0550ae',
            'accent': '#218bff',
            'bg-dark': '#ffffff',
            'bg-medium': '#f6f8fa',
            'bg-light': '#eaeef2',
            'text-primary': '#1f2328',
            'text-secondary': '#656d76',
            'success': '#1a7f37',
            'warning': '#bf8700',
            'error': '#d1242f',
            'info': '#0969da',
            'border': '#d0d7de',
            'glass-bg': 'rgba(255, 255, 255, 0.85)',
            'glass-border': 'rgba(9, 105, 218, 0.2)',
            'gradient-start': '#0550ae',
            'gradient-end': '#0969da',
            'neon-glow': 'rgba(9, 105, 218, 0.3)'
        }
    }
    
    return themes.get(theme_name, themes['midnight_ocean'])


def get_custom_css(bg_image_base64: str = None, theme_name: str = 'midnight_ocean') -> str:
    """
    Generate custom CSS with selected theme
    
    Args:
        bg_image_base64: Base64 encoded background image
        theme_name: Theme identifier (default: 'midnight_ocean')
    
    Returns:
        str: Complete CSS string
    """
    
    colors = get_theme_colors(theme_name)
    is_light = theme_name == 'daylight'
    
    # Background CSS - Glass Morphism
    if bg_image_base64:
        if is_light:
            bg_css = f"""
    /* Background image for main chat area */
    .stApp {{
        background: linear-gradient(rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.92)), 
                    url('data:image/jpeg;base64,{bg_image_base64}') no-repeat center center fixed;
        background-size: cover;
    }}
    
    .main .block-container {{
        background: var(--glass-bg);
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border: 1px solid var(--glass-border);
    }}
    """
        else:
    bg_css = f"""
    /* Background image for main chat area */
    .stApp {{
        background: linear-gradient(rgba(10, 10, 10, 0.85), rgba(10, 10, 10, 0.92)), 
                    url('data:image/jpeg;base64,{bg_image_base64}') no-repeat center center fixed;
        background-size: cover;
    }}
    
    .main .block-container {{
        background: var(--glass-bg);
        backdrop-filter: blur(24px) saturate(180%);
        -webkit-backdrop-filter: blur(24px) saturate(180%);
        border: 1px solid var(--glass-border);
    }}
    """
    else:
        bg_css = """
    /* Solid background if no image */
    .stApp {{
        background: var(--color-bg-dark);
    }}
    
    .main .block-container {{
        background: var(--color-bg-medium);
        border: 1px solid var(--color-border);
    }}
    """
    
    css = f"""
    <style>
    /* ============================================
       GOOGLE FONT OUTFIT - Elite Typography
       ============================================ */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
    
    /* ============================================
       CSS VARIABLES - {colors['name']} Theme
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
        --color-border: {colors['border']};
        --glass-bg: {colors['glass-bg']};
        --glass-border: {colors['glass-border']};
        --gradient-start: {colors['gradient-start']};
        --gradient-end: {colors['gradient-end']};
        --neon-glow: {colors['neon-glow']};
        
        --border-radius-sm: 6px;
        --border-radius-md: 8px;
        --border-radius-lg: 12px;
        --border-radius-xl: 16px;
        
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.12);
        --shadow-md: 0 4px 12px rgba(0, 0, 0, 0.15);
        --shadow-lg: 0 8px 24px rgba(0, 0, 0, 0.2);
        --shadow-glass: 0 8px 32px rgba(0, 0, 0, 0.37);
        
        --transition-fast: 0.12s cubic-bezier(0.2, 0, 0.38, 0.9);
        --transition-normal: 0.2s cubic-bezier(0.2, 0, 0.38, 0.9);
        --transition-slow: 0.3s cubic-bezier(0.2, 0, 0.38, 0.9);
    }}
    
    /* ============================================
       GLOBAL FONT APPLICATION
       ============================================ */
    .stApp, body, * {{
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }}
    
    /* Code blocks use monospace */
    code, pre, .stCodeBlock {{
        font-family: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace !important;
    }}
    
    /* ============================================
       BACKGROUND
       ============================================ */
    {bg_css}
    
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        border-radius: var(--border-radius-lg);
        margin: 1rem;
        box-shadow: var(--shadow-glass);
    }}
    
    /* ============================================
       SIDEBAR STYLING
       ============================================ */
    [data-testid="stSidebar"] {{
        background: var(--color-bg-medium);
        border-right: 1px solid var(--color-border);
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
    
    /* Sidebar buttons - gradient style */
    [data-testid="stSidebar"] .stButton button {{
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
        border: none !important;
        padding: 0.4rem 1rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        color: var(--color-text-primary) !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
        position: relative !important;
        z-index: 1 !important;
    }}
    
    [data-testid="stSidebar"] .stButton button:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px var(--neon-glow) !important;
    }}
    
    /* Fix button container overflow */
    [data-testid="stSidebar"] .stButton {{
        overflow: hidden !important;
    }}
    
    /* Ensure columns don't overlap */
    [data-testid="stSidebar"] .row-widget {{
        overflow: visible !important;
    }}
    
    [data-testid="stSidebar"] [data-testid="column"] {{
        overflow: visible !important;
        padding: 0 0.2rem !important;
    }}
    
    /* ============================================
       CHAT MESSAGES - Glass Morphism
       ============================================ */
    .stChatMessage {{
        background: var(--glass-bg) !important;
        backdrop-filter: blur(20px) saturate(180%) !important;
        -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--border-radius-lg) !important;
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
        box-shadow: var(--shadow-md) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stChatMessage:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg) !important;
        border-color: var(--color-primary) !important;
    }}
    
    /* User message - Primary color accent */
    .stChatMessage[data-testid="user-message"] {{
        background: linear-gradient(135deg, var(--glass-bg), rgba(255, 255, 255, 0.03)) !important;
        border-left: 3px solid var(--color-primary) !important;
    }}
    
    /* Assistant message - Subtle glass */
    .stChatMessage[data-testid="assistant-message"] {{
        background: var(--glass-bg) !important;
        border-left: 3px solid var(--color-secondary) !important;
    }}
    
    /* ============================================
       CODE BLOCKS
       ============================================ */
    .stChatMessage code {{
        font-family: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace !important;
        background: var(--color-bg-light) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--border-radius-sm) !important;
        padding: 0.2em 0.4em !important;
        color: var(--color-text-primary) !important;
        font-size: 0.9em !important;
    }}
    
    .stChatMessage pre {{
        position: relative;
        background: var(--color-bg-dark) !important;
        border: 1px solid var(--color-border) !important;
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
       HEADERS - Clean & Bold
       ============================================ */
    h1, h2, h3 {{
        color: var(--color-text-primary) !important;
        font-weight: 700 !important;
        margin-top: 1.5rem !important;
        margin-bottom: 0.75rem !important;
        border-bottom: 1px solid var(--color-border);
        padding-bottom: 0.5rem;
        letter-spacing: -0.02em;
    }}
    
    h1 {{
        font-size: 2rem !important;
        font-weight: 800 !important;
    }}
    
    h2 {{
        font-size: 1.5rem !important;
    }}
    
    h3 {{
        font-size: 1.25rem !important;
        border-bottom: none;
        font-weight: 600 !important;
    }}
    
    /* ============================================
       METRICS/TOKEN COUNTER
       ============================================ */
    [data-testid="metric-container"] {{
        background: linear-gradient(135deg, var(--glass-bg), rgba(255, 255, 255, 0.02));
        border: 2px solid var(--glass-border);
        border-radius: var(--border-radius-md);
        padding: 1rem;
        backdrop-filter: blur(10px);
        box-shadow: 0 2px 12px var(--neon-glow);
        transition: all var(--transition-normal);
    }}
    
    [data-testid="metric-container"]:hover {{
        transform: translateY(-5px);
        box-shadow: 0 0 30px var(--neon-glow);
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
       BUTTONS - Gradient & Neon
       ============================================ */
    .stButton button {{
        background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end)) !important;
        color: var(--color-text-primary) !important;
        border: none !important;
        border-radius: var(--border-radius-xl) !important;
        padding: 0.6rem 2rem !important;
        font-weight: 600 !important;
        box-shadow: 0 0 20px var(--neon-glow) !important;
        transition: all var(--transition-normal) !important;
    }}
    
    .stButton button:hover {{
        transform: scale(1.05);
        box-shadow: 0 0 30px var(--neon-glow) !important;
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
        background: var(--color-bg-light) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--border-radius-sm) !important;
        color: var(--color-text-primary) !important;
        transition: all var(--transition-fast) !important;
        padding: 0.5rem 0.75rem !important;
        font-weight: 400 !important;
    }}
    
    .stTextInput input:focus, .stTextArea textarea:focus, .stSelectbox select:focus {{
        outline: 2px solid var(--color-primary) !important;
        outline-offset: -1px !important;
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px var(--neon-glow) !important;
    }}
    
    .stTextInput input:hover, .stTextArea textarea:hover, .stSelectbox select:hover {{
        border-color: var(--color-text-secondary) !important;
    }}
    
    /* ============================================
       CHAT INPUT
       ============================================ */
    .stChatInput {{
        background: var(--color-bg-light) !important;
        border: 1px solid var(--color-border) !important;
        border-radius: var(--border-radius-md) !important;
        padding: 0.5rem !important;
        transition: all var(--transition-fast) !important;
    }}
    
    .stChatInput:focus-within {{
        outline: 2px solid var(--color-primary) !important;
        outline-offset: -1px !important;
        border-color: var(--color-primary) !important;
        box-shadow: 0 0 0 3px var(--neon-glow) !important;
    }}
    
    .stChatInput input {{
        background: transparent !important;
        border: none !important;
        color: var(--color-text-primary) !important;
    }}
    
    /* ============================================
       SCROLLBAR
       ============================================ */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: var(--color-bg-medium);
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: var(--color-border);
        border-radius: 6px;
        border: 2px solid var(--color-bg-medium);
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: var(--color-text-secondary);
    }}
    
    ::-webkit-scrollbar-thumb:active {{
        background: var(--color-primary);
    }}
    
    /* ============================================
       EXPANDER
       ============================================ */
    .streamlit-expanderHeader {{
        background: var(--color-bg-light) !important;
        border-radius: var(--border-radius-sm) !important;
        border: 1px solid var(--color-border) !important;
        transition: all var(--transition-fast) !important;
        font-weight: 500 !important;
    }}
    
    .streamlit-expanderHeader:hover {{
        background: var(--color-bg-medium) !important;
        border-color: var(--color-text-secondary) !important;
    }}
    
    [data-testid="stExpanderDetails"] {{
        background: var(--color-bg-medium) !important;
        border: 1px solid var(--color-border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--border-radius-sm) var(--border-radius-sm) !important;
    }}
    
    /* ============================================
       TOAST NOTIFICATIONS
       ============================================ */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: var(--border-radius-sm) !important;
        border: 1px solid !important;
        padding: 1rem !important;
        animation: slideIn var(--transition-normal) ease-out;
        font-weight: 500 !important;
    }}
    
    .stSuccess {{
        background: rgba(63, 185, 80, 0.1) !important;
        border-color: var(--color-success) !important;
        color: var(--color-success) !important;
    }}
    
    .stInfo {{
        background: rgba(88, 166, 255, 0.1) !important;
        border-color: var(--color-info) !important;
        color: var(--color-info) !important;
    }}
    
    .stWarning {{
        background: rgba(210, 153, 34, 0.1) !important;
        border-color: var(--color-warning) !important;
        color: var(--color-warning) !important;
    }}
    
    .stError {{
        background: rgba(248, 81, 73, 0.1) !important;
        border-color: var(--color-error) !important;
        color: var(--color-error) !important;
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
        background: linear-gradient(135deg, var(--glass-bg), rgba(255, 255, 255, 0.02));
        border: 1px solid var(--glass-border);
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
        background: linear-gradient(180deg, var(--gradient-start), var(--gradient-end));
        transform: scaleY(0);
        transition: transform var(--transition-normal);
    }}
    
    .conversation-card:hover {{
        transform: translateX(5px);
        border-color: var(--color-primary);
        box-shadow: 0 0 20px var(--neon-glow);
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
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-lg);
        animation: pulse 2s infinite;
    }}
    
    .thinking-spinner {{
        display: inline-block;
        width: 16px;
        height: 16px;
        border: 2px solid var(--glass-border);
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
    
    /* Hide Streamlit branding and debug elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Hide any debug or key text */
    [data-testid] *[class*="key_"] {{
        overflow: hidden !important;
    }}
    
    /* Prevent text overflow globally */
    * {{
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
    }}
    
    /* Ensure proper text clipping */
    .element-container {{
        overflow: hidden !important;
    }}
    
    /* Fix columns spacing to prevent overlap */
    [data-testid="column"] {{
        padding-left: 0.25rem !important;
        padding-right: 0.25rem !important;
        min-width: 0 !important;
    }}
    
    /* Ensure tabs don't overflow */
    .stTabs {{
        overflow: hidden !important;
    }}
    
    .stTabs [data-baseweb="tab-list"] {{
        overflow-x: auto !important;
        flex-wrap: nowrap !important;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }}
    
    /* ============================================
       SPECIAL: THEME SELECTOR STYLING
       ============================================ */
    .theme-selector {{
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: var(--border-radius-md);
        padding: 1rem;
        margin-bottom: 1rem;
    }}
    
    .theme-preview {{
        display: inline-block;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        border: 2px solid var(--color-border);
        margin-right: 0.5rem;
        transition: all var(--transition-fast);
    }}
    
    .theme-preview:hover {{
        transform: scale(1.2);
        box-shadow: 0 0 15px var(--neon-glow);
    }}
    </style>
    """
    
    return css
