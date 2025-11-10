"""
Login page component
"""
import streamlit as st
from backend.database.user_operations import UserDB


def render_login_page():
    """
    Render a simple, clean login page
    """
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # App logo/title
        st.markdown("""
        <div style="text-align: center; margin-bottom: 3rem;">
            <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">🧠</h1>
            <h1 style="margin-top: 0;">Mathanoshto AI</h1>
            <p style="color: #888; font-size: 1.1rem;">Your Personal AI Assistant</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="login_username"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="login_password"
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button(
                "🔐 Sign In",
                use_container_width=True
            )
            
            if submitted:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    # Authenticate user
                    user = UserDB.authenticate_user(username, password)
                    
                    if user:
                        # Store user info in session state
                        st.session_state.user_id = user.id
                        st.session_state.username = user.username
                        st.session_state.full_name = user.full_name
                        st.session_state.user_preferences = {
                            'default_provider': user.default_provider,
                            'default_model': user.default_model,
                            'default_temperature': user.default_temperature,
                            'default_max_tokens': user.default_max_tokens,
                            'theme': user.theme
                        }
                        st.session_state.logged_in = True
                        
                        st.success(f"✅ Welcome back, {user.full_name or user.username}!")
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        
        # Team info
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>Team Members: Risad • Mazed • Mrittika • Nafis • Rafi</p>
            <p style="margin-top: 1rem;">Need help? Contact your team administrator</p>
        </div>
        """, unsafe_allow_html=True)


def logout():
    """Logout user and clear session"""
    keys_to_clear = [
        'user_id', 'username', 'full_name', 'user_preferences', 
        'logged_in', 'chat_manager', 'current_conversation_id', 
        'messages'
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    st.rerun()


def require_login():
    """
    Check if user is logged in, show login page if not
    
    Returns:
        bool: True if logged in, False otherwise
    """
    if not st.session_state.get('logged_in', False):
        render_login_page()
        return False
    return True

