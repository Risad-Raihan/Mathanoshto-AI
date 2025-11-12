"""
Conversation Suggestions Engine
Generates continuation suggestions, follow-up questions, and smart prompts
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from datetime import datetime, timedelta

from backend.database.models import Message, Conversation
from backend.database.conversation_insights_models import ConversationSuggestion
from backend.database.operations import get_db
from sqlalchemy.orm import Session


@dataclass
class Suggestion:
    """A single suggestion"""
    text: str
    category: str  # clarification, expansion, related, deep-dive, next-step
    relevance_score: float
    priority: str  # low, medium, high
    reason: str


class ConversationSuggestionEngine:
    """
    Generates intelligent conversation continuation suggestions
    Analyzes context and intent to suggest relevant follow-ups
    """
    
    def __init__(self, llm_provider=None, model: str = None):
        """
        Initialize suggestion engine
        
        Args:
            llm_provider: LLM provider instance (optional, for AI-powered suggestions)
            model: Model name to use for generation
        """
        self.llm_provider = llm_provider
        self.model = model
    
    def generate_suggestions(
        self,
        messages: List[Message],
        conversation_id: int,
        user_id: int,
        num_suggestions: int = 5,
        use_ai: bool = False
    ) -> List[Suggestion]:
        """
        Generate conversation continuation suggestions
        
        Args:
            messages: List of messages in conversation
            conversation_id: Conversation ID
            user_id: User ID
            num_suggestions: Number of suggestions to generate
            use_ai: Whether to use AI for generation
        
        Returns:
            List of Suggestion objects
        """
        if not messages:
            return self._default_suggestions()
        
        # Analyze conversation context
        context = self._analyze_context(messages)
        
        if use_ai and self.llm_provider:
            suggestions = self._ai_generate_suggestions(messages, context, num_suggestions)
        else:
            suggestions = self._rule_based_suggestions(messages, context, num_suggestions)
        
        return suggestions[:num_suggestions]
    
    def _analyze_context(self, messages: List[Message]) -> Dict:
        """
        Analyze conversation context
        
        Args:
            messages: List of messages
        
        Returns:
            Context dictionary with analysis
        """
        # Get last N messages for context
        recent_messages = messages[-5:] if len(messages) > 5 else messages
        
        # Determine conversation type
        conv_type = self._determine_conversation_type(messages)
        
        # Check if conversation seems complete
        is_complete = self._is_conversation_complete(messages)
        
        # Extract main topics
        topics = self._extract_topics(messages)
        
        # Get last user question
        last_user_msg = next((m for m in reversed(messages) if m.role == 'user'), None)
        last_assistant_msg = next((m for m in reversed(messages) if m.role == 'assistant'), None)
        
        # Check for incomplete topics
        has_unanswered_questions = self._has_unanswered_questions(messages)
        
        return {
            'conv_type': conv_type,
            'is_complete': is_complete,
            'topics': topics,
            'last_user_msg': last_user_msg,
            'last_assistant_msg': last_assistant_msg,
            'recent_messages': recent_messages,
            'has_unanswered': has_unanswered_questions,
            'message_count': len(messages)
        }
    
    def _rule_based_suggestions(
        self,
        messages: List[Message],
        context: Dict,
        num_suggestions: int
    ) -> List[Suggestion]:
        """
        Generate suggestions using rule-based approach
        
        Args:
            messages: List of messages
            context: Context analysis
            num_suggestions: Number to generate
        
        Returns:
            List of suggestions
        """
        suggestions = []
        
        # Strategy 1: Clarification questions if last answer was complex
        if context['last_assistant_msg']:
            clarification = self._generate_clarification_suggestions(
                context['last_assistant_msg']
            )
            suggestions.extend(clarification)
        
        # Strategy 2: Expansion suggestions based on topics
        if context['topics']:
            expansion = self._generate_expansion_suggestions(context['topics'])
            suggestions.extend(expansion)
        
        # Strategy 3: Deep-dive into specific aspects
        deep_dive = self._generate_deep_dive_suggestions(messages)
        suggestions.extend(deep_dive)
        
        # Strategy 4: Related topics
        related = self._generate_related_suggestions(context['topics'])
        suggestions.extend(related)
        
        # Strategy 5: Next steps if actionable conversation
        if context['conv_type'] in ['problem-solving', 'implementation']:
            next_steps = self._generate_next_step_suggestions(messages)
            suggestions.extend(next_steps)
        
        # Strategy 6: If conversation seems complete, suggest new directions
        if context['is_complete']:
            new_directions = self._generate_new_direction_suggestions(context['topics'])
            suggestions.extend(new_directions)
        
        # Sort by relevance and priority
        suggestions.sort(key=lambda s: (
            {'high': 3, 'medium': 2, 'low': 1}[s.priority],
            s.relevance_score
        ), reverse=True)
        
        return suggestions
    
    def _determine_conversation_type(self, messages: List[Message]) -> str:
        """Determine the type of conversation"""
        all_text = ' '.join(m.content.lower() for m in messages if m.role in ['user', 'assistant'])
        
        # Patterns for different conversation types
        patterns = {
            'problem-solving': [
                'problem', 'issue', 'error', 'fix', 'solve', 'debug', 'troubleshoot'
            ],
            'implementation': [
                'implement', 'build', 'create', 'develop', 'code', 'setup', 'configure'
            ],
            'exploratory': [
                'how', 'why', 'what', 'explain', 'understand', 'learn', 'tell me about'
            ],
            'informational': [
                'what is', 'define', 'definition', 'information', 'details'
            ],
            'creative': [
                'idea', 'brainstorm', 'suggest', 'design', 'plan', 'strategy'
            ]
        }
        
        # Count matches for each type
        scores = {}
        for conv_type, keywords in patterns.items():
            score = sum(1 for kw in keywords if kw in all_text)
            scores[conv_type] = score
        
        # Return type with highest score, default to exploratory
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        return 'exploratory'
    
    def _is_conversation_complete(self, messages: List[Message]) -> bool:
        """Check if conversation seems complete"""
        if len(messages) < 2:
            return False
        
        last_assistant = next((m for m in reversed(messages) if m.role == 'assistant'), None)
        if not last_assistant:
            return False
        
        # Check for completion indicators
        completion_indicators = [
            r'\b(?:hope this helps|you\'re welcome|glad to help|happy to assist)\b',
            r'\b(?:let me know if|feel free to|don\'t hesitate)\b',
            r'\b(?:is there anything else|anything else I can help)\b',
            r'\b(?:that\'s it|that should do it|that covers it)\b'
        ]
        
        content_lower = last_assistant.content.lower()
        return any(re.search(pattern, content_lower) for pattern in completion_indicators)
    
    def _extract_topics(self, messages: List[Message]) -> List[str]:
        """Extract main topics from conversation"""
        topics = []
        
        # Simple topic extraction from user messages
        for msg in messages:
            if msg.role == 'user':
                # Extract noun phrases (simplified)
                words = msg.content.lower().split()
                # Look for capitalized words or technical terms
                for i, word in enumerate(words):
                    if len(word) > 4 and (word.istitle() or '_' in word or word.isupper()):
                        topics.append(word)
        
        # Deduplicate and limit
        topics = list(dict.fromkeys(topics))[:5]
        return topics
    
    def _has_unanswered_questions(self, messages: List[Message]) -> bool:
        """Check if there are unanswered questions"""
        if not messages:
            return False
        
        last_msg = messages[-1]
        return last_msg.role == 'user' and '?' in last_msg.content
    
    def _generate_clarification_suggestions(self, last_assistant_msg: Message) -> List[Suggestion]:
        """Generate clarification suggestions based on last assistant message"""
        suggestions = []
        content = last_assistant_msg.content
        
        # If message is long or complex, suggest clarifications
        if len(content) > 300:
            suggestions.append(Suggestion(
                text="Can you elaborate on that in simpler terms?",
                category="clarification",
                relevance_score=0.8,
                priority="high",
                reason="Last response was detailed, user might need clarification"
            ))
            
            suggestions.append(Suggestion(
                text="Can you give me a specific example of that?",
                category="clarification",
                relevance_score=0.75,
                priority="medium",
                reason="Examples help understand complex explanations"
            ))
        
        # If message contains code or technical terms
        if '```' in content or any(term in content.lower() for term in ['api', 'function', 'class', 'method']):
            suggestions.append(Suggestion(
                text="How would I implement this in practice?",
                category="clarification",
                relevance_score=0.85,
                priority="high",
                reason="Technical content suggests need for practical guidance"
            ))
        
        return suggestions
    
    def _generate_expansion_suggestions(self, topics: List[str]) -> List[Suggestion]:
        """Generate expansion suggestions based on topics"""
        suggestions = []
        
        for topic in topics[:2]:  # Focus on top 2 topics
            suggestions.append(Suggestion(
                text=f"Tell me more about {topic}",
                category="expansion",
                relevance_score=0.7,
                priority="medium",
                reason=f"User might want to explore '{topic}' further"
            ))
            
            suggestions.append(Suggestion(
                text=f"What are the best practices for {topic}?",
                category="expansion",
                relevance_score=0.75,
                priority="medium",
                reason=f"Best practices are commonly sought for '{topic}'"
            ))
        
        return suggestions
    
    def _generate_deep_dive_suggestions(self, messages: List[Message]) -> List[Suggestion]:
        """Generate deep-dive suggestions"""
        suggestions = []
        
        # Check last assistant message for aspects to deep-dive
        last_assistant = next((m for m in reversed(messages) if m.role == 'assistant'), None)
        
        if last_assistant:
            # Look for numbered lists or bullet points
            if re.search(r'[\d\-\*\•]', last_assistant.content):
                suggestions.append(Suggestion(
                    text="Can you explain the first point in more detail?",
                    category="deep-dive",
                    relevance_score=0.8,
                    priority="medium",
                    reason="Response contained multiple points worth exploring"
                ))
            
            # Look for technical terms or concepts
            if any(word in last_assistant.content.lower() for word in ['algorithm', 'architecture', 'design', 'pattern', 'system']):
                suggestions.append(Suggestion(
                    text="What are the trade-offs and considerations here?",
                    category="deep-dive",
                    relevance_score=0.85,
                    priority="high",
                    reason="Technical discussion suggests need for deeper analysis"
                ))
        
        return suggestions
    
    def _generate_related_suggestions(self, topics: List[str]) -> List[Suggestion]:
        """Generate suggestions for related topics"""
        suggestions = []
        
        # Common related topic patterns
        if topics:
            suggestions.append(Suggestion(
                text="What are some common pitfalls to avoid?",
                category="related",
                relevance_score=0.7,
                priority="medium",
                reason="Understanding pitfalls helps avoid mistakes"
            ))
            
            suggestions.append(Suggestion(
                text="Are there any alternatives or better approaches?",
                category="related",
                relevance_score=0.75,
                priority="medium",
                reason="Exploring alternatives provides broader perspective"
            ))
        
        return suggestions
    
    def _generate_next_step_suggestions(self, messages: List[Message]) -> List[Suggestion]:
        """Generate next-step suggestions for actionable conversations"""
        suggestions = []
        
        suggestions.append(Suggestion(
            text="What should I do first to get started?",
            category="next-step",
            relevance_score=0.9,
            priority="high",
            reason="Actionable conversation needs clear next steps"
        ))
        
        suggestions.append(Suggestion(
            text="What tools or resources do I need for this?",
            category="next-step",
            relevance_score=0.85,
            priority="high",
            reason="Implementation requires proper tools and resources"
        ))
        
        suggestions.append(Suggestion(
            text="How long would this typically take to implement?",
            category="next-step",
            relevance_score=0.75,
            priority="medium",
            reason="Time estimation helps with planning"
        ))
        
        return suggestions
    
    def _generate_new_direction_suggestions(self, topics: List[str]) -> List[Suggestion]:
        """Generate suggestions for new conversation directions"""
        suggestions = []
        
        suggestions.append(Suggestion(
            text="What else can I learn about this topic?",
            category="new-direction",
            relevance_score=0.6,
            priority="low",
            reason="Conversation appears complete, suggesting new exploration"
        ))
        
        if topics:
            suggestions.append(Suggestion(
                text=f"How does this relate to real-world applications?",
                category="new-direction",
                relevance_score=0.65,
                priority="low",
                reason="Connecting theory to practice is valuable"
            ))
        
        return suggestions
    
    def _default_suggestions(self) -> List[Suggestion]:
        """Return default suggestions for empty conversations"""
        return [
            Suggestion(
                text="What can you help me with?",
                category="general",
                relevance_score=0.5,
                priority="medium",
                reason="Starting a new conversation"
            ),
            Suggestion(
                text="I need help with...",
                category="general",
                relevance_score=0.5,
                priority="medium",
                reason="General help request"
            ),
            Suggestion(
                text="Can you explain...",
                category="general",
                relevance_score=0.5,
                priority="medium",
                reason="Seeking explanation"
            )
        ]
    
    def _ai_generate_suggestions(
        self,
        messages: List[Message],
        context: Dict,
        num_suggestions: int
    ) -> List[Suggestion]:
        """
        Use AI to generate suggestions (placeholder for future AI integration)
        
        Args:
            messages: List of messages
            context: Context analysis
            num_suggestions: Number to generate
        
        Returns:
            List of suggestions
        """
        # TODO: Integrate with LLM provider
        # For now, fall back to rule-based
        return self._rule_based_suggestions(messages, context, num_suggestions)
    
    def save_suggestions(
        self,
        conversation_id: int,
        user_id: int,
        suggestions: List[Suggestion],
        context_message_ids: List[int],
        db: Optional[Session] = None
    ) -> List[ConversationSuggestion]:
        """
        Save suggestions to database
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            suggestions: List of suggestions to save
            context_message_ids: IDs of messages used for context
            db: Database session (optional)
        
        Returns:
            List of ConversationSuggestion models
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            # Mark old suggestions as expired
            old_suggestions = db.query(ConversationSuggestion).filter(
                ConversationSuggestion.conversation_id == conversation_id,
                ConversationSuggestion.was_used == False,
                ConversationSuggestion.expires_at == None
            ).all()
            
            for old_sug in old_suggestions:
                old_sug.expires_at = datetime.utcnow()
            
            # Save new suggestions
            saved_suggestions = []
            for rank, suggestion in enumerate(suggestions, 1):
                db_suggestion = ConversationSuggestion(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    suggestion_type='continuation',
                    suggestion_text=suggestion.text,
                    suggestion_category=suggestion.category,
                    context_messages=context_message_ids,
                    relevance_score=suggestion.relevance_score,
                    rank=rank,
                    priority=suggestion.priority,
                    generation_reason=suggestion.reason,
                    expires_at=datetime.utcnow() + timedelta(hours=24)
                )
                db.add(db_suggestion)
                saved_suggestions.append(db_suggestion)
            
            db.commit()
            
            # Refresh all
            for sug in saved_suggestions:
                db.refresh(sug)
            
            return saved_suggestions
            
        finally:
            if should_close:
                db.close()


