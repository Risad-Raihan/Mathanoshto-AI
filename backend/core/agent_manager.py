"""
Agent Manager - Handles agent selection, tracking, and management
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Tuple
from datetime import datetime

from backend.database.agent_models import Agent, AgentVersion, AgentSession
from backend.data.predefined_agents import PREDEFINED_AGENTS


class AgentManager:
    """
    Manages AI agents (personas) for the application
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def initialize_system_agents(self) -> List[Agent]:
        """
        Initialize pre-defined system agents in the database
        Call this on first setup or to reset system agents
        """
        created_agents = []
        
        for agent_data in PREDEFINED_AGENTS:
            # Check if agent already exists
            existing = self.db.query(Agent).filter(
                Agent.name == agent_data["name"],
                Agent.is_system == True
            ).first()
            
            if not existing:
                agent = Agent(
                    name=agent_data["name"],
                    emoji=agent_data["emoji"],
                    description=agent_data["description"],
                    system_prompt=agent_data["system_prompt"],
                    temperature=agent_data["temperature"],
                    max_tokens=agent_data["max_tokens"],
                    tone=agent_data.get("tone", "professional"),
                    expertise_level=agent_data.get("expertise_level", "expert"),
                    response_format=agent_data.get("response_format", "markdown"),
                    allowed_tools=agent_data.get("allowed_tools", []),
                    category=agent_data["category"],
                    tags=agent_data.get("tags", []),
                    version="1.0",
                    is_system=True,
                    is_active=True,
                    is_public=True,
                    created_by=None  # System agents have no creator
                )
                
                self.db.add(agent)
                created_agents.append(agent)
        
        self.db.commit()
        
        for agent in created_agents:
            self.db.refresh(agent)
        
        print(f"✅ Initialized {len(created_agents)} system agents")
        return created_agents
    
    def get_all_agents(
        self,
        category: Optional[str] = None,
        is_active: bool = True,
        include_custom: bool = True,
        user_id: Optional[int] = None
    ) -> List[Agent]:
        """
        Get all agents, optionally filtered by category and user
        """
        query = self.db.query(Agent)
        
        if is_active is not None:
            query = query.filter(Agent.is_active == is_active)
        
        if category:
            query = query.filter(Agent.category == category)
        
        # Filter: system agents + user's custom agents
        if include_custom and user_id:
            query = query.filter(
                (Agent.is_system == True) | (Agent.created_by == user_id)
            )
        else:
            query = query.filter(Agent.is_system == True)
        
        return query.order_by(Agent.category, Agent.name).all()
    
    def get_agent_by_id(self, agent_id: int) -> Optional[Agent]:
        """Get specific agent by ID"""
        return self.db.query(Agent).filter(Agent.id == agent_id).first()
    
    def get_agent_by_name(self, name: str) -> Optional[Agent]:
        """Get agent by name"""
        return self.db.query(Agent).filter(Agent.name == name).first()
    
    def create_custom_agent(
        self,
        user_id: int,
        name: str,
        description: str,
        system_prompt: str,
        emoji: str = "🤖",
        temperature: float = 0.7,
        max_tokens: int = 2000,
        tone: str = "professional",
        category: str = "custom",
        allowed_tools: Optional[List[str]] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Agent]:
        """
        Create a custom agent for a user
        """
        try:
            # Check if name already exists for this user
            existing = self.db.query(Agent).filter(
                Agent.name == name,
                Agent.created_by == user_id
            ).first()
            
            if existing:
                print(f"❌ Agent with name '{name}' already exists for user {user_id}")
                return None
            
            agent = Agent(
                name=name,
                emoji=emoji,
                description=description,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                tone=tone,
                category=category,
                allowed_tools=allowed_tools or [],
                tags=tags or [],
                version="1.0",
                is_system=False,
                is_active=True,
                is_public=False,
                created_by=user_id
            )
            
            self.db.add(agent)
            self.db.commit()
            self.db.refresh(agent)
            
            # Create initial version
            self._create_version(
                agent_id=agent.id,
                version="1.0",
                system_prompt=system_prompt,
                settings={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "tone": tone
                },
                change_summary="Initial creation",
                changed_by=user_id
            )
            
            print(f"✅ Created custom agent '{name}' for user {user_id}")
            return agent
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error creating agent: {e}")
            return None
    
    def update_agent(
        self,
        agent_id: int,
        user_id: int,
        **updates
    ) -> Optional[Agent]:
        """
        Update an existing agent (custom agents only)
        """
        try:
            agent = self.get_agent_by_id(agent_id)
            
            if not agent:
                print(f"❌ Agent {agent_id} not found")
                return None
            
            # Only allow updating custom agents by their creator
            if agent.is_system or agent.created_by != user_id:
                print(f"❌ Cannot update agent {agent_id} - not authorized")
                return None
            
            # Track if system_prompt or settings changed (for versioning)
            prompt_changed = "system_prompt" in updates and updates["system_prompt"] != agent.system_prompt
            settings_changed = any(k in updates for k in ["temperature", "max_tokens", "tone"])
            
            # Apply updates
            for key, value in updates.items():
                if hasattr(agent, key):
                    setattr(agent, key, value)
            
            # Increment version if significant changes
            if prompt_changed or settings_changed:
                old_version = agent.version
                major, minor = map(int, old_version.split("."))
                agent.version = f"{major}.{minor + 1}"
                
                # Create new version record
                self._create_version(
                    agent_id=agent.id,
                    version=agent.version,
                    system_prompt=agent.system_prompt,
                    settings={
                        "temperature": agent.temperature,
                        "max_tokens": agent.max_tokens,
                        "tone": agent.tone
                    },
                    change_summary=updates.get("change_summary", "Updated agent configuration"),
                    changed_by=user_id
                )
            
            self.db.commit()
            self.db.refresh(agent)
            
            print(f"✅ Updated agent {agent_id}")
            return agent
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error updating agent: {e}")
            return None
    
    def delete_agent(self, agent_id: int, user_id: int) -> bool:
        """
        Delete a custom agent (system agents cannot be deleted)
        """
        try:
            agent = self.get_agent_by_id(agent_id)
            
            if not agent:
                print(f"❌ Agent {agent_id} not found")
                return False
            
            # Only allow deleting custom agents by their creator
            if agent.is_system or agent.created_by != user_id:
                print(f"❌ Cannot delete agent {agent_id} - not authorized")
                return False
            
            self.db.delete(agent)
            self.db.commit()
            
            print(f"✅ Deleted agent {agent_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error deleting agent: {e}")
            return False
    
    def start_agent_session(
        self,
        agent_id: int,
        conversation_id: int,
        user_id: int
    ) -> Optional[AgentSession]:
        """
        Start a new agent session for a conversation
        """
        try:
            session = AgentSession(
                agent_id=agent_id,
                conversation_id=conversation_id,
                user_id=user_id,
                message_count=0
            )
            
            self.db.add(session)
            
            # Increment agent usage count
            agent = self.get_agent_by_id(agent_id)
            if agent:
                agent.usage_count += 1
            
            self.db.commit()
            self.db.refresh(session)
            
            return session
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error starting agent session: {e}")
            return None
    
    def end_agent_session(
        self,
        session_id: int,
        rating: Optional[int] = None,
        feedback: Optional[str] = None
    ) -> bool:
        """
        End an agent session and optionally collect feedback
        """
        try:
            session = self.db.query(AgentSession).filter(
                AgentSession.id == session_id
            ).first()
            
            if not session:
                return False
            
            session.ended_at = datetime.utcnow()
            
            if rating is not None:
                session.rating = rating
            
            if feedback:
                session.feedback = feedback
            
            # Update agent average rating
            if rating is not None:
                agent = self.get_agent_by_id(session.agent_id)
                if agent:
                    # Simple moving average
                    total_rated = self.db.query(AgentSession).filter(
                        AgentSession.agent_id == agent.id,
                        AgentSession.rating.isnot(None)
                    ).count()
                    
                    avg_rating = self.db.query(AgentSession).filter(
                        AgentSession.agent_id == agent.id,
                        AgentSession.rating.isnot(None)
                    ).with_entities(
                        func.avg(AgentSession.rating)
                    ).scalar()
                    
                    agent.rating = float(avg_rating) if avg_rating else 0.0
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            print(f"❌ Error ending agent session: {e}")
            return False
    
    def get_agent_stats(self, agent_id: int) -> Dict:
        """
        Get statistics for an agent
        """
        agent = self.get_agent_by_id(agent_id)
        
        if not agent:
            return {}
        
        sessions = self.db.query(AgentSession).filter(
            AgentSession.agent_id == agent_id
        ).all()
        
        total_sessions = len(sessions)
        total_messages = sum(s.message_count for s in sessions)
        rated_sessions = [s for s in sessions if s.rating is not None]
        avg_rating = sum(s.rating for s in rated_sessions) / len(rated_sessions) if rated_sessions else 0.0
        
        return {
            "agent_id": agent_id,
            "name": agent.name,
            "total_sessions": total_sessions,
            "total_messages": total_messages,
            "average_rating": round(avg_rating, 2),
            "rating_count": len(rated_sessions),
            "usage_count": agent.usage_count
        }
    
    def _create_version(
        self,
        agent_id: int,
        version: str,
        system_prompt: str,
        settings: Dict,
        change_summary: str,
        changed_by: int
    ) -> AgentVersion:
        """
        Internal: Create a version record for an agent
        """
        version_record = AgentVersion(
            agent_id=agent_id,
            version=version,
            system_prompt=system_prompt,
            settings=settings,
            change_summary=change_summary,
            changed_by=changed_by
        )
        
        self.db.add(version_record)
        return version_record
    
    def get_agent_versions(self, agent_id: int) -> List[AgentVersion]:
        """
        Get all versions of an agent
        """
        return self.db.query(AgentVersion).filter(
            AgentVersion.agent_id == agent_id
        ).order_by(AgentVersion.created_at.desc()).all()
    
    def get_categories(self) -> List[Dict]:
        """
        Get all agent categories with counts
        """
        results = self.db.query(
            Agent.category,
            func.count(Agent.id).label('count')
        ).filter(
            Agent.is_active == True
        ).group_by(Agent.category).all()
        
        return [
            {"category": cat, "count": count}
            for cat, count in results
        ]


def get_agent_manager(db: Session) -> AgentManager:
    """Get agent manager instance"""
    return AgentManager(db)

