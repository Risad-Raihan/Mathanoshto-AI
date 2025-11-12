"""
Smart Prompt Library & Follow-up Question Generator
Manages reusable prompts and generates contextual follow-up questions
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import re
from datetime import datetime

from backend.database.models import Message, Conversation
from backend.database.conversation_insights_models import UserPromptLibrary, ConversationSuggestion
from backend.database.operations import get_db
from sqlalchemy.orm import Session


@dataclass
class PromptTemplate:
    """A prompt template"""
    title: str
    text: str
    category: str
    tags: List[str]
    complexity: str  # beginner, intermediate, advanced
    agent_type: Optional[str] = None


@dataclass
class FollowUpQuestion:
    """A generated follow-up question"""
    question: str
    intent: str  # clarify, expand, validate, explore, apply
    priority: str  # high, medium, low
    context: str  # Why this question is relevant


class SmartPromptLibrary:
    """
    Manages a library of smart prompts and generates contextual suggestions
    """
    
    # Built-in prompt templates by category
    BUILTIN_PROMPTS = {
        'learning': [
            PromptTemplate(
                title="Explain Concept",
                text="Explain {topic} in simple terms, as if teaching a beginner",
                category="learning",
                tags=["explanation", "teaching", "basics"],
                complexity="beginner"
            ),
            PromptTemplate(
                title="Deep Technical Explanation",
                text="Provide a detailed technical explanation of {topic}, including underlying principles and implementation details",
                category="learning",
                tags=["technical", "deep-dive", "advanced"],
                complexity="advanced"
            ),
            PromptTemplate(
                title="Example-Based Learning",
                text="Teach me {topic} using practical examples and real-world scenarios",
                category="learning",
                tags=["examples", "practical", "hands-on"],
                complexity="intermediate"
            ),
            PromptTemplate(
                title="Compare and Contrast",
                text="Compare {topic_a} and {topic_b}, highlighting their differences, similarities, and use cases",
                category="learning",
                tags=["comparison", "analysis"],
                complexity="intermediate"
            ),
        ],
        'problem-solving': [
            PromptTemplate(
                title="Debug Issue",
                text="Help me debug this issue: {problem_description}. Here's my code/setup: {details}",
                category="problem-solving",
                tags=["debugging", "troubleshooting", "fix"],
                complexity="intermediate"
            ),
            PromptTemplate(
                title="Error Analysis",
                text="I'm getting this error: {error_message}. What does it mean and how can I fix it?",
                category="problem-solving",
                tags=["error", "fix", "solution"],
                complexity="beginner"
            ),
            PromptTemplate(
                title="Optimization Request",
                text="How can I optimize {aspect} in my {system}? Current performance: {metrics}",
                category="problem-solving",
                tags=["optimization", "performance", "improvement"],
                complexity="advanced"
            ),
        ],
        'implementation': [
            PromptTemplate(
                title="Step-by-Step Implementation",
                text="Guide me through implementing {feature} step by step, from scratch",
                category="implementation",
                tags=["tutorial", "guide", "implementation"],
                complexity="beginner"
            ),
            PromptTemplate(
                title="Best Practices Implementation",
                text="Show me how to implement {feature} following industry best practices and design patterns",
                category="implementation",
                tags=["best-practices", "patterns", "professional"],
                complexity="advanced"
            ),
            PromptTemplate(
                title="Code Review",
                text="Review this code for {purpose}: {code}. Suggest improvements and best practices",
                category="implementation",
                tags=["review", "feedback", "improvement"],
                complexity="intermediate"
            ),
        ],
        'planning': [
            PromptTemplate(
                title="Project Architecture",
                text="Help me design the architecture for {project_description}. Consider scalability, maintainability, and best practices",
                category="planning",
                tags=["architecture", "design", "planning"],
                complexity="advanced"
            ),
            PromptTemplate(
                title="Technology Stack Selection",
                text="What technology stack should I use for {project_type}? Consider: {requirements}",
                category="planning",
                tags=["technology", "stack", "selection"],
                complexity="intermediate"
            ),
            PromptTemplate(
                title="Project Roadmap",
                text="Create a development roadmap for {project}. Break it into phases with milestones",
                category="planning",
                tags=["roadmap", "planning", "milestones"],
                complexity="intermediate"
            ),
        ],
        'analysis': [
            PromptTemplate(
                title="Trade-offs Analysis",
                text="Analyze the trade-offs between {option_a} and {option_b} for {use_case}",
                category="analysis",
                tags=["trade-offs", "comparison", "decision"],
                complexity="advanced"
            ),
            PromptTemplate(
                title="Security Review",
                text="Review the security implications of {approach} in {context}",
                category="analysis",
                tags=["security", "review", "vulnerabilities"],
                complexity="advanced"
            ),
            PromptTemplate(
                title="Performance Analysis",
                text="Analyze the performance characteristics of {solution}, including time/space complexity",
                category="analysis",
                tags=["performance", "complexity", "analysis"],
                complexity="advanced"
            ),
        ],
    }
    
    def __init__(self):
        """Initialize prompt library"""
        pass
    
    def get_prompts_by_category(
        self,
        category: str,
        complexity: Optional[str] = None
    ) -> List[PromptTemplate]:
        """
        Get prompts by category
        
        Args:
            category: Prompt category
            complexity: Filter by complexity level
        
        Returns:
            List of PromptTemplate objects
        """
        prompts = self.BUILTIN_PROMPTS.get(category, [])
        
        if complexity:
            prompts = [p for p in prompts if p.complexity == complexity]
        
        return prompts
    
    def get_all_categories(self) -> List[str]:
        """Get all available prompt categories"""
        return list(self.BUILTIN_PROMPTS.keys())
    
    def search_prompts(
        self,
        query: str,
        limit: int = 10
    ) -> List[PromptTemplate]:
        """
        Search prompts by query
        
        Args:
            query: Search query
            limit: Max results
        
        Returns:
            List of matching prompts
        """
        query_lower = query.lower()
        results = []
        
        for category, prompts in self.BUILTIN_PROMPTS.items():
            for prompt in prompts:
                # Check if query matches title, text, tags, or category
                if (query_lower in prompt.title.lower() or
                    query_lower in prompt.text.lower() or
                    query_lower in category or
                    any(query_lower in tag.lower() for tag in prompt.tags)):
                    results.append(prompt)
        
        return results[:limit]
    
    def get_contextual_prompts(
        self,
        messages: List[Message],
        limit: int = 5
    ) -> List[PromptTemplate]:
        """
        Get contextually relevant prompts based on conversation
        
        Args:
            messages: Conversation messages
            limit: Max prompts to return
        
        Returns:
            List of relevant prompts
        """
        if not messages:
            # Return general starter prompts
            return self.get_prompts_by_category('learning', 'beginner')[:limit]
        
        # Analyze conversation to determine relevant categories
        all_text = ' '.join(m.content.lower() for m in messages if m.role in ['user', 'assistant'])
        
        # Score categories based on conversation content
        category_scores = {}
        for category in self.get_all_categories():
            score = self._score_category_relevance(all_text, category)
            if score > 0:
                category_scores[category] = score
        
        # Get prompts from top categories
        relevant_prompts = []
        sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
        
        for category, score in sorted_categories:
            category_prompts = self.get_prompts_by_category(category)
            relevant_prompts.extend(category_prompts)
            if len(relevant_prompts) >= limit:
                break
        
        return relevant_prompts[:limit]
    
    def _score_category_relevance(self, text: str, category: str) -> float:
        """Score how relevant a category is to the text"""
        category_keywords = {
            'learning': ['learn', 'understand', 'explain', 'what is', 'how does', 'teach', 'concept'],
            'problem-solving': ['error', 'issue', 'problem', 'debug', 'fix', 'not working', 'fails'],
            'implementation': ['implement', 'build', 'create', 'develop', 'code', 'write', 'setup'],
            'planning': ['design', 'architecture', 'plan', 'strategy', 'approach', 'structure'],
            'analysis': ['analyze', 'compare', 'review', 'evaluate', 'trade-off', 'performance'],
        }
        
        keywords = category_keywords.get(category, [])
        score = sum(1 for kw in keywords if kw in text)
        return score
    
    def save_user_prompt(
        self,
        user_id: int,
        prompt_text: str,
        prompt_title: Optional[str] = None,
        category: Optional[str] = None,
        tags: Optional[List[str]] = None,
        source_conversation_id: Optional[int] = None,
        db: Optional[Session] = None
    ) -> UserPromptLibrary:
        """
        Save a user's custom prompt to their library
        
        Args:
            user_id: User ID
            prompt_text: Prompt text
            prompt_title: Optional title
            category: Optional category
            tags: Optional tags
            source_conversation_id: Source conversation if any
            db: Database session
        
        Returns:
            UserPromptLibrary model
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            user_prompt = UserPromptLibrary(
                user_id=user_id,
                prompt_text=prompt_text,
                prompt_title=prompt_title or f"Custom Prompt {datetime.now().strftime('%Y%m%d')}",
                prompt_category=category,
                tags=tags or [],
                is_custom=True,
                source_conversation_id=source_conversation_id
            )
            db.add(user_prompt)
            db.commit()
            db.refresh(user_prompt)
            return user_prompt
        finally:
            if should_close:
                db.close()
    
    def get_user_prompts(
        self,
        user_id: int,
        category: Optional[str] = None,
        favorites_only: bool = False,
        db: Optional[Session] = None
    ) -> List[UserPromptLibrary]:
        """
        Get user's saved prompts
        
        Args:
            user_id: User ID
            category: Filter by category
            favorites_only: Only return favorites
            db: Database session
        
        Returns:
            List of UserPromptLibrary models
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            query = db.query(UserPromptLibrary).filter(
                UserPromptLibrary.user_id == user_id
            )
            
            if category:
                query = query.filter(UserPromptLibrary.prompt_category == category)
            
            if favorites_only:
                query = query.filter(UserPromptLibrary.is_favorite == True)
            
            return query.order_by(UserPromptLibrary.last_used.desc()).all()
        finally:
            if should_close:
                db.close()


class FollowUpQuestionGenerator:
    """
    Generates intelligent follow-up questions based on conversation context
    """
    
    def __init__(self):
        """Initialize generator"""
        pass
    
    def generate_follow_ups(
        self,
        messages: List[Message],
        num_questions: int = 5
    ) -> List[FollowUpQuestion]:
        """
        Generate follow-up questions
        
        Args:
            messages: Conversation messages
            num_questions: Number of questions to generate
        
        Returns:
            List of FollowUpQuestion objects
        """
        if not messages:
            return []
        
        questions = []
        
        # Strategy 1: Clarification questions
        clarify_questions = self._generate_clarification_questions(messages)
        questions.extend(clarify_questions)
        
        # Strategy 2: Expansion questions
        expand_questions = self._generate_expansion_questions(messages)
        questions.extend(expand_questions)
        
        # Strategy 3: Validation questions
        validate_questions = self._generate_validation_questions(messages)
        questions.extend(validate_questions)
        
        # Strategy 4: Exploration questions
        explore_questions = self._generate_exploration_questions(messages)
        questions.extend(explore_questions)
        
        # Strategy 5: Application questions
        apply_questions = self._generate_application_questions(messages)
        questions.extend(apply_questions)
        
        # Sort by priority
        questions.sort(key=lambda q: {'high': 3, 'medium': 2, 'low': 1}[q.priority], reverse=True)
        
        return questions[:num_questions]
    
    def _generate_clarification_questions(self, messages: List[Message]) -> List[FollowUpQuestion]:
        """Generate clarification questions"""
        questions = []
        last_assistant = next((m for m in reversed(messages) if m.role == 'assistant'), None)
        
        if last_assistant:
            content = last_assistant.content
            
            # If response mentions technical terms
            if any(term in content.lower() for term in ['api', 'algorithm', 'architecture', 'framework']):
                questions.append(FollowUpQuestion(
                    question="Could you break down the technical terminology used?",
                    intent="clarify",
                    priority="high",
                    context="Response contains technical terms that might need clarification"
                ))
            
            # If response lists multiple options
            if re.search(r'(?:\d\.|\-|\•)', content):
                questions.append(FollowUpQuestion(
                    question="Which of these options would you recommend for my specific use case?",
                    intent="clarify",
                    priority="high",
                    context="Multiple options presented, need guidance on selection"
                ))
            
            # If response is long
            if len(content) > 500:
                questions.append(FollowUpQuestion(
                    question="Can you summarize the key takeaways?",
                    intent="clarify",
                    priority="medium",
                    context="Long response might benefit from summary"
                ))
        
        return questions
    
    def _generate_expansion_questions(self, messages: List[Message]) -> List[FollowUpQuestion]:
        """Generate expansion questions"""
        questions = []
        last_assistant = next((m for m in reversed(messages) if m.role == 'assistant'), None)
        
        if last_assistant:
            # Always valuable to go deeper
            questions.append(FollowUpQuestion(
                question="Can you provide a more detailed example of this in action?",
                intent="expand",
                priority="high",
                context="Examples help solidify understanding"
            ))
            
            questions.append(FollowUpQuestion(
                question="What are the advanced considerations I should know about?",
                intent="expand",
                priority="medium",
                context="Deeper knowledge often reveals important nuances"
            ))
        
        return questions
    
    def _generate_validation_questions(self, messages: List[Message]) -> List[FollowUpQuestion]:
        """Generate validation questions"""
        questions = []
        
        # Check if user has expressed understanding
        last_user = next((m for m in reversed(messages) if m.role == 'user'), None)
        if last_user and any(phrase in last_user.content.lower() for phrase in ['i think', 'so if i', 'does that mean']):
            questions.append(FollowUpQuestion(
                question="Is my understanding correct?",
                intent="validate",
                priority="high",
                context="User has expressed an interpretation that should be validated"
            ))
        
        questions.append(FollowUpQuestion(
            question="What are common misconceptions about this topic?",
            intent="validate",
            priority="medium",
            context="Identifying misconceptions prevents future errors"
        ))
        
        return questions
    
    def _generate_exploration_questions(self, messages: List[Message]) -> List[FollowUpQuestion]:
        """Generate exploration questions"""
        questions = []
        
        questions.append(FollowUpQuestion(
            question="What related topics should I explore to deepen my knowledge?",
            intent="explore",
            priority="medium",
            context="Exploring related areas provides comprehensive understanding"
        ))
        
        questions.append(FollowUpQuestion(
            question="How does this connect to real-world applications?",
            intent="explore",
            priority="medium",
            context="Real-world context makes concepts more concrete"
        ))
        
        return questions
    
    def _generate_application_questions(self, messages: List[Message]) -> List[FollowUpQuestion]:
        """Generate application questions"""
        questions = []
        
        questions.append(FollowUpQuestion(
            question="What would be a good first project to apply this knowledge?",
            intent="apply",
            priority="high",
            context="Practical application reinforces learning"
        ))
        
        questions.append(FollowUpQuestion(
            question="What tools and resources do I need to get started?",
            intent="apply",
            priority="high",
            context="Practical implementation requires specific tools"
        ))
        
        questions.append(FollowUpQuestion(
            question="What challenges might I face when implementing this?",
            intent="apply",
            priority="medium",
            context="Anticipating challenges helps prepare solutions"
        ))
        
        return questions
    
    def save_as_suggestions(
        self,
        conversation_id: int,
        user_id: int,
        questions: List[FollowUpQuestion],
        context_message_ids: List[int],
        db: Optional[Session] = None
    ) -> List[ConversationSuggestion]:
        """
        Save follow-up questions as conversation suggestions
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            questions: List of follow-up questions
            context_message_ids: Context message IDs
            db: Database session
        
        Returns:
            List of ConversationSuggestion models
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            saved_suggestions = []
            for rank, q in enumerate(questions, 1):
                suggestion = ConversationSuggestion(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    suggestion_type='followup',
                    suggestion_text=q.question,
                    suggestion_category=q.intent,
                    context_messages=context_message_ids,
                    relevance_score={'high': 0.9, 'medium': 0.7, 'low': 0.5}[q.priority],
                    rank=rank,
                    priority=q.priority,
                    generation_reason=q.context
                )
                db.add(suggestion)
                saved_suggestions.append(suggestion)
            
            db.commit()
            
            for sug in saved_suggestions:
                db.refresh(sug)
            
            return saved_suggestions
            
        finally:
            if should_close:
                db.close()


