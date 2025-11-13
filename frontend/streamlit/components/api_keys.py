"""
API Key Management Component
Allows users to add, view, and manage their API keys
"""
import streamlit as st
from backend.database.user_operations import UserAPIKeyDB


def render_api_key_management():
    """
    Render API key management interface for the logged-in user
    """
    user_id = st.session_state.get('user_id')
    
    st.subheader("🔑 API Key Management")
    st.caption("Add and manage your API keys for different LLM providers")
    
    # Get existing keys (without showing decrypted values)
    existing_keys = UserAPIKeyDB.list_user_api_keys(user_id)
    existing_providers = {key['provider'] for key in existing_keys if key['is_active']}
    
    # Show status of existing keys
    if existing_keys:
        st.markdown("### 📋 Your API Keys:")
        for key in existing_keys:
            if key['is_active']:
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{key['provider'].upper()}**")
                with col2:
                    st.caption(f"Added: {key['created_at'].strftime('%Y-%m-%d')}")
                with col3:
                    if st.button("🗑️", key=f"delete_{key['provider']}", help="Delete key"):
                        UserAPIKeyDB.delete_api_key(user_id, key['provider'])
                        st.success(f"Deleted {key['provider']} API key")
                        st.rerun()
        st.divider()
    
    # Add new API key form
    st.markdown("### ➕ Add New API Key")
    
    with st.form("add_api_key_form", clear_on_submit=True):
        provider = st.selectbox(
            "Provider",
            options=['openai', 'gemini', 'anthropic', 'tavily', 'firecrawl', 'mathpix'],
            format_func=lambda x: {
                'openai': 'OpenAI (GPT models)',
                'gemini': 'Google Gemini',
                'anthropic': 'Anthropic (Claude)',
                'tavily': 'Tavily (Web Search)',
                'firecrawl': 'Firecrawl (Advanced Web Scraping)',
                'mathpix': 'Mathpix (OCR & Math Recognition)'
            }.get(x, x.upper())
        )
        
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="Enter your API key here",
            help="Your API key will be encrypted before storage"
        )
        
        # Optional: Base URL for custom endpoints (mainly for OpenAI)
        show_base_url = provider == 'openai'
        base_url = None
        if show_base_url:
            base_url = st.text_input(
                "Base URL (Optional)",
                placeholder="https://api.openai.com/v1",
                help="Leave empty for default OpenAI endpoint"
            )
        
        submitted = st.form_submit_button("💾 Save API Key", use_container_width=True)
        
        if submitted:
            if not api_key:
                st.error("Please enter an API key")
            else:
                try:
                    # Map provider to key name
                    key_name_map = {
                        'openai': 'OPENAI_API_KEY',
                        'gemini': 'GEMINI_API_KEY',
                        'anthropic': 'ANTHROPIC_API_KEY',
                        'tavily': 'TAVILY_API_KEY',
                        'firecrawl': 'FIRECRAWL_API_KEY',
                        'mathpix': 'MATHPIX_API_KEY'
                    }
                    
                    UserAPIKeyDB.add_api_key(
                        user_id=user_id,
                        provider=provider,
                        api_key=api_key,
                        key_name=key_name_map[provider],
                        base_url=base_url if base_url else None
                    )
                    
                    st.success(f"✅ Successfully added {provider.upper()} API key!")
                    st.info("🔄 Please refresh the page or restart the app to use the new API key")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving API key: {str(e)}")
    
    # Help section
    with st.expander("❓ How to get API keys"):
        st.markdown("""
        ### OpenAI
        1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
        2. Sign in and create a new API key
        3. Copy the key and paste it above
        
        ### Google Gemini
        1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
        2. Sign in with your Google account
        3. Create an API key and copy it
        
        ### Anthropic (Claude)
        1. Visit [Anthropic Console](https://console.anthropic.com/)
        2. Sign in and navigate to API keys
        3. Create a new key and copy it
        
        ### Tavily (Web Search)
        1. Visit [Tavily Dashboard](https://app.tavily.com)
        2. Sign up or sign in
        3. Get your API key from the dashboard
        
        ### Firecrawl (Advanced Web Scraping) - Optional
        1. Visit [Firecrawl](https://firecrawl.dev)
        2. Sign up for an account
        3. Get your API key from the dashboard
        4. **Note:** Not currently in use, but supported for future features
        
        ### Mathpix (OCR & Math Recognition) - Optional
        1. Visit [Mathpix OCR](https://mathpix.com/ocr)
        2. Create an account
        3. Get your API credentials
        4. **Note:** Not currently in use, will be used for advanced OCR features
        
        ---
        
        **Important:** 
        - Your API keys are encrypted before storage
        - Keys are never shared or logged
        - You can delete keys anytime
        - Each user manages their own keys (no shared keys in Docker)
        """)

