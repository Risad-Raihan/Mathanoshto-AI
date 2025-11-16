"""
Login page component
"""
import streamlit as st
import extra_streamlit_components as stx
from backend.database.user_operations import UserDB, UserSessionDB
from backend.config.settings import settings
from backend.auth.firebase_rest_auth import signup_with_email_password, signin_with_email_password, get_firebase_api_key


def get_cookie_manager():
    """
    Get or create CookieManager instance (cached in session state to avoid duplicate keys)
    
    Returns:
        CookieManager instance
    """
    if 'cookie_manager' not in st.session_state:
        st.session_state.cookie_manager = stx.CookieManager(key="cookie_manager_init")
    return st.session_state.cookie_manager


def render_login_page():
    """
    Render login/signup page with tabs and Remember Me functionality
    Note: Auto-login is now handled in require_login() to avoid duplicate checks
    """
    # Get cookie manager (cached instance)
    cookie_manager = get_cookie_manager()
    
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
        
        # Tabs for Login and Sign Up
        tab1, tab2 = st.tabs(["🔐 Sign In", "✨ Sign Up"])
        
        # Check if Firebase Web API Key is configured
        firebase_api_key = get_firebase_api_key()
        use_firebase_rest = settings.use_firebase_auth and firebase_api_key
        
        # ===== LOGIN TAB =====
        with tab1:
            if use_firebase_rest:
                # Firebase Email/Password Login
                with st.form("firebase_login_form", clear_on_submit=False):
                    st.markdown("### 🔥 Sign In with Firebase")
                    
                    email = st.text_input(
                        "Email",
                        placeholder="your@email.com",
                        key="firebase_login_email"
                    )
                    
                    password = st.text_input(
                        "Password",
                        type="password",
                        placeholder="Enter your password",
                        key="firebase_login_password"
                    )
                    
                    remember_me = st.checkbox(
                        "Remember me for 30 days",
                        value=True,
                        key="firebase_remember_me"
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    submitted = st.form_submit_button(
                        "🔐 Sign In",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    if submitted:
                        if not email or not password:
                            st.error("Please enter both email and password")
                        else:
                            try:
                                # Sign in with Firebase REST API
                                firebase_result = signin_with_email_password(email, password)
                                
                                # Check if signin was successful (has localId or idToken)
                                if firebase_result and ('localId' in firebase_result or 'idToken' in firebase_result):
                                    # Get or create user in database
                                    user = None
                                    
                                    # Try using idToken if available
                                    if 'idToken' in firebase_result:
                                        user = UserDB.authenticate_with_firebase(firebase_result['idToken'])
                                    
                                    # If no user yet, create from REST response directly (handles localId case)
                                    if not user:
                                        user = UserDB.create_user_from_firebase_rest_response(firebase_result)
                                    
                                    if user:
                                        _set_user_session_state(user)
                                        
                                        # Create session token for Remember Me
                                        if remember_me:
                                            try:
                                                plain_token, _ = UserSessionDB.create_session(user.id)
                                                cookie_manager.set('session_token', plain_token, max_age=30*24*60*60)
                                            except Exception as e:
                                                print(f"Failed to create session: {e}")
                                        
                                        st.success(f"✅ Welcome back, {user.full_name or user.email}!")
                                        st.rerun()
                                    else:
                                        st.error("❌ Failed to create user account. Please try again.")
                                else:
                                    st.error("❌ Invalid email or password")
                            except Exception as e:
                                error_msg = str(e)
                                if "INVALID_PASSWORD" in error_msg or "EMAIL_NOT_FOUND" in error_msg:
                                    st.error("❌ Invalid email or password")
                                elif "USER_DISABLED" in error_msg:
                                    st.error("❌ This account has been disabled")
                                else:
                                    st.error(f"❌ Authentication error: {error_msg}")
            
            # Show error if Firebase is not configured
            if not use_firebase_rest:
                st.error("❌ Firebase Web API Key is not configured. Please set FIREBASE_WEB_API_KEY in your environment.")
        
        # ===== SIGNUP TAB =====
        with tab2:
            if use_firebase_rest:
                # Firebase Email/Password Signup
                with st.form("firebase_signup_form", clear_on_submit=True):
                    st.markdown("### ✨ Sign Up with Firebase")
                    
                    new_email = st.text_input(
                        "Email *",
                        placeholder="your@email.com",
                        key="firebase_signup_email"
                    )
                    
                    new_full_name = st.text_input(
                        "Full Name",
                        placeholder="Your full name (optional)",
                        key="firebase_signup_full_name"
                    )
                    
                    col_a, col_b = st.columns(2)
                    
                    with col_a:
                        new_password = st.text_input(
                            "Password *",
                            type="password",
                            placeholder="Create a strong password",
                            key="firebase_signup_password",
                            help="Minimum 6 characters"
                        )
                    
                    with col_b:
                        confirm_password = st.text_input(
                            "Confirm Password *",
                            type="password",
                            placeholder="Re-enter password",
                            key="firebase_signup_confirm_password"
                        )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    signup_submitted = st.form_submit_button(
                        "✨ Create Account",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    if signup_submitted:
                        # Validation
                        if not new_email or not new_password:
                            st.error("❌ Please fill in all required fields")
                        elif len(new_password) < 6:
                            st.error("❌ Password must be at least 6 characters long")
                        elif new_password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif '@' not in new_email:
                            st.error("❌ Please enter a valid email address")
                        else:
                            try:
                                # Sign up with Firebase REST API
                                firebase_result = signup_with_email_password(
                                    email=new_email,
                                    password=new_password,
                                    display_name=new_full_name if new_full_name else None
                                )
                                
                                # Check if signup was successful (has localId or idToken)
                                if firebase_result and ('localId' in firebase_result or 'idToken' in firebase_result):
                                    # Create user in database
                                    try:
                                        user = None
                                        
                                        # Try using idToken if available
                                        if 'idToken' in firebase_result:
                                            user = UserDB.authenticate_with_firebase(firebase_result['idToken'])
                                        
                                        # If no user yet, create from REST response directly (handles localId case)
                                        if not user:
                                            user = UserDB.create_user_from_firebase_rest_response(firebase_result)
                                        
                                        if user:
                                            st.success(f"✅ Account created! Welcome, {user.full_name or user.email}!")
                                            st.info("👉 Please switch to the **Sign In** tab to login")
                                        else:
                                            st.error("❌ Account created in Firebase but failed to create database record.")
                                            st.info("💡 Check terminal logs for details. You can try signing in - the account will be created automatically.")
                                    except Exception as db_error:
                                        st.error(f"❌ Database error: {str(db_error)}")
                                        import traceback
                                        st.code(traceback.format_exc())
                                else:
                                    st.error("❌ Failed to create account in Firebase. Please try again.")
                                    if firebase_result:
                                        st.error(f"Debug: Firebase response keys: {list(firebase_result.keys())}")
                            except Exception as e:
                                error_msg = str(e)
                                if "EMAIL_EXISTS" in error_msg:
                                    st.error("❌ An account with this email already exists. Please sign in instead.")
                                elif "WEAK_PASSWORD" in error_msg:
                                    st.error("❌ Password is too weak. Please use a stronger password.")
                                elif "INVALID_EMAIL" in error_msg:
                                    st.error("❌ Invalid email address. Please check your email.")
                                else:
                                    st.error(f"❌ Error creating account: {error_msg}")
                                    import traceback
                                    st.code(traceback.format_exc())
            
            # Show error if Firebase is not configured
            if not use_firebase_rest:
                st.error("❌ Firebase Web API Key is not configured. Please set FIREBASE_WEB_API_KEY in your environment.")
        
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
    st.session_state.username = user.username or user.email or f"user_{user.id}"
    st.session_state.full_name = user.full_name
    st.session_state.email = user.email
    st.session_state.firebase_uid = user.firebase_uid
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
    # Get cookie manager (cached instance)
    cookie_manager = get_cookie_manager()
    
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
    Also checks for Remember Me cookie and auto-logs in if valid
    
    Returns:
        bool: True if logged in, False otherwise
    """
    # First check if already logged in via session state
    if st.session_state.get('logged_in', False):
        return True
    
    # If not logged in, check for Remember Me cookie
    cookie_manager = get_cookie_manager()
    session_token = cookie_manager.get('session_token')
    
    if session_token:
        # Try to auto-login with session token
        user = UserSessionDB.validate_session(session_token)
        if user:
            # Auto-login successful
            _set_user_session_state(user)
            st.rerun()
            return True
    
    # No valid session, show login page
    render_login_page()
    return False

