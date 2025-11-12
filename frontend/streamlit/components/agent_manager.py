"""
Agent Manager UI - Create, view, edit, and manage AI agents (personas)
"""

import streamlit as st
from backend.database.operations import get_db
from backend.core.agent_manager import get_agent_manager
from frontend.streamlit.components.ui_utils import show_toast
from typing import Optional


class AgentManagerUI:
    """UI for managing AI agents"""
    
    @staticmethod
    def render():
        """Render the agent manager interface"""
        st.title("🤖 AI Agent Management")
        st.markdown("""
        Manage your AI agents (personas). System agents are pre-defined, while you can create custom agents tailored to your needs.
        """)
        
        user_id = st.session_state.get('user_id')
        if not user_id:
            st.error("User not authenticated")
            return
        
        # Initialize database
        db = get_db()
        agent_manager = get_agent_manager(db)
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "📋 All Agents",
            "➕ Create Agent",
            "✏️ Edit Agent",
            "📊 Agent Stats"
        ])
        
        with tab1:
            AgentManagerUI._render_agent_list(agent_manager, user_id)
        
        with tab2:
            AgentManagerUI._render_create_agent(agent_manager, user_id)
        
        with tab3:
            AgentManagerUI._render_edit_agent(agent_manager, user_id)
        
        with tab4:
            AgentManagerUI._render_agent_stats(agent_manager, user_id)
        
        db.close()
    
    @staticmethod
    def _render_agent_list(agent_manager, user_id: int):
        """Render list of all agents"""
        st.subheader("📋 All Agents")
        
        # Filter options
        col1, col2 = st.columns(2)
        with col1:
            show_type = st.selectbox(
                "Show",
                ["All Agents", "System Agents Only", "My Custom Agents Only"],
                key="agent_filter_type"
            )
        
        with col2:
            category_filter = st.selectbox(
                "Category",
                ["All"] + [cat.title() for cat in ["research", "development", "product", "data", "documentation", "custom"]],
                key="agent_filter_category"
            )
        
        # Get agents based on filters
        category = None if category_filter == "All" else category_filter.lower()
        
        if show_type == "System Agents Only":
            agents = [a for a in agent_manager.get_all_agents(category=category, user_id=user_id) if a.is_system]
        elif show_type == "My Custom Agents Only":
            agents = [a for a in agent_manager.get_all_agents(category=category, user_id=user_id) if not a.is_system]
        else:
            agents = agent_manager.get_all_agents(category=category, user_id=user_id)
        
        if not agents:
            st.info("No agents found. Try adjusting your filters.")
            return
        
        # Display agents
        st.write(f"**Found {len(agents)} agent(s)**")
        
        for agent in agents:
            with st.expander(f"{agent.emoji} **{agent.name}**" + (" 🔒 System" if agent.is_system else " ✏️ Custom"), expanded=False):
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown(f"**Description:** {agent.description}")
                    st.caption(f"**Category:** {agent.category.title()}")
                    st.caption(f"**Tone:** {agent.tone.title()}")
                    st.caption(f"**Temperature:** {agent.temperature}")
                    st.caption(f"**Max Tokens:** {agent.max_tokens}")
                    
                    if agent.allowed_tools:
                        st.caption(f"**Allowed Tools:** {', '.join(agent.allowed_tools)}")
                    
                    if agent.usage_count > 0:
                        st.caption(f"**Usage Count:** {agent.usage_count}")
                    
                    if agent.rating > 0:
                        st.caption(f"**Rating:** {agent.rating:.1f} ⭐")
                    
                    # Show system prompt in code block
                    with st.expander("📜 View System Prompt"):
                        st.code(agent.system_prompt, language="text")
                
                with col2:
                    # Action buttons
                    if st.button("🎯 Use", key=f"use_agent_{agent.id}", use_container_width=True):
                        st.session_state.selected_agent_id = agent.id
                        show_toast(f"Selected agent: {agent.name}", "success")
                        st.rerun()
                    
                    if not agent.is_system and agent.created_by == user_id:
                        if st.button("✏️ Edit", key=f"edit_agent_{agent.id}", use_container_width=True):
                            st.session_state.editing_agent_id = agent.id
                            st.rerun()
                        
                        if st.button("🗑️ Delete", key=f"delete_agent_{agent.id}", use_container_width=True):
                            if agent_manager.delete_agent(agent.id, user_id):
                                show_toast(f"Deleted agent: {agent.name}", "success")
                                st.rerun()
                            else:
                                show_toast("Failed to delete agent", "error")
    
    @staticmethod
    def _render_create_agent(agent_manager, user_id: int):
        """Render form to create a new custom agent"""
        st.subheader("➕ Create Custom Agent")
        
        st.info("💡 **Tip:** Create specialized agents for your specific workflows. Be creative with your system prompts!")
        
        with st.form("create_agent_form"):
            # Basic info
            col1, col2 = st.columns([3, 1])
            
            with col1:
                name = st.text_input(
                    "Agent Name *",
                    placeholder="e.g., Django Expert, Bug Hunter, Documentation Writer",
                    help="Give your agent a descriptive name"
                )
            
            with col2:
                emoji = st.text_input(
                    "Emoji",
                    value="🤖",
                    max_chars=2,
                    help="Choose an emoji for your agent"
                )
            
            description = st.text_area(
                "Description *",
                placeholder="What does this agent do? What is it specialized in?",
                help="Describe your agent's purpose and specialization",
                height=100
            )
            
            system_prompt = st.text_area(
                "System Prompt *",
                placeholder="You are an expert in...\n\nYour role is to...\n\nWhen responding:\n1. ...\n2. ...",
                help="This defines your agent's personality, expertise, and behavior",
                height=300
            )
            
            # Settings
            st.divider()
            st.subheader("⚙️ Agent Settings")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category = st.selectbox(
                    "Category",
                    ["custom", "research", "development", "product", "data", "documentation"],
                    help="Categorize your agent"
                )
            
            with col2:
                tone = st.selectbox(
                    "Tone",
                    ["professional", "casual", "technical", "creative", "friendly", "analytical"],
                    help="Agent's communication style"
                )
            
            with col3:
                expertise = st.selectbox(
                    "Expertise Level",
                    ["beginner", "intermediate", "expert"],
                    index=2,
                    help="Agent's knowledge depth"
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=0.7,
                    step=0.1,
                    help="Higher = more creative, Lower = more focused"
                )
            
            with col2:
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=100,
                    max_value=8000,
                    value=2000,
                    step=100,
                    help="Maximum response length"
                )
            
            # Tool permissions
            st.divider()
            st.subheader("🛠️ Tool Permissions")
            st.caption("Select which tools this agent can use")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                allow_web_search = st.checkbox("Web Search", value=True)
            with col2:
                allow_web_scraper = st.checkbox("Web Scraper", value=True)
            with col3:
                allow_youtube = st.checkbox("YouTube", value=True)
            with col4:
                allow_data_analyzer = st.checkbox("Data Analyzer", value=True)
            
            # Tags
            tags_input = st.text_input(
                "Tags (comma-separated)",
                placeholder="python, debugging, backend, api",
                help="Add tags for easier searching"
            )
            
            # Submit button
            submitted = st.form_submit_button("✨ Create Agent", use_container_width=True)
            
            if submitted:
                # Validation
                if not name or not description or not system_prompt:
                    st.error("❌ Please fill in all required fields (Name, Description, System Prompt)")
                    return
                
                # Parse tags
                tags = [t.strip() for t in tags_input.split(',') if t.strip()] if tags_input else []
                
                # Build allowed tools list
                allowed_tools = []
                if allow_web_search:
                    allowed_tools.extend(["web_search", "tavily_search"])
                if allow_web_scraper:
                    allowed_tools.append("web_scraper")
                if allow_youtube:
                    allowed_tools.extend(["youtube", "youtube_summarizer"])
                if allow_data_analyzer:
                    allowed_tools.append("data_analyzer")
                
                # Create agent
                agent = agent_manager.create_custom_agent(
                    user_id=user_id,
                    name=name,
                    description=description,
                    system_prompt=system_prompt,
                    emoji=emoji,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tone=tone,
                    category=category,
                    allowed_tools=allowed_tools,
                    tags=tags
                )
                
                if agent:
                    show_toast(f"✅ Created agent: {name}", "success")
                    st.success(f"🎉 Successfully created **{name}**!")
                    st.balloons()
                    st.rerun()
                else:
                    st.error("❌ Failed to create agent. Agent name might already exist.")
    
    @staticmethod
    def _render_edit_agent(agent_manager, user_id: int):
        """Render form to edit an existing custom agent"""
        st.subheader("✏️ Edit Custom Agent")
        
        # Get user's custom agents
        custom_agents = [a for a in agent_manager.get_all_agents(user_id=user_id) if not a.is_system and a.created_by == user_id]
        
        if not custom_agents:
            st.info("You don't have any custom agents yet. Create one in the 'Create Agent' tab!")
            return
        
        # Select agent to edit
        agent_options = {f"{a.emoji} {a.name}": a.id for a in custom_agents}
        
        # Check if there's a pre-selected agent to edit
        editing_agent_id = st.session_state.get('editing_agent_id')
        default_index = 0
        
        if editing_agent_id:
            for idx, (name, agent_id) in enumerate(agent_options.items()):
                if agent_id == editing_agent_id:
                    default_index = idx
                    break
            st.session_state.editing_agent_id = None  # Clear after use
        
        selected_agent_name = st.selectbox(
            "Select Agent to Edit",
            list(agent_options.keys()),
            index=default_index
        )
        
        selected_agent_id = agent_options[selected_agent_name]
        agent = agent_manager.get_agent_by_id(selected_agent_id)
        
        if not agent:
            st.error("Agent not found")
            return
        
        with st.form("edit_agent_form"):
            # Basic info
            col1, col2 = st.columns([3, 1])
            
            with col1:
                name = st.text_input(
                    "Agent Name *",
                    value=agent.name
                )
            
            with col2:
                emoji = st.text_input(
                    "Emoji",
                    value=agent.emoji,
                    max_chars=2
                )
            
            description = st.text_area(
                "Description *",
                value=agent.description,
                height=100
            )
            
            system_prompt = st.text_area(
                "System Prompt *",
                value=agent.system_prompt,
                height=300
            )
            
            # Settings
            st.divider()
            st.subheader("⚙️ Agent Settings")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category = st.selectbox(
                    "Category",
                    ["custom", "research", "development", "product", "data", "documentation"],
                    index=["custom", "research", "development", "product", "data", "documentation"].index(agent.category)
                )
            
            with col2:
                tone = st.selectbox(
                    "Tone",
                    ["professional", "casual", "technical", "creative", "friendly", "analytical"],
                    index=["professional", "casual", "technical", "creative", "friendly", "analytical"].index(agent.tone) if agent.tone in ["professional", "casual", "technical", "creative", "friendly", "analytical"] else 0
                )
            
            with col3:
                expertise = st.selectbox(
                    "Expertise Level",
                    ["beginner", "intermediate", "expert"],
                    index=["beginner", "intermediate", "expert"].index(agent.expertise_level) if agent.expertise_level in ["beginner", "intermediate", "expert"] else 2
                )
            
            col1, col2 = st.columns(2)
            
            with col1:
                temperature = st.slider(
                    "Temperature",
                    min_value=0.0,
                    max_value=2.0,
                    value=float(agent.temperature),
                    step=0.1
                )
            
            with col2:
                max_tokens = st.number_input(
                    "Max Tokens",
                    min_value=100,
                    max_value=8000,
                    value=agent.max_tokens,
                    step=100
                )
            
            # Tool permissions
            st.divider()
            st.subheader("🛠️ Tool Permissions")
            
            current_tools = agent.allowed_tools or []
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                allow_web_search = st.checkbox("Web Search", value="web_search" in current_tools or "tavily_search" in current_tools)
            with col2:
                allow_web_scraper = st.checkbox("Web Scraper", value="web_scraper" in current_tools)
            with col3:
                allow_youtube = st.checkbox("YouTube", value="youtube" in current_tools or "youtube_summarizer" in current_tools)
            with col4:
                allow_data_analyzer = st.checkbox("Data Analyzer", value="data_analyzer" in current_tools)
            
            # Tags
            tags_input = st.text_input(
                "Tags (comma-separated)",
                value=", ".join(agent.tags) if agent.tags else ""
            )
            
            change_summary = st.text_input(
                "Change Summary (optional)",
                placeholder="e.g., Updated system prompt to be more concise",
                help="Describe what you changed"
            )
            
            # Submit button
            col1, col2 = st.columns(2)
            
            with col1:
                submitted = st.form_submit_button("💾 Save Changes", use_container_width=True)
            
            with col2:
                if st.form_submit_button("🗑️ Delete Agent", use_container_width=True):
                    if agent_manager.delete_agent(agent.id, user_id):
                        show_toast(f"Deleted agent: {agent.name}", "success")
                        st.rerun()
                    else:
                        st.error("Failed to delete agent")
            
            if submitted:
                # Validation
                if not name or not description or not system_prompt:
                    st.error("❌ Please fill in all required fields")
                    return
                
                # Parse tags
                tags = [t.strip() for t in tags_input.split(',') if t.strip()] if tags_input else []
                
                # Build allowed tools list
                allowed_tools = []
                if allow_web_search:
                    allowed_tools.extend(["web_search", "tavily_search"])
                if allow_web_scraper:
                    allowed_tools.append("web_scraper")
                if allow_youtube:
                    allowed_tools.extend(["youtube", "youtube_summarizer"])
                if allow_data_analyzer:
                    allowed_tools.append("data_analyzer")
                
                # Update agent
                updated = agent_manager.update_agent(
                    agent_id=agent.id,
                    user_id=user_id,
                    name=name,
                    emoji=emoji,
                    description=description,
                    system_prompt=system_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tone=tone,
                    category=category,
                    expertise_level=expertise,
                    allowed_tools=allowed_tools,
                    tags=tags,
                    change_summary=change_summary if change_summary else "Updated agent configuration"
                )
                
                if updated:
                    show_toast(f"✅ Updated agent: {name}", "success")
                    st.success(f"🎉 Successfully updated **{name}**!")
                    st.rerun()
                else:
                    st.error("❌ Failed to update agent")
    
    @staticmethod
    def _render_agent_stats(agent_manager, user_id: int):
        """Render agent statistics and analytics"""
        st.subheader("📊 Agent Statistics")
        
        # Get all agents
        agents = agent_manager.get_all_agents(user_id=user_id, include_custom=True)
        
        if not agents:
            st.info("No agents available")
            return
        
        # Overall stats
        total_agents = len(agents)
        system_agents = len([a for a in agents if a.is_system])
        custom_agents = len([a for a in agents if not a.is_system])
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Agents", total_agents)
        with col2:
            st.metric("System Agents", system_agents)
        with col3:
            st.metric("Custom Agents", custom_agents)
        
        st.divider()
        
        # Most used agents
        st.subheader("🔥 Most Used Agents")
        
        sorted_agents = sorted(agents, key=lambda a: a.usage_count, reverse=True)[:10]
        
        for agent in sorted_agents:
            if agent.usage_count > 0:
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"{agent.emoji} **{agent.name}**")
                
                with col2:
                    st.write(f"Used: {agent.usage_count}x")
                
                with col3:
                    if agent.rating > 0:
                        st.write(f"{agent.rating:.1f} ⭐")
        
        st.divider()
        
        # Category distribution
        st.subheader("📁 Agents by Category")
        
        categories = agent_manager.get_categories()
        
        for cat_info in categories:
            st.write(f"**{cat_info['category'].title()}:** {cat_info['count']} agent(s)")


def render_agent_manager():
    """Main entry point for agent manager UI"""
    AgentManagerUI.render()

