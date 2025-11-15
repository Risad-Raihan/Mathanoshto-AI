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

# Auto-initialize agents if they don't exist
from backend.database.operations import get_db
from backend.core.agent_manager import get_agent_manager
try:
    db = get_db()
    agent_manager = get_agent_manager(db)
    existing_agents = agent_manager.get_all_agents(is_active=True, include_custom=False)
    system_agents = [a for a in existing_agents if a.is_system]
    if len(system_agents) < 10:
        # Initialize system agents if less than 10 exist
        agent_manager.initialize_system_agents()
        print("✅ Auto-initialized system agents")
    db.close()
except Exception as e:
    print(f"⚠️  Could not auto-initialize agents: {e}")

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

# Add aggressive JavaScript to hide Material Icons text - inject directly into main document
st.markdown("""
<script>
(function() {
    function hideKeyboardArrowText() {
        if (!document.body) return;
        
        let found = 0;
        const foundElements = [];
        
        // DEBUG: First, let's find WHERE the text actually is
        const allElements = document.querySelectorAll('*');
        allElements.forEach(el => {
            const text = (el.textContent || el.innerText || '').trim();
            if (text && (
                text === 'keyboard_arrow_right' || 
                text === 'keyboard_arrow_down' || 
                text === 'keyboard_arrow_up' ||
                text === 'keyboard_arrow_left' ||
                text === 'keyboard_double_arrow_right' ||
                text === 'keyboard_double_arrow_down' ||
                text === 'keyboard_double_arrow_up' ||
                text === 'keyboard_double_arrow_left' ||
                text.includes('keyboard_arrow') ||
                text.includes('keyboard_double_arrow')
            )) {
                // Log for debugging
                console.log('🔍 Found keyboard_arrow text:', {
                    text: text,
                    tagName: el.tagName,
                    className: el.className,
                    id: el.id,
                    parent: el.parentElement?.tagName,
                    element: el
                });
                foundElements.push(el);
                
                // Hide it aggressively
                el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;position:absolute!important;left:-9999px!important;';
                el.textContent = '';
                el.innerText = '';
                if (el.innerHTML) el.innerHTML = '';
                found++;
            }
        });
        
        // Also check text nodes
        try {
            if (document.body && document.body.nodeType === 1) {
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    null,
                    false
                );
                
                let textNode;
                while (textNode = walker.nextNode()) {
                    const text = textNode.textContent.trim();
                    if (text && (
                        text === 'keyboard_arrow_right' || 
                        text === 'keyboard_arrow_down' || 
                        text === 'keyboard_arrow_up' ||
                        text === 'keyboard_arrow_left' ||
                        text === 'keyboard_double_arrow_right' ||
                        text === 'keyboard_double_arrow_down' ||
                        text === 'keyboard_double_arrow_up' ||
                        text === 'keyboard_double_arrow_left' ||
                        text.includes('keyboard_arrow') ||
                        text.includes('keyboard_double_arrow')
                    )) {
                        console.log('🔍 Found keyboard_arrow in text node:', {
                            text: text,
                            parent: textNode.parentElement?.tagName,
                            parentClass: textNode.parentElement?.className
                        });
                        
                        if (textNode.parentElement) {
                            textNode.parentElement.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;';
                            textNode.textContent = '';
                            found++;
                        }
                    }
                }
            }
        } catch(e) {
            console.warn('TreeWalker error:', e);
        }
        
        // CRITICAL FIX: Target expander summary elements specifically
        document.querySelectorAll('[data-testid="stExpander"]').forEach(expander => {
            // Find summary elements (native HTML details/summary)
            const summaries = expander.querySelectorAll('summary, details summary');
            summaries.forEach(summary => {
                // Find all spans inside summary
                const spans = summary.querySelectorAll('span');
                spans.forEach(span => {
                    const text = (span.textContent || span.innerText || '').trim();
                    if (text && (
                        text.includes('keyboard_arrow') || 
                        text.includes('keyboard_double_arrow') ||
                        text === 'keyboard_double_arrow_right' ||
                        text === 'keyboard_arrow_right'
                    )) {
                        console.log('🔍 Found keyboard_arrow in expander summary span:', {
                            text: text,
                            className: span.className,
                            parent: summary.tagName,
                            element: span
                        });
                        span.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;position:absolute!important;left:-9999px!important;z-index:-9999!important;clip:rect(0,0,0,0)!important;';
                        span.textContent = '';
                        span.innerText = '';
                        if (span.innerHTML) span.innerHTML = '';
                        found++;
                    }
                });
                
                // Check summary's direct text content
                const summaryText = (summary.textContent || summary.innerText || '').trim();
                if (summaryText && (
                    summaryText.includes('keyboard_arrow') || 
                    summaryText.includes('keyboard_double_arrow')
                )) {
                    // Check if it's ONLY the icon text (not other content)
                    const children = Array.from(summary.children);
                    const hasOnlyIconText = children.length === 0 || summaryText.length < 50;
                    if (hasOnlyIconText || summaryText === 'keyboard_double_arrow_right') {
                        console.log('🔍 Summary contains only icon text, checking children');
                        // The text might be in a pseudo-element or background
                        summary.style.cssText += 'background-image:none!important;';
                    }
                }
                
                // Check for emotion cache classes in summary
                const emotionCacheElements = summary.querySelectorAll('[class*="st-emotion-cache"]');
                emotionCacheElements.forEach(el => {
                    const text = (el.textContent || el.innerText || '').trim();
                    if (text && (text.includes('keyboard_arrow') || text.includes('keyboard_double_arrow'))) {
                        console.log('🔍 Hiding emotion cache element in summary:', {
                            className: el.className,
                            text: text
                        });
                        el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;position:absolute!important;left:-9999px!important;z-index:-9999!important;';
                        el.textContent = '';
                        el.innerText = '';
                        if (el.innerHTML) el.innerHTML = '';
                        found++;
                    }
                    
                    // Check computed styles for content/background that might contain text
                    try {
                        const computed = window.getComputedStyle(el);
                        const computedBefore = window.getComputedStyle(el, '::before');
                        const computedAfter = window.getComputedStyle(el, '::after');
                        
                        // Check if content property contains the text
                        if (computedBefore.content && (
                            computedBefore.content.includes('keyboard_arrow') || 
                            computedBefore.content.includes('keyboard_double_arrow')
                        )) {
                            console.log('🔍 Found keyboard_arrow in ::before pseudo-element');
                            el.style.setProperty('--before-content', 'none', 'important');
                        }
                        
                        if (computedAfter.content && (
                            computedAfter.content.includes('keyboard_arrow') || 
                            computedAfter.content.includes('keyboard_double_arrow')
                        )) {
                            console.log('🔍 Found keyboard_arrow in ::after pseudo-element');
                            el.style.setProperty('--after-content', 'none', 'important');
                        }
                        
                        // Remove background-image if it might contain text
                        if (computed.backgroundImage && computed.backgroundImage !== 'none') {
                            el.style.backgroundImage = 'none';
                        }
                    } catch(e) {
                        // Ignore errors from pseudo-element access
                    }
                });
                
                // Also check summary itself for computed styles
                try {
                    const summaryComputed = window.getComputedStyle(summary);
                    const summaryBefore = window.getComputedStyle(summary, '::before');
                    const summaryAfter = window.getComputedStyle(summary, '::after');
                    
                    if (summaryBefore.content && (
                        summaryBefore.content.includes('keyboard_arrow') || 
                        summaryBefore.content.includes('keyboard_double_arrow')
                    )) {
                        console.log('🔍 Summary has keyboard_arrow in ::before');
                        summary.style.setProperty('--before-content', 'none', 'important');
                    }
                    
                    if (summaryAfter.content && (
                        summaryAfter.content.includes('keyboard_arrow') || 
                        summaryAfter.content.includes('keyboard_double_arrow')
                    )) {
                        console.log('🔍 Summary has keyboard_arrow in ::after');
                        summary.style.setProperty('--after-content', 'none', 'important');
                    }
                } catch(e) {}
            });
            
            // Try multiple selectors for old structure
            const selectors = [
                '.streamlit-expanderHeader > div:last-child',
                '.streamlit-expanderHeader > div > div:last-child',
                '.streamlit-expanderHeader > div > div > div:last-child',
                '> div > div:last-child',
                '> div:last-child'
            ];
            
            selectors.forEach(selector => {
                try {
                    const elements = expander.querySelectorAll(selector);
                    elements.forEach(el => {
                        el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;width:0!important;height:0!important;overflow:hidden!important;';
                    });
                } catch(e) {}
            });
        });
        
        // SPECIFIC FIX: Check header/top bar elements (where keyboard_double_arrow_right appears)
        const headerSelectors = [
            'header',
            '[role="banner"]',
            '[data-testid="stHeader"]',
            '.stApp > header',
            'header *',
            '[data-testid="stHeader"] *'
        ];
        
        headerSelectors.forEach(selector => {
            try {
                const headers = document.querySelectorAll(selector);
                headers.forEach(header => {
                    const allChildren = header.querySelectorAll('*');
                    allChildren.forEach(el => {
                        const text = (el.textContent || el.innerText || '').trim();
                        if (text && (
                            text.includes('keyboard_arrow') || 
                            text.includes('keyboard_double_arrow')
                        )) {
                            console.log('🔍 Found keyboard_arrow in header:', {
                                text: text,
                                tagName: el.tagName,
                                className: el.className,
                                element: el
                            });
                            el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;position:absolute!important;left:-9999px!important;';
                            el.textContent = '';
                            el.innerText = '';
                            if (el.innerHTML) el.innerHTML = '';
                            found++;
                        }
                    });
                });
            } catch(e) {
                console.warn('Header selector error:', e);
            }
        });
        
        // CRITICAL FIX: Target Streamlit selectboxes specifically - they use emotion cache classes
        document.querySelectorAll('[data-testid="stSelectbox"], .stSelectbox').forEach(selectbox => {
            // Find all children and check for icon text
            const allDescendants = selectbox.querySelectorAll('*');
            allDescendants.forEach(el => {
                const text = (el.textContent || el.innerText || '').trim();
                if (text && (
                    text === 'keyboard_arrow_right' || 
                    text === 'keyboard_arrow_down' || 
                    text === 'keyboard_arrow_up' ||
                    text === 'keyboard_arrow_left' ||
                    text === 'keyboard_double_arrow_right' ||
                    text === 'keyboard_double_arrow_down' ||
                    text === 'keyboard_double_arrow_up' ||
                    text === 'keyboard_double_arrow_left' ||
                    text.includes('keyboard_arrow') ||
                    text.includes('keyboard_double_arrow')
                )) {
                    const computed = window.getComputedStyle(el);
                    console.log('🔍 Found keyboard_arrow in selectbox:', {
                        text: text,
                        tagName: el.tagName,
                        className: el.className,
                        zIndex: computed.zIndex,
                        position: computed.position,
                        display: computed.display,
                        visibility: computed.visibility,
                        opacity: computed.opacity,
                        element: el
                    });
                    
                    // Nuclear option: Hide completely with multiple methods
                    el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;position:absolute!important;left:-9999px!important;clip:rect(0,0,0,0)!important;z-index:-9999!important;';
                    el.textContent = '';
                    el.innerText = '';
                    if (el.innerHTML) el.innerHTML = '';
                    
                    // Also hide parent if it only contains this text
                    if (el.parentElement) {
                        const parentText = (el.parentElement.textContent || el.parentElement.innerText || '').trim();
                        if (parentText === text || parentText.includes('keyboard_arrow') || parentText.includes('keyboard_double_arrow')) {
                            const parentComputed = window.getComputedStyle(el.parentElement);
                            console.log('🔍 Hiding parent element:', {
                                parentText: parentText,
                                zIndex: parentComputed.zIndex,
                                position: parentComputed.position
                            });
                            el.parentElement.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;z-index:-9999!important;';
                        }
                    }
                    
                    // Also check siblings that might be overlapping
                    if (el.parentElement) {
                        Array.from(el.parentElement.children).forEach(sibling => {
                            const siblingText = (sibling.textContent || sibling.innerText || '').trim();
                            if (sibling !== el && (siblingText.includes('keyboard_arrow') || siblingText.includes('keyboard_double_arrow'))) {
                                console.log('🔍 Hiding sibling with keyboard_arrow text');
                                sibling.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;z-index:-9999!important;';
                            }
                        });
                    }
                    
                    found++;
                }
            });
            
            // Also check for pseudo-elements by inspecting computed styles
            try {
                const computed = window.getComputedStyle(selectbox, '::after');
                if (computed.content && (computed.content.includes('keyboard_arrow') || computed.content.includes('keyboard_double_arrow'))) {
                    console.log('🔍 Found keyboard_arrow in pseudo-element');
                    // Can't directly modify pseudo-elements, but we can hide the parent's last child
                    const lastChild = selectbox.querySelector(':last-child');
                    if (lastChild) {
                        lastChild.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;';
                    }
                }
            } catch(e) {}
            
            // EXTREME: Hide the last div in selectbox structure (where icon usually is)
            const lastDiv = selectbox.querySelector('> div:last-child');
            if (lastDiv) {
                const lastDivText = (lastDiv.textContent || lastDiv.innerText || '').trim();
                if (lastDivText.includes('keyboard_arrow') || lastDivText.includes('keyboard_double_arrow')) {
                    console.log('🔍 Hiding last div in selectbox');
                    lastDiv.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;z-index:-9999!important;';
                }
            }
            
            // Also check for elements with emotion cache classes that contain the text
            const emotionCacheElements = selectbox.querySelectorAll('[class*="st-emotion-cache"]');
            emotionCacheElements.forEach(el => {
                const text = (el.textContent || el.innerText || '').trim();
                if (text && (text.includes('keyboard_arrow') || text.includes('keyboard_double_arrow'))) {
                    // Check if this element ONLY contains the icon text (not other content)
                    const children = Array.from(el.children);
                    const hasOnlyIconText = children.length === 0 && text.length < 50;
                    if (hasOnlyIconText || text === 'keyboard_double_arrow_right' || text === 'keyboard_arrow_right') {
                        console.log('🔍 Hiding emotion cache element with icon text:', {
                            className: el.className,
                            text: text
                        });
                        el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;z-index:-9999!important;position:absolute!important;left:-9999px!important;';
                        el.textContent = '';
                        el.innerText = '';
                        if (el.innerHTML) el.innerHTML = '';
                    }
                }
            });
        });
        
        // Also check ALL elements with emotion cache classes globally
        document.querySelectorAll('[class*="st-emotion-cache"]').forEach(el => {
            const text = (el.textContent || el.innerText || '').trim();
            if (text && (
                text === 'keyboard_double_arrow_right' ||
                text === 'keyboard_arrow_right' ||
                text === 'keyboard_double_arrow_down' ||
                text === 'keyboard_arrow_down'
            )) {
                // Only hide if it's a small element (likely just the icon text)
                const computed = window.getComputedStyle(el);
                const width = parseFloat(computed.width);
                const height = parseFloat(computed.height);
                
                // If it's a small element or has no children, hide it
                if ((width < 200 && height < 50) || el.children.length === 0) {
                    console.log('🔍 Hiding emotion cache element globally:', {
                        className: el.className,
                        text: text,
                        width: width,
                        height: height
                    });
                    el.style.cssText = 'display:none!important;visibility:hidden!important;opacity:0!important;font-size:0!important;width:0!important;height:0!important;overflow:hidden!important;z-index:-9999!important;position:absolute!important;left:-9999px!important;';
                    el.textContent = '';
                    el.innerText = '';
                    if (el.innerHTML) el.innerHTML = '';
                    found++;
                }
            }
        });
        
        if (found > 0) {
            console.log('✅ Hidden ' + found + ' keyboard_arrow elements');
        } else if (foundElements.length === 0) {
            console.log('⚠️ No keyboard_arrow text found in DOM');
        }
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => {
            console.log('🔍 DOM loaded, searching for keyboard_arrow...');
            hideKeyboardArrowText();
        });
    } else {
        console.log('🔍 DOM ready, searching for keyboard_arrow...');
        hideKeyboardArrowText();
    }
    
    // Run multiple times with delays
    const delays = [10, 50, 100, 200, 500, 1000, 2000, 3000, 5000];
    delays.forEach(delay => {
        setTimeout(() => hideKeyboardArrowText(), delay);
    });
    
    // Watch for DOM changes
    if (document.body) {
        const observer = new MutationObserver((mutations) => {
            let shouldCheck = false;
            mutations.forEach(mutation => {
                if (mutation.addedNodes.length > 0) {
                    shouldCheck = true;
                }
            });
            if (shouldCheck) {
                hideKeyboardArrowText();
            }
        });
        observer.observe(document.body, {
            childList: true, 
            subtree: true, 
            characterData: true
        });
        
        // Run on clicks and mouse events
        document.addEventListener('click', hideKeyboardArrowText, true);
        document.addEventListener('mousedown', hideKeyboardArrowText, true);
        document.addEventListener('mouseup', hideKeyboardArrowText, true);
    }
    
    console.log('✅ Keyboard arrow text remover initialized');
})();
</script>
""", unsafe_allow_html=True)

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