# Convenience functions
def get_smart_prompts(
    category: Optional[str] = None,
    complexity: Optional[str] = None,
    search_query: Optional[str] = None
) -> List[PromptTemplate]:
    """
    Get smart prompts from library
    
    Args:
        category: Filter by category
        complexity: Filter by complexity
        search_query: Search query
    
    Returns:
        List of PromptTemplate objects
    """
    library = SmartPromptLibrary()
    
    if search_query:
        return library.search_prompts(search_query)
    elif category:
        return library.get_prompts_by_category(category, complexity)
    else:
        # Return all prompts
        all_prompts = []
        for cat in library.get_all_categories():
            all_prompts.extend(library.get_prompts_by_category(cat))
        return all_prompts


def generate_follow_up_questions(
    conversation_id: int,
    user_id: int,
    num_questions: int = 5,
    save_to_db: bool = True
) -> List[FollowUpQuestion]:
    """
    Generate and optionally save follow-up questions
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID
        num_questions: Number of questions
        save_to_db: Whether to save to database
    
    Returns:
        List of FollowUpQuestion objects
    """
    from backend.database.operations import MessageDB
    
    messages = MessageDB.get_messages(conversation_id)
    
    if not messages:
        return []
    
    generator = FollowUpQuestionGenerator()
    questions = generator.generate_follow_ups(messages, num_questions)
    
    if save_to_db:
        context_message_ids = [m.id for m in messages[-5:]]
        generator.save_as_suggestions(
            conversation_id,
            user_id,
            questions,
            context_message_ids
        )
    
    return questions

