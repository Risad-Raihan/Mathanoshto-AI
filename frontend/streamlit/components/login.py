"""
Login page component
"""
import streamlit as st
import extra_streamlit_components as stx
from backend.database.user_operations import UserDB, UserSessionDB


def render_login_page():
    """
    Render a simple, clean login page with Remember Me functionality
    """
    # Initialize cookie manager
    cookie_manager = stx.CookieManager()
    
    # Check for existing session token in cookies
    if not st.session_state.get('logged_in', False):
        session_token = cookie_manager.get('session_token')
        if session_token:
            # Try to auto-login with session token
            user = UserSessionDB.validate_session(session_token)
            if user:
                # Auto-login successful
                _set_user_session_state(user)
                st.rerun()
    
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
            
            # Remember Me checkbox
            remember_me = st.checkbox(
                "Remember me for 30 days",
                value=True,
                key="remember_me",
                help="Stay logged in even after closing the browser"
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
                        _set_user_session_state(user)
                        
                        # Create session token if Remember Me is checked
                        if remember_me:
                            try:
                                plain_token, _ = UserSessionDB.create_session(user.id)
                                # Store token in cookie (30 days)
                                cookie_manager.set('session_token', plain_token, max_age=30*24*60*60)
                            except Exception as e:
                                print(f"Failed to create session: {e}")
                        
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


def _set_user_session_state(user):
    """Helper function to set user session state"""
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


def logout():
    """Logout user and clear session"""
    # Get cookie manager
    cookie_manager = stx.CookieManager()
    
    # Delete session token from database
    session_token = cookie_manager.get('session_token')
    if session_token:
        try:
            UserSessionDB.delete_session(session_token)
        except Exception as e:
            print(f"Failed to delete session: {e}")
    
    # Delete cookie
    cookie_manager.delete('session_token')
    
    # Clear session state
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

