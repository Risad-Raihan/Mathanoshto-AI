"""
Conversation Insights Analyzer
Extracts topics, entities, and generates analytics dashboard data
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass
from collections import Counter
import re
from datetime import datetime, timedelta

from backend.database.models import Message, Conversation
from backend.database.conversation_insights_models import ConversationInsight
from backend.database.operations import get_db
from sqlalchemy.orm import Session


@dataclass
class TopicScore:
    """A topic with relevance score"""
    topic: str
    score: float
    frequency: int
    context: List[str]  # Sample contexts where topic appears


@dataclass
class Entity:
    """An extracted entity"""
    text: str
    entity_type: str  # person, product, technology, concept, place
    frequency: int
    contexts: List[str]


@dataclass
class InsightsData:
    """Complete insights for a conversation"""
    main_topics: List[TopicScore]
    topic_clusters: Dict[str, List[str]]
    entities: Dict[str, List[Entity]]
    conversation_type: str
    complexity_level: str
    relationships: List[Dict]
    statistics: Dict
    duration_minutes: Optional[int]


class ConversationInsightsAnalyzer:
    """
    Analyzes conversations to extract insights, topics, and entities
    """
    
    # Common technical terms and concepts
    TECHNICAL_TERMS = {
        'programming': ['api', 'function', 'class', 'method', 'algorithm', 'database', 'framework'],
        'data_science': ['model', 'training', 'dataset', 'neural', 'learning', 'prediction'],
        'web_dev': ['frontend', 'backend', 'server', 'client', 'http', 'rest', 'endpoint'],
        'devops': ['docker', 'kubernetes', 'deployment', 'pipeline', 'container'],
        'architecture': ['microservices', 'monolith', 'scalability', 'distributed', 'architecture']
    }
    
    # Entity patterns
    ENTITY_PATTERNS = {
        'technology': [
            'python', 'javascript', 'java', 'react', 'vue', 'angular', 'node', 'django',
            'flask', 'fastapi', 'postgresql', 'mongodb', 'redis', 'aws', 'azure', 'gcp',
            'docker', 'kubernetes', 'tensorflow', 'pytorch', 'pandas', 'numpy'
        ],
        'concept': [
            'machine learning', 'deep learning', 'artificial intelligence', 'neural network',
            'api', 'rest api', 'graphql', 'microservices', 'serverless', 'blockchain',
            'cloud computing', 'devops', 'agile', 'scrum'
        ],
        'product': [
            'chatgpt', 'github', 'gitlab', 'jira', 'confluence', 'slack', 'notion'
        ]
    }
    
    def __init__(self):
        """Initialize insights analyzer"""
        pass
    
    def analyze_conversation(
        self,
        messages: List[Message],
        conversation_id: int,
        user_id: int
    ) -> InsightsData:
        """
        Analyze conversation and extract insights
        
        Args:
            messages: List of messages
            conversation_id: Conversation ID
            user_id: User ID
        
        Returns:
            InsightsData object
        """
        if not messages:
            return self._empty_insights()
        
        # Extract components
        topics = self._extract_topics(messages)
        topic_clusters = self._cluster_topics(topics)
        entities = self._extract_entities(messages)
        conv_type = self._determine_conversation_type(messages)
        complexity = self._assess_complexity(messages)
        relationships = self._extract_relationships(messages, topics, entities)
        statistics = self._calculate_statistics(messages)
        duration = self._calculate_duration(messages)
        
        return InsightsData(
            main_topics=topics,
            topic_clusters=topic_clusters,
            entities=entities,
            conversation_type=conv_type,
            complexity_level=complexity,
            relationships=relationships,
            statistics=statistics,
            duration_minutes=duration
        )
    
    def _extract_topics(self, messages: List[Message]) -> List[TopicScore]:
        """Extract main topics from conversation"""
        # Combine all text
        all_text = ' '.join(m.content for m in messages if m.role in ['user', 'assistant'])
        all_text_lower = all_text.lower()
        
        topic_scores = {}
        
        # Extract noun phrases (simplified - look for capitalized words and technical terms)
        words = re.findall(r'\b[A-Z][a-zA-Z]+\b|\b[a-z_-]+\b', all_text)
        
        # Score words by frequency and context
        word_freq = Counter(w.lower() for w in words if len(w) > 3)
        
        # Filter stop words
        stop_words = {'this', 'that', 'with', 'have', 'from', 'they', 'been', 'were', 'what', 'when', 'where', 'which', 'while', 'would', 'could', 'should'}
        
        for word, freq in word_freq.most_common(30):
            if word in stop_words:
                continue
            
            # Calculate score based on frequency and technical relevance
            score = freq
            
            # Boost if it's a technical term
            for category, terms in self.TECHNICAL_TERMS.items():
                if word in terms:
                    score *= 2
                    break
            
            # Extract contexts
            contexts = self._find_contexts(all_text, word, max_contexts=3)
            
            topic_scores[word] = TopicScore(
                topic=word,
                score=float(score),
                frequency=freq,
                context=contexts
            )
        
        # Sort by score
        sorted_topics = sorted(topic_scores.values(), key=lambda t: t.score, reverse=True)
        
        return sorted_topics[:10]  # Top 10 topics
    
    def _find_contexts(self, text: str, word: str, max_contexts: int = 3) -> List[str]:
        """Find sample contexts where word appears"""
        contexts = []
        sentences = re.split(r'[.!?]+', text)
        
        for sent in sentences:
            if word.lower() in sent.lower() and len(contexts) < max_contexts:
                # Trim to reasonable length
                if len(sent) > 100:
                    # Find word position and extract around it
                    word_pos = sent.lower().find(word.lower())
                    start = max(0, word_pos - 40)
                    end = min(len(sent), word_pos + 60)
                    sent = '...' + sent[start:end] + '...'
                contexts.append(sent.strip())
        
        return contexts
    
    def _cluster_topics(self, topics: List[TopicScore]) -> Dict[str, List[str]]:
        """Cluster related topics together"""
        clusters = {}
        
        # Simple clustering by technical category
        for topic in topics:
            topic_word = topic.topic.lower()
            
            # Check which technical category it belongs to
            assigned = False
            for category, terms in self.TECHNICAL_TERMS.items():
                if topic_word in terms:
                    if category not in clusters:
                        clusters[category] = []
                    clusters[category].append(topic.topic)
                    assigned = True
                    break
            
            # If not assigned to any category, put in 'general'
            if not assigned:
                if 'general' not in clusters:
                    clusters['general'] = []
                clusters['general'].append(topic.topic)
        
        return clusters
    
    def _extract_entities(self, messages: List[Message]) -> Dict[str, List[Entity]]:
        """Extract entities (technologies, products, concepts)"""
        all_text = ' '.join(m.content for m in messages if m.role in ['user', 'assistant'])
        all_text_lower = all_text.lower()
        
        entities_by_type = {}
        
        # Extract known entities
        for entity_type, entity_list in self.ENTITY_PATTERNS.items():
            for entity_text in entity_list:
                # Count occurrences
                freq = all_text_lower.count(entity_text.lower())
                
                if freq > 0:
                    # Find contexts
                    contexts = self._find_contexts(all_text, entity_text, max_contexts=2)
                    
                    entity = Entity(
                        text=entity_text,
                        entity_type=entity_type,
                        frequency=freq,
                        contexts=contexts
                    )
                    
                    if entity_type not in entities_by_type:
                        entities_by_type[entity_type] = []
                    entities_by_type[entity_type].append(entity)
        
        # Sort each type by frequency
        for entity_type in entities_by_type:
            entities_by_type[entity_type].sort(key=lambda e: e.frequency, reverse=True)
        
        return entities_by_type
    
    def _determine_conversation_type(self, messages: List[Message]) -> str:
        """Determine the type of conversation"""
        all_text = ' '.join(m.content.lower() for m in messages if m.role in ['user', 'assistant'])
        
        # Patterns for different types
        type_patterns = {
            'exploratory': ['how', 'why', 'what', 'explain', 'understand', 'learn', 'tell me'],
            'problem-solving': ['error', 'issue', 'problem', 'debug', 'fix', 'not working', 'fails'],
            'implementation': ['implement', 'build', 'create', 'develop', 'code', 'setup', 'configure'],
            'informational': ['what is', 'define', 'definition', 'information', 'details'],
            'creative': ['idea', 'brainstorm', 'suggest', 'design', 'plan', 'strategy'],
            'analytical': ['analyze', 'compare', 'review', 'evaluate', 'trade-off', 'performance']
        }
        
        # Score each type
        type_scores = {}
        for conv_type, patterns in type_patterns.items():
            score = sum(1 for pattern in patterns if pattern in all_text)
            type_scores[conv_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        return 'general'
    
    def _assess_complexity(self, messages: List[Message]) -> str:
        """Assess conversation complexity level"""
        all_text = ' '.join(m.content for m in messages if m.role in ['user', 'assistant'])
        
        # Factors for complexity
        avg_msg_length = sum(len(m.content) for m in messages) / len(messages)
        
        # Count technical terms
        technical_term_count = 0
        for terms in self.TECHNICAL_TERMS.values():
            technical_term_count += sum(1 for term in terms if term in all_text.lower())
        
        # Count code blocks
        code_blocks = all_text.count('```')
        
        # Assess complexity
        if avg_msg_length > 500 or technical_term_count > 10 or code_blocks > 2:
            return 'complex'
        elif avg_msg_length > 200 or technical_term_count > 5 or code_blocks > 0:
            return 'intermediate'
        else:
            return 'simple'
    
    def _extract_relationships(
        self,
        messages: List[Message],
        topics: List[TopicScore],
        entities: Dict[str, List[Entity]]
    ) -> List[Dict]:
        """Extract relationships between topics and entities"""
        relationships = []
        
        # Find topics that appear together in messages
        for i, topic_a in enumerate(topics[:5]):  # Top 5 topics
            for topic_b in topics[i+1:6]:
                # Check if they appear in same messages
                co_occurrence = 0
                for msg in messages:
                    if (topic_a.topic.lower() in msg.content.lower() and
                        topic_b.topic.lower() in msg.content.lower()):
                        co_occurrence += 1
                
                if co_occurrence > 0:
                    relationships.append({
                        'from': topic_a.topic,
                        'to': topic_b.topic,
                        'type': 'co-occurs',
                        'strength': co_occurrence
                    })
        
        # Link topics to entities
        for topic in topics[:5]:
            for entity_type, entity_list in entities.items():
                for entity in entity_list[:3]:  # Top 3 entities per type
                    # Check if topic and entity appear together
                    co_occurrence = 0
                    for msg in messages:
                        if (topic.topic.lower() in msg.content.lower() and
                            entity.text.lower() in msg.content.lower()):
                            co_occurrence += 1
                    
                    if co_occurrence > 0:
                        relationships.append({
                            'from': topic.topic,
                            'to': entity.text,
                            'type': f'uses-{entity_type}',
                            'strength': co_occurrence
                        })
        
        return relationships[:20]  # Limit to top 20 relationships
    
    def _calculate_statistics(self, messages: List[Message]) -> Dict:
        """Calculate conversation statistics"""
        user_messages = [m for m in messages if m.role == 'user']
        assistant_messages = [m for m in messages if m.role == 'assistant']
        
        total_chars = sum(len(m.content) for m in messages)
        
        # Calculate average message lengths
        avg_user_length = (
            sum(len(m.content) for m in user_messages) / len(user_messages)
            if user_messages else 0
        )
        avg_assistant_length = (
            sum(len(m.content) for m in assistant_messages) / len(assistant_messages)
            if assistant_messages else 0
        )
        
        # Count questions
        questions = sum(1 for m in user_messages if '?' in m.content)
        
        # Count code blocks
        code_blocks = sum(m.content.count('```') for m in messages)
        
        return {
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'total_characters': total_chars,
            'avg_message_length': total_chars / len(messages),
            'avg_user_message_length': avg_user_length,
            'avg_assistant_message_length': avg_assistant_length,
            'questions_asked': questions,
            'code_blocks': code_blocks // 2,  # Divide by 2 (opening and closing)
            'engagement_ratio': len(user_messages) / len(messages) if messages else 0
        }
    
    def _calculate_duration(self, messages: List[Message]) -> Optional[int]:
        """Calculate conversation duration in minutes"""
        if len(messages) < 2:
            return None
        
        first_time = messages[0].created_at
        last_time = messages[-1].created_at
        
        if first_time and last_time:
            duration = last_time - first_time
            return int(duration.total_seconds() / 60)
        
        return None
    
    def _empty_insights(self) -> InsightsData:
        """Return empty insights"""
        return InsightsData(
            main_topics=[],
            topic_clusters={},
            entities={},
            conversation_type='general',
            complexity_level='simple',
            relationships=[],
            statistics={},
            duration_minutes=None
        )
    
    def save_insights(
        self,
        conversation_id: int,
        user_id: int,
        insights_data: InsightsData,
        db: Optional[Session] = None
    ) -> ConversationInsight:
        """
        Save insights to database
        
        Args:
            conversation_id: Conversation ID
            user_id: User ID
            insights_data: Insights data to save
            db: Database session
        
        Returns:
            ConversationInsight model
        """
        should_close = False
        if db is None:
            db = get_db()
            should_close = True
        
        try:
            # Check if insights already exist
            existing = db.query(ConversationInsight).filter(
                ConversationInsight.conversation_id == conversation_id
            ).first()
            
            # Prepare topics data
            topics_data = [
                {'topic': t.topic, 'score': t.score, 'frequency': t.frequency}
                for t in insights_data.main_topics
            ]
            
            # Prepare entities data
            entities_data = {
                entity_type: [{'text': e.text, 'frequency': e.frequency} for e in entities]
                for entity_type, entities in insights_data.entities.items()
            }
            
            stats = insights_data.statistics
            
            if existing:
                # Update existing
                existing.main_topics = topics_data
                existing.topic_clusters = insights_data.topic_clusters
                existing.entities = entities_data
                existing.conversation_type = insights_data.conversation_type
                existing.complexity_level = insights_data.complexity_level
                existing.relationships = insights_data.relationships
                existing.total_messages = stats.get('total_messages', 0)
                existing.user_messages = stats.get('user_messages', 0)
                existing.assistant_messages = stats.get('assistant_messages', 0)
                existing.avg_message_length = stats.get('avg_message_length', 0.0)
                existing.conversation_duration_minutes = insights_data.duration_minutes
                existing.updated_at = datetime.utcnow()
                
                insight = existing
            else:
                # Create new
                insight = ConversationInsight(
                    conversation_id=conversation_id,
                    user_id=user_id,
                    main_topics=topics_data,
                    topic_clusters=insights_data.topic_clusters,
                    entities=entities_data,
                    conversation_type=insights_data.conversation_type,
                    complexity_level=insights_data.complexity_level,
                    relationships=insights_data.relationships,
                    total_messages=stats.get('total_messages', 0),
                    user_messages=stats.get('user_messages', 0),
                    assistant_messages=stats.get('assistant_messages', 0),
                    avg_message_length=stats.get('avg_message_length', 0.0),
                    conversation_duration_minutes=insights_data.duration_minutes
                )
                db.add(insight)
            
            db.commit()
            db.refresh(insight)
            return insight
            
        finally:
            if should_close:
                db.close()


# Convenience functions
def analyze_conversation(
    conversation_id: int,
    user_id: int
) -> Optional[ConversationInsight]:
    """
    Analyze conversation and save insights
    
    Args:
        conversation_id: Conversation ID
        user_id: User ID
    
    Returns:
        ConversationInsight model
    """
    from backend.database.operations import MessageDB
    
    messages = MessageDB.get_messages(conversation_id)
    
    if not messages:
        return None
    
    analyzer = ConversationInsightsAnalyzer()
    insights_data = analyzer.analyze_conversation(messages, conversation_id, user_id)
    
    return analyzer.save_insights(conversation_id, user_id, insights_data)


def get_conversation_insights(conversation_id: int) -> Optional[ConversationInsight]:
    """
    Get saved conversation insights
    
    Args:
        conversation_id: Conversation ID
    
    Returns:
        ConversationInsight or None
    """
    db = get_db()
    try:
        return db.query(ConversationInsight).filter(
            ConversationInsight.conversation_id == conversation_id
        ).first()
    finally:
        db.close()