# Convenience functions
def generate_conversation_suggestions(
    conversation_id: int,
    user_id: int,
    num_suggestions: int = 5,
    use_ai: bool = False
) -> List[ConversationSuggestion]:
    """
    Generate and save conversation suggestions
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID
        num_suggestions: Number of suggestions
        use_ai: Use AI for generation
    
    Returns:
        List of ConversationSuggestion models
    """
    from backend.database.operations import MessageDB
    
    # Get messages
    messages = MessageDB.get_messages(conversation_id)
    
    if not messages:
        return []
    
    # Create engine
    engine = ConversationSuggestionEngine()
    
    # Generate suggestions
    suggestions = engine.generate_suggestions(
        messages=messages,
        conversation_id=conversation_id,
        user_id=user_id,
        num_suggestions=num_suggestions,
        use_ai=use_ai
    )
    
    # Save to database
    context_message_ids = [m.id for m in messages[-5:]]
    return engine.save_suggestions(
        conversation_id,
        user_id,
        suggestions,
        context_message_ids
    )


def get_active_suggestions(conversation_id: int) -> List[ConversationSuggestion]:
    """
    Get active (non-expired, non-used) suggestions
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        List of active suggestions
    """
    db = get_db()
    try:
        now = datetime.utcnow()
        return db.query(ConversationSuggestion).filter(
            ConversationSuggestion.conversation_id == conversation_id,
            ConversationSuggestion.was_used == False,
            (ConversationSuggestion.expires_at == None) | (ConversationSuggestion.expires_at > now)
        ).order_by(ConversationSuggestion.rank).all()
    finally:
        db.close()

