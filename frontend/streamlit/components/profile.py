"""
User Profile and Settings Component
"""
import streamlit as st
from backend.database.user_operations import UserDB
from backend.database.operations import MessageDB
from datetime import datetime


def render_user_profile():
    """
    Render user profile page with preferences and statistics
    """
    user_id = st.session_state.get('user_id')
    user = UserDB.get_user_by_id(user_id)
    
    if not user:
        st.error("User not found")
        return
    
    st.title("👤 User Profile")
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["📋 Profile", "⚙️ Preferences", "📊 Statistics"])
    
    # ============== PROFILE TAB ==============
    with tab1:
        st.subheader("Profile Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **Username:** `{user.username}`  
            **Full Name:** {user.full_name or 'Not set'}  
            **Email:** {user.email or 'Not set'}  
            **Account Created:** {user.created_at.strftime('%B %d, %Y')}  
            **Last Login:** {user.last_login.strftime('%B %d, %Y at %I:%M %p') if user.last_login else 'Never'}
            """)
        
        with col2:
            # Display avatar placeholder
            st.markdown(f"""
            <div style="
                width: 150px;
                height: 150px;
                border-radius: 50%;
                background: linear-gradient(135deg, #00d4ff, #9d4edd);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 4rem;
                color: white;
                font-weight: bold;
                margin: 0 auto;
            ">
                {user.full_name[0].upper() if user.full_name else user.username[0].upper()}
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # Team members
        st.subheader("👥 Team Members")
        all_users = UserDB.list_all_users()
        
        cols = st.columns(5)
        for idx, team_user in enumerate(all_users):
            with cols[idx % 5]:
                is_current = team_user.id == user_id
                border_color = "#00d4ff" if is_current else "#555"
                
                st.markdown(f"""
                <div style="
                    text-align: center;
                    padding: 1rem;
                    border: 2px solid {border_color};
                    border-radius: 10px;
                    margin-bottom: 1rem;
                ">
                    <div style="
                        width: 60px;
                        height: 60px;
                        border-radius: 50%;
                        background: linear-gradient(135deg, #00d4ff, #9d4edd);
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 1.5rem;
                        color: white;
                        font-weight: bold;
                        margin: 0 auto 0.5rem;
                    ">
                        {team_user.full_name[0].upper() if team_user.full_name else team_user.username[0].upper()}
                    </div>
                    <strong>{team_user.full_name or team_user.username}</strong>
                    {"<br><span style='color: #00d4ff; font-size: 0.8rem;'>● You</span>" if is_current else ""}
                </div>
                """, unsafe_allow_html=True)
    
    # ============== PREFERENCES TAB ==============
    with tab2:
        st.subheader("⚙️ Default Preferences")
        st.caption("Set your default settings for new conversations")
        
        with st.form("preferences_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                default_provider = st.selectbox(
                    "Default Provider",
                    options=['openai', 'gemini'],
                    index=0 if user.default_provider == 'openai' else 1,
                    format_func=lambda x: x.upper()
                )
                
                default_model = st.text_input(
                    "Default Model",
                    value=user.default_model or 'gpt-4o',
                    placeholder="e.g., gpt-4o, gemini-pro"
                )
            
            with col2:
                default_temperature = st.slider(
                    "Default Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=float(user.default_temperature) if user.default_temperature else 0.7,
                    step=0.1,
                    help="Higher = more creative, Lower = more focused"
                )
                
                default_max_tokens = st.number_input(
                    "Default Max Tokens",
                    min_value=100,
                    max_value=8000,
                    value=user.default_max_tokens or 2000,
                    step=100
                )
            
            theme = st.selectbox(
                "Theme",
                options=['dark', 'light'],
                index=0 if user.theme == 'dark' else 1,
                format_func=lambda x: f"🌙 {x.capitalize()}" if x == 'dark' else f"☀️ {x.capitalize()}"
            )
            
            submitted = st.form_submit_button("💾 Save Preferences", use_container_width=True)
            
            if submitted:
                try:
                    UserDB.update_user_preferences(
                        user_id=user_id,
                        default_provider=default_provider,
                        default_model=default_model,
                        default_temperature=default_temperature,
                        default_max_tokens=default_max_tokens,
                        theme=theme
                    )
                    st.success("✅ Preferences saved successfully!")
                    
                    # Update session state
                    st.session_state.user_preferences = {
                        'default_provider': default_provider,
                        'default_model': default_model,
                        'default_temperature': default_temperature,
                        'default_max_tokens': default_max_tokens,
                        'theme': theme
                    }
                    st.session_state.dark_mode = (theme == 'dark')
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error saving preferences: {str(e)}")
    
    # ============== STATISTICS TAB ==============
    with tab3:
        render_user_statistics(user_id)


def render_user_statistics(user_id: int):
    """
    Render user statistics dashboard
    
    Args:
        user_id: User ID
    """
    st.subheader("📊 Your Usage Statistics")
    
    from backend.database.operations import ConversationDB
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from backend.config.settings import settings
    from backend.database.models import Conversation, Message
    
    # Get database session
    engine = create_engine(settings.database_url, echo=False)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get all conversations for user
        conversations = db.query(Conversation).filter(
            Conversation.user_id == user_id
        ).all()
        
        total_conversations = len(conversations)
        active_conversations = len([c for c in conversations if not c.is_archived])
        archived_conversations = len([c for c in conversations if c.is_archived])
        
        # Get all messages for user's conversations
        conversation_ids = [c.id for c in conversations]
        
        if conversation_ids:
            messages = db.query(Message).filter(
                Message.conversation_id.in_(conversation_ids)
            ).all()
            
            total_messages = len(messages)
            user_messages = len([m for m in messages if m.role == 'user'])
            assistant_messages = len([m for m in messages if m.role == 'assistant'])
            
            total_input_tokens = sum(m.input_tokens for m in messages)
            total_output_tokens = sum(m.output_tokens for m in messages)
            total_tokens = total_input_tokens + total_output_tokens
            total_cost = sum(m.cost for m in messages)
            
            # Provider breakdown
            providers = {}
            models = {}
            for msg in messages:
                if msg.provider:
                    providers[msg.provider] = providers.get(msg.provider, 0) + 1
                if msg.model:
                    models[msg.model] = models.get(msg.model, 0) + 1
        else:
            total_messages = user_messages = assistant_messages = 0
            total_input_tokens = total_output_tokens = total_tokens = 0
            total_cost = 0
            providers = {}
            models = {}
        
    finally:
        db.close()
    
    # Display statistics in cards
    st.markdown("### 📈 Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Conversations",
            total_conversations,
            delta=f"{active_conversations} active"
        )
    
    with col2:
        st.metric(
            "Total Messages",
            f"{total_messages:,}",
            delta=f"{user_messages} sent"
        )
    
    with col3:
        st.metric(
            "Total Tokens",
            f"{total_tokens:,}",
            delta=f"${total_cost:.4f} cost"
        )
    
    with col4:
        avg_tokens_per_msg = total_tokens // total_messages if total_messages > 0 else 0
        st.metric(
            "Avg Tokens/Message",
            f"{avg_tokens_per_msg:,}"
        )
    
    st.divider()
    
    # Token usage breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔢 Token Usage")
        st.markdown(f"""
        **Input Tokens:** `{total_input_tokens:,}`  
        **Output Tokens:** `{total_output_tokens:,}`  
        **Total Tokens:** `{total_tokens:,}`  
        **Total Cost:** `${total_cost:.4f}`
        """)
        
        # Cost breakdown
        if total_cost > 0:
            if total_cost < 0.01:
                cost_level = "🟢 Low"
            elif total_cost < 0.10:
                cost_level = "🟡 Medium"
            else:
                cost_level = "🔴 High"
            
            st.info(f"**Cost Level:** {cost_level}")
    
    with col2:
        st.markdown("### 📊 Message Breakdown")
        st.markdown(f"""
        **Your Messages:** `{user_messages:,}`  
        **AI Responses:** `{assistant_messages:,}`  
        **Total:** `{total_messages:,}`
        """)
        
        if total_messages > 0:
            response_rate = (assistant_messages / user_messages * 100) if user_messages > 0 else 0
            st.info(f"**Response Rate:** {response_rate:.1f}%")
    
    st.divider()
    
    # Provider and model usage
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Providers Used")
        if providers:
            for provider, count in sorted(providers.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / total_messages * 100) if total_messages > 0 else 0
                st.progress(percentage / 100, text=f"{provider.upper()}: {count} messages ({percentage:.1f}%)")
        else:
            st.caption("No provider data available")
    
    with col2:
        st.markdown("### 🎯 Top Models")
        if models:
            top_models = sorted(models.items(), key=lambda x: x[1], reverse=True)[:5]
            for model, count in top_models:
                percentage = (count / total_messages * 100) if total_messages > 0 else 0
                st.progress(percentage / 100, text=f"{model}: {count} ({percentage:.1f}%)")
        else:
            st.caption("No model data available")
    
    st.divider()
    
    # Recent activity
    st.markdown("### 🕒 Recent Activity")
    if conversations:
        recent_convs = sorted(conversations, key=lambda c: c.updated_at, reverse=True)[:5]
        
        for conv in recent_convs:
            time_diff = datetime.now() - conv.updated_at
            if time_diff.days == 0:
                if time_diff.seconds < 3600:
                    time_str = f"{time_diff.seconds // 60} minutes ago"
                else:
                    time_str = f"{time_diff.seconds // 3600} hours ago"
            elif time_diff.days == 1:
                time_str = "Yesterday"
            else:
                time_str = f"{time_diff.days} days ago"
            
            st.markdown(f"**{conv.title}** - *{time_str}*")
    else:
        st.caption("No recent activity")

