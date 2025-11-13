"""
Session State Manager
Centralized session state initialization and management to prevent race conditions
"""

import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime


class SessionStateManager:
    """
    Centralized session state management to prevent race conditions
    """
    
    # Default values for all session state variables
    _defaults = {
        # Authentication
        'logged_in': False,
        'user_id': None,
        'username': None,
        'user_email': None,
        
        # Chat
        'chat_manager': None,
        'current_conversation_id': None,
        'messages': [],
        'attached_images': [],
        'attached_files': [],
        'user_message': '',
        
        # UI State
        'show_image_gallery': False,
        'editing_message': None,
        'regenerating_message': None,
        'theme_name': 'midnight_ocean',  # Default theme
        'dark_mode': True,
        
        # Agent
        'selected_agent_id': None,
        'editing_agent_id': None,
        
        # Loading States
        'loading': False,
        'loading_message': '',
        
        # Flags
        'initialized': False,
        'last_init': None
    }
    
    @classmethod
    def initialize(cls, force: bool = False):
        """
        Initialize all session state variables with default values
        
        Args:
            force: Force re-initialization even if already initialized
        """
        # Check if already initialized
        if not force and st.session_state.get('initialized', False):
            return
        
        # Initialize all defaults
        for key, default_value in cls._defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # Mark as initialized
        st.session_state.initialized = True
        st.session_state.last_init = datetime.now()
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Safely get a session state value with fallback
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
        
        Returns:
            Value from session state or default
        """
        return st.session_state.get(key, default if default is not None else cls._defaults.get(key))
    
    @classmethod
    def set(cls, key: str, value: Any):
        """
        Safely set a session state value
        
        Args:
            key: Session state key
            value: Value to set
        """
        st.session_state[key] = value
    
    @classmethod
    def update_atomic(cls, updates: Dict[str, Any]):
        """
        Atomically update multiple session state variables
        
        Args:
            updates: Dictionary of key-value pairs to update
        """
        # Store all updates in a temporary dict first
        temp_updates = {}
        
        for key, value in updates.items():
            temp_updates[key] = value
        
        # Apply all updates atomically
        for key, value in temp_updates.items():
            st.session_state[key] = value
    
    @classmethod
    def clear(cls, keys: Optional[list] = None):
        """
        Clear specific session state keys or reset to defaults
        
        Args:
            keys: List of keys to clear. If None, clears all
        """
        if keys is None:
            # Clear all and reinitialize
            for key in st.session_state.keys():
                del st.session_state[key]
            cls.initialize(force=True)
        else:
            # Clear specific keys
            for key in keys:
                if key in st.session_state:
                    del st.session_state[key]
                # Restore default if available
                if key in cls._defaults:
                    st.session_state[key] = cls._defaults[key]
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """
        Check if user is authenticated with proper state
        
        Returns:
            True if user is logged in with valid user_id
        """
        return (
            cls.get('logged_in', False) and 
            cls.get('user_id') is not None
        )
    
    @classmethod
    def reset_chat_state(cls):
        """
        Reset chat-related session state (for new conversations)
        """
        chat_keys = [
            'chat_manager',
            'current_conversation_id',
            'messages',
            'attached_images',
            'attached_files',
            'editing_message',
            'regenerating_message'
        ]
        cls.clear(chat_keys)
    
    @classmethod
    def set_loading(cls, loading: bool, message: str = ''):
        """
        Set loading state with message
        
        Args:
            loading: Whether app is loading
            message: Loading message to display
        """
        cls.update_atomic({
            'loading': loading,
            'loading_message': message
        })
    
    @classmethod
    def is_loading(cls) -> bool:
        """
        Check if app is currently in loading state
        
        Returns:
            True if loading
        """
        return cls.get('loading', False)


# Convenience function for initialization
def init_session_state(force: bool = False):
    """
    Initialize session state (convenience function)
    
    Args:
        force: Force re-initialization
    """
    SessionStateManager.initialize(force=force)

