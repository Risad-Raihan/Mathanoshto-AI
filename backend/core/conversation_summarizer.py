"""
Conversation Summarization System
Generates multi-level summaries with key insights extraction
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

from backend.database.models import Message, Conversation
from backend.database.conversation_insights_models import ConversationSummary
from backend.database.operations import get_db
from sqlalchemy.orm import Session


@dataclass
class SummaryResult:
    """Result of summarization"""
    short_summary: str
    medium_summary: str
    detailed_summary: str
    key_points: List[str]
    decisions_made: List[str]
    action_items: List[str]
    questions_asked: List[str]
    confidence_score: float
    message_count: int


class ConversationSummarizer:
    """
    Generates intelligent summaries of conversations
    Multi-level summaries with key information extraction
    """
    
    def __init__(self, llm_provider=None, model: str = None):
        """
        Initialize summarizer
        
        Args:
            llm_provider: LLM provider instance (optional, for AI-powered summaries)
            model: Model name to use for generation
        """
        self.llm_provider = llm_provider
        self.model = model
    
    def summarize_conversation(
        self,
        messages: List[Message],
        conversation_id: int,
        user_id: int,
        use_ai: bool = True
    ) -> SummaryResult:
        """
        Summarize a conversation
        
        Args:
            messages: List of messages in conversation
            conversation_id: Conversation ID
            user_id: User ID
            use_ai: Whether to use AI for summarization
        
        Returns:
            SummaryResult with multi-level summaries
        """
        if not messages:
            return self._empty_summary()
        
        # Extract conversation text
        conversation_text = self._format_conversation(messages)
        
        if use_ai and self.llm_provider:
            return self._ai_summarize(messages, conversation_text)
        else:
            return self._rule_based_summarize(messages, conversation_text)
    
    def _ai_summarize(
        self,
        messages: List[Message],
        conversation_text: str
    ) -> SummaryResult:
        """
        Use AI to generate comprehensive summary
        
        Args:
            messages: List of messages
            conversation_text: Formatted conversation
        
        Returns:
            SummaryResult
        """
        # Build prompt for AI summarization
        prompt = self._build_summarization_prompt(conversation_text)
        
        try:
            # Call LLM (this would integrate with your existing LLM system)
            # For now, we'll use rule-based as fallback
            # TODO: Integrate with actual LLM provider
            return self._rule_based_summarize(messages, conversation_text)
        except Exception as e:
            print(f"AI summarization failed: {e}, falling back to rule-based")
            return self._rule_based_summarize(messages, conversation_text)
    
    def _rule_based_summarize(
        self,
        messages: List[Message],
        conversation_text: str
    ) -> SummaryResult:
        """
        Generate summary using rule-based extraction
        
        Args:
            messages: List of messages
            conversation_text: Formatted conversation
        
        Returns:
            SummaryResult
        """
        # Extract components
        key_points = self._extract_key_points(messages)
        decisions = self._extract_decisions(messages)
        action_items = self._extract_action_items(messages)
        questions = self._extract_questions(messages)
        
        # Generate summaries at different levels
        short_summary = self._generate_short_summary(messages, key_points)
        medium_summary = self._generate_medium_summary(messages, key_points, decisions)
        detailed_summary = self._generate_detailed_summary(
            messages, key_points, decisions, action_items, questions
        )
        
        return SummaryResult(
            short_summary=short_summary,
            medium_summary=medium_summary,
            detailed_summary=detailed_summary,
            key_points=key_points,
            decisions_made=decisions,
            action_items=action_items,
            questions_asked=questions,
            confidence_score=0.75,  # Rule-based has medium confidence
            message_count=len(messages)
        )
    
    def _format_conversation(self, messages: List[Message]) -> str:
        """Format conversation for processing"""
        formatted = []
        for msg in messages:
            if msg.role in ['user', 'assistant']:
                role = "User" if msg.role == "user" else "Assistant"
                formatted.append(f"{role}: {msg.content}")
        return "\n\n".join(formatted)
    
    def _extract_key_points(self, messages: List[Message]) -> List[str]:
        """Extract key points from conversation"""
        key_points = []
        
        # Look for important markers
        important_markers = [
            r'\bimportant\b',
            r'\bkey point\b',
            r'\bmain.*(?:idea|point|topic)\b',
            r'\bcrucial\b',
            r'\bessential\b',
            r'\bsignificant\b'
        ]
        
        for msg in messages:
            if msg.role == 'assistant':
                content = msg.content.lower()
                
                # Check for importance markers
                for marker in important_markers:
                    if re.search(marker, content):
                        # Extract sentence containing the marker
                        sentences = self._split_sentences(msg.content)
                        for sent in sentences:
                            if re.search(marker, sent.lower()):
                                key_points.append(sent.strip())
                                break
                
                # Also extract first sentence of longer assistant messages
                if len(msg.content) > 200 and not key_points:
                    sentences = self._split_sentences(msg.content)
                    if sentences:
                        key_points.append(sentences[0].strip())
        
        # Deduplicate and limit
        key_points = list(dict.fromkeys(key_points))[:5]
        return key_points
    
    def _extract_decisions(self, messages: List[Message]) -> List[str]:
        """Extract decisions made during conversation"""
        decisions = []
        
        decision_patterns = [
            r"(?:decided|decided to|decision|chose to|will|going to|agreed to)\s+(.{10,100})",
            r"(?:let's|we'll|we will|we should)\s+(.{10,100})",
            r"(?:final decision|conclusion|determined that)\s*:?\s*(.{10,100})"
        ]
        
        for msg in messages:
            content = msg.content
            for pattern in decision_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    decision_text = match.group(1).strip()
                    # Clean up and truncate
                    decision_text = re.split(r'[.!?]', decision_text)[0]
                    if len(decision_text) > 15:
                        decisions.append(decision_text)
        
        # Deduplicate and limit
        decisions = list(dict.fromkeys(decisions))[:5]
        return decisions
    
    def _extract_action_items(self, messages: List[Message]) -> List[str]:
        """Extract action items and tasks"""
        action_items = []
        
        action_patterns = [
            r"(?:need to|should|must|have to|action|task|todo|to-do)\s*:?\s*(.{10,100})",
            r"(?:next steps?|follow[- ]?up)\s*:?\s*(.{10,100})",
            r"(?:\[\s*\]|\[ \])\s*(.{10,100})"  # Checkbox pattern
        ]
        
        for msg in messages:
            content = msg.content
            for pattern in action_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    action_text = match.group(1).strip()
                    # Clean up
                    action_text = re.split(r'[.!?]', action_text)[0]
                    if len(action_text) > 10:
                        action_items.append(action_text)
        
        # Deduplicate and limit
        action_items = list(dict.fromkeys(action_items))[:7]
        return action_items
    
    def _extract_questions(self, messages: List[Message]) -> List[str]:
        """Extract important questions asked"""
        questions = []
        
        for msg in messages:
            if msg.role == 'user':
                # Find questions (sentences ending with ?)
                content = msg.content
                potential_questions = re.findall(r'[^.!?]*\?', content)
                
                for q in potential_questions:
                    q = q.strip()
                    if len(q) > 10 and len(q) < 200:
                        questions.append(q)
        
        # Limit to most recent/important questions
        questions = questions[:5]
        return questions
    
    def _generate_short_summary(
        self,
        messages: List[Message],
        key_points: List[str]
    ) -> str:
        """Generate 1-2 sentence summary"""
        if not messages:
            return "Empty conversation"
        
        # Get first user message as topic indicator
        first_user_msg = next((m for m in messages if m.role == 'user'), None)
        
        if first_user_msg:
            first_content = first_user_msg.content[:100]
            msg_count = len(messages)
            user_msg_count = sum(1 for m in messages if m.role == 'user')
            
            # Generate concise summary
            if key_points:
                return f"Conversation about {first_content}... ({msg_count} messages exchanged covering {len(key_points)} key topics)"
            else:
                return f"Conversation with {user_msg_count} user queries and {msg_count - user_msg_count} responses"
        
        return f"Conversation with {len(messages)} messages"
    
    def _generate_medium_summary(
        self,
        messages: List[Message],
        key_points: List[str],
        decisions: List[str]
    ) -> str:
        """Generate paragraph-length summary"""
        summary_parts = []
        
        # Get conversation topic from first messages
        first_user_msg = next((m for m in messages if m.role == 'user'), None)
        if first_user_msg:
            topic = first_user_msg.content[:150]
            summary_parts.append(f"This conversation discusses {topic}...")
        
        # Add key points
        if key_points:
            summary_parts.append(f"Main topics covered include: {', '.join(key_points[:3])}")
        
        # Add decisions if any
        if decisions:
            summary_parts.append(f"Key decisions: {decisions[0]}")
        
        # Add message statistics
        msg_count = len(messages)
        user_count = sum(1 for m in messages if m.role == 'user')
        summary_parts.append(f"The conversation consisted of {user_count} user messages and {msg_count - user_count} assistant responses")
        
        return ". ".join(summary_parts) + "."
    
    def _generate_detailed_summary(
        self,
        messages: List[Message],
        key_points: List[str],
        decisions: List[str],
        action_items: List[str],
        questions: List[str]
    ) -> str:
        """Generate comprehensive detailed summary"""
        sections = []
        
        # Overview
        first_user_msg = next((m for m in messages if m.role == 'user'), None)
        if first_user_msg:
            sections.append(f"**Overview:**\n{first_user_msg.content[:200]}...")
        
        # Key Points
        if key_points:
            sections.append("**Key Points:**\n" + "\n".join(f"- {kp}" for kp in key_points))
        
        # Decisions
        if decisions:
            sections.append("**Decisions Made:**\n" + "\n".join(f"- {d}" for d in decisions))
        
        # Action Items
        if action_items:
            sections.append("**Action Items:**\n" + "\n".join(f"- {ai}" for ai in action_items))
        
        # Questions Discussed
        if questions:
            sections.append("**Questions Addressed:**\n" + "\n".join(f"- {q}" for q in questions[:3]))
        
        # Statistics
        msg_count = len(messages)
        user_count = sum(1 for m in messages if m.role == 'user')
        total_chars = sum(len(m.content) for m in messages)
        sections.append(f"\n**Statistics:**\n- Total messages: {msg_count}\n- User messages: {user_count}\n- Assistant responses: {msg_count - user_count}\n- Total characters: {total_chars:,}")
        
        return "\n\n".join(sections)
    
    def _build_summarization_prompt(self, conversation_text: str) -> str:
        """Build prompt for AI summarization"""
        return f"""Analyze the following conversation and provide a comprehensive summary.

Conversation:
{conversation_text}

Please provide:
1. A short summary (1-2 sentences)
2. A medium summary (1 paragraph)
3. A detailed summary with key points
4. List of key points discussed
5. Any decisions made
6. Any action items identified
7. Important questions asked

Format your response as JSON."""
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _empty_summary(self) -> SummaryResult:
        """Return empty summary"""
        return SummaryResult(
            short_summary="No conversation to summarize",
            medium_summary="No messages in conversation",
            detailed_summary="No conversation content available",
            key_points=[],
            decisions_made=[],
            action_items=[],
            questions_asked=[],
            confidence_score=0.0,
            message_count=0
        )
    
    def save_summary(
        self,
        conversation_id: int,
        user_id: int,
        summary_result: SummaryResult,
        db: Optional[Session] = None
    ) -> ConversationSummary:
        """
        Save summary to database
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            summary_result: Summary result to save
            db: Database session (optional)
        
        Returns:
            ConversationSummary model
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            # Check if summary already exists
            existing = db.query(ConversationSummary).filter(
                ConversationSummary.conversation_id == conversation_id
            ).first()
            
            if existing:
                # Update existing summary
                existing.short_summary = summary_result.short_summary
                existing.medium_summary = summary_result.medium_summary
                existing.detailed_summary = summary_result.detailed_summary
                existing.key_points = summary_result.key_points
                existing.decisions_made = summary_result.decisions_made
                existing.action_items = summary_result.action_items
                existing.questions_asked = summary_result.questions_asked
                existing.message_count = summary_result.message_count
                existing.confidence_score = summary_result.confidence_score
                existing.updated_at = datetime.utcnow()
                
                summary = existing
            else:
                # Create new summary
                summary = ConversationSummary(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    short_summary=summary_result.short_summary,
                    medium_summary=summary_result.medium_summary,
                    detailed_summary=summary_result.detailed_summary,
                    key_points=summary_result.key_points,
                    decisions_made=summary_result.decisions_made,
                    action_items=summary_result.action_items,
                    questions_asked=summary_result.questions_asked,
                    message_count=summary_result.message_count,
                    confidence_score=summary_result.confidence_score,
                    generation_method='rule_based'
                )
                db.add(summary)
            
            db.commit()
            db.refresh(summary)
            return summary
            
        finally:
            if should_close:
                db.close()


# Convenience functions
def summarize_conversation(
    conversation_id: int,
    user_id: int,
    use_ai: bool = False
) -> Optional[ConversationSummary]:
    """
    Summarize a conversation and save to database
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID
        use_ai: Use AI for summarization
    
    Returns:
        ConversationSummary model
    """
    from backend.database.operations import MessageDB
    
    # Get messages
    messages = MessageDB.get_messages(conversation_id)
    
    if not messages:
        return None
    
    # Create summarizer
    summarizer = ConversationSummarizer()
    
    # Generate summary
    summary_result = summarizer.summarize_conversation(
        messages=messages,
        conversation_id=conversation_id,
        user_id=user_id,
        use_ai=use_ai
    )
    
    # Save to database
    return summarizer.save_summary(conversation_id, user_id, summary_result)


def get_conversation_summary(conversation_id: int) -> Optional[ConversationSummary]:
    """
    Get existing conversation summary
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        ConversationSummary or None
    """
    db = get_db()
    try:
        return db.query(ConversationSummary).filter(
            ConversationSummary.conversation_id == conversation_id
        ).first()
    finally:
        db.close()

