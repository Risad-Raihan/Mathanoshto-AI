"""
Memory Extractor - Intelligent extraction of important information from conversations
Uses LLM to identify and extract memorable facts, preferences, and context
"""
import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime

from backend.database.memory_models import Memory
from backend.core.memory_manager import MemoryManager
from backend.providers.base import BaseLLMProvider


class MemoryExtractor:
    """
    Extracts important information from conversations and creates memories
    """
    
    EXTRACTION_PROMPT = """You are a memory extraction assistant. Your job is to identify and extract important, memorable information from conversations.

Analyze the following conversation and extract ANY important information that should be remembered for future interactions. This includes:

**Personal Information:**
- Name, age, location, occupation, family details
- Contact information, preferences about how to be addressed

**Preferences & Interests:**
- Likes, dislikes, hobbies, interests
- Preferred communication style, humor style
- Favorite things (foods, movies, books, music, etc.)
- Pet peeves, things they avoid

**Facts & Context:**
- Important life events, achievements
- Goals, plans, aspirations
- Challenges, problems they're facing
- Skills, expertise, knowledge areas

**Relationships:**
- Information about people they mention (friends, family, colleagues)
- Professional relationships, network

**Tasks & Commitments:**
- Things they need to do or remember
- Deadlines, appointments, reminders
- Promises or commitments made

**Conversation Context:**
- Topics of interest to continue later
- Questions left unanswered
- Follow-up topics

For each piece of information, provide:
1. **content**: The actual information to remember (be specific and concise)
2. **memory_type**: One of: personal_info, preference, fact, task, goal, relationship, conversation_summary
3. **category**: A specific subcategory (e.g., "hobby", "family", "work", "food_preference")
4. **importance**: Score from 0.0 to 1.0 (how important is this to remember?)
5. **confidence**: Score from 0.0 to 1.0 (how certain are you about this information?)
6. **tags**: Array of relevant tags for organization

**Conversation:**
{conversation}

Respond with a JSON array of extracted memories. If nothing important to remember, return an empty array.

Example response:
```json
[
  {{
    "content": "User's name is Sarah and she prefers to be called 'Sar' by friends",
    "memory_type": "personal_info",
    "category": "name_preference",
    "importance": 0.9,
    "confidence": 1.0,
    "tags": ["name", "preference"]
  }},
  {{
    "content": "Loves Italian food, especially pasta carbonara",
    "memory_type": "preference",
    "category": "food",
    "importance": 0.6,
    "confidence": 1.0,
    "tags": ["food", "italian", "pasta"]
  }}
]
```

Extract ALL relevant memories from the conversation:"""
    
    CONFLICT_RESOLUTION_PROMPT = """You are checking for conflicts between memories. 

**New Memory:**
{new_memory}

**Existing Related Memories:**
{existing_memories}

Analyze if the new memory conflicts with or updates any existing memories. Respond with:

1. **has_conflict**: true/false - Does it conflict?
2. **conflicting_ids**: Array of memory IDs that conflict
3. **resolution**: How to resolve - "supersede" (new replaces old), "merge" (combine), "keep_both" (no real conflict)
4. **merged_content**: If merging, provide the merged content

Respond in JSON format:
```json
{{
  "has_conflict": true,
  "conflicting_ids": [123, 456],
  "resolution": "supersede",
  "explanation": "New memory provides more recent information",
  "merged_content": "Updated content if merging"
}}
```"""
    
    def __init__(
        self,
        llm_provider: BaseLLMProvider,
        memory_manager: MemoryManager
    ):
        """
        Initialize memory extractor
        
        Args:
            llm_provider: LLM provider for extraction
            memory_manager: Memory manager instance
        """
        self.llm_provider = llm_provider
        self.memory_manager = memory_manager
    
    def extract_from_conversation(
        self,
        user_id: int,
        conversation: List[Dict[str, str]],
        conversation_id: Optional[int] = None,
        auto_save: bool = True
    ) -> List[Memory]:
        """
        Extract memories from a conversation
        
        Args:
            user_id: User ID
            conversation: List of message dicts with 'role' and 'content'
            conversation_id: Optional conversation ID for source tracking
            auto_save: Automatically save extracted memories
        
        Returns:
            List of created Memory objects
        """
        try:
            # Format conversation for prompt
            conv_text = self._format_conversation(conversation)
            
            # Build extraction prompt
            prompt = self.EXTRACTION_PROMPT.format(conversation=conv_text)
            
            # Call LLM to extract memories
            response = self.llm_provider.generate(
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Lower temperature for more consistent extraction
                max_tokens=2000
            )
            
            # Parse JSON response
            extracted_data = self._parse_extraction_response(response)
            
            if not extracted_data:
                return []
            
            # Create memories
            created_memories = []
            for mem_data in extracted_data:
                if auto_save:
                    # Check for conflicts before saving
                    memory = self._create_memory_with_conflict_check(
                        user_id=user_id,
                        mem_data=mem_data,
                        conversation_id=conversation_id
                    )
                    if memory:
                        created_memories.append(memory)
            
            return created_memories
        
        except Exception as e:
            print(f"Error extracting memories from conversation: {e}")
            return []
    
    def _format_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """Format conversation messages into readable text"""
        formatted = []
        for msg in conversation:
            role = msg.get('role', 'unknown').capitalize()
            content = msg.get('content', '')
            formatted.append(f"{role}: {content}")
        
        return "\n\n".join(formatted)
    
    def _parse_extraction_response(self, response: str) -> List[Dict]:
        """Parse LLM response to extract memory data"""
        try:
            # Try to find JSON in the response
            # Look for JSON array pattern
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                memories = json.loads(json_str)
                return memories
            
            # Try parsing entire response as JSON
            memories = json.loads(response)
            return memories
        
        except json.JSONDecodeError as e:
            print(f"Failed to parse extraction response as JSON: {e}")
            print(f"Response: {response[:500]}")
            return []
    
    def _create_memory_with_conflict_check(
        self,
        user_id: int,
        mem_data: Dict,
        conversation_id: Optional[int] = None
    ) -> Optional[Memory]:
        """
        Create memory with conflict resolution
        
        Args:
            user_id: User ID
            mem_data: Extracted memory data
            conversation_id: Optional conversation ID
        
        Returns:
            Created or updated Memory object
        """
        try:
            content = mem_data.get('content', '')
            memory_type = mem_data.get('memory_type', 'fact')
            
            # Search for similar existing memories
            similar_memories = self.memory_manager.search_memories(
                user_id=user_id,
                query=content,
                memory_types=[memory_type],
                limit=5,
                min_similarity=0.7  # High threshold for conflict detection
            )
            
            # If very similar memories exist, check for conflicts
            if similar_memories and similar_memories[0][1] > 0.85:
                resolution = self._resolve_conflict(
                    new_memory_data=mem_data,
                    existing_memories=similar_memories
                )
                
                if resolution['action'] == 'skip':
                    print(f"Skipping duplicate memory: {content[:50]}...")
                    return None
                
                elif resolution['action'] == 'update':
                    # Update existing memory
                    existing_memory = similar_memories[0][0]
                    updated = self.memory_manager.update_memory(
                        memory_id=existing_memory.id,
                        content=resolution.get('content', content),
                        importance_score=mem_data.get('importance', 0.5)
                    )
                    return updated
            
            # Create new memory
            memory = self.memory_manager.create_memory(
                user_id=user_id,
                content=content,
                memory_type=memory_type,
                category=mem_data.get('category'),
                tags=mem_data.get('tags', []),
                importance_score=mem_data.get('importance', 0.5),
                source_type='conversation',
                source_id=str(conversation_id) if conversation_id else None,
                confidence=mem_data.get('confidence', 0.8),
                metadata={
                    'extracted_at': datetime.utcnow().isoformat(),
                    'extraction_method': 'llm'
                }
            )
            
            return memory
        
        except Exception as e:
            print(f"Error creating memory with conflict check: {e}")
            return None
    
    def _resolve_conflict(
        self,
        new_memory_data: Dict,
        existing_memories: List[Tuple[Memory, float]]
    ) -> Dict:
        """
        Resolve conflicts between new and existing memories
        
        Args:
            new_memory_data: New memory data
            existing_memories: List of similar existing memories
        
        Returns:
            Resolution dict with 'action' and optional 'content'
        """
        # Simple heuristic-based resolution
        # In a more advanced version, you could use LLM for conflict resolution
        
        most_similar = existing_memories[0]
        similarity = most_similar[1]
        
        # Very high similarity - likely duplicate
        if similarity > 0.95:
            return {'action': 'skip'}
        
        # High similarity but not exact - update if newer or more important
        if similarity > 0.85:
            new_importance = new_memory_data.get('importance', 0.5)
            existing_importance = most_similar[0].importance_score
            
            if new_importance > existing_importance:
                return {
                    'action': 'update',
                    'content': new_memory_data.get('content')
                }
            else:
                return {'action': 'skip'}
        
        # Moderate similarity - create as new memory
        return {'action': 'create'}
    
    def extract_from_single_message(
        self,
        user_id: int,
        message: str,
        context: Optional[List[Dict[str, str]]] = None
    ) -> List[Memory]:
        """
        Extract memories from a single message (with optional context)
        
        Args:
            user_id: User ID
            message: Message text
            context: Optional previous messages for context
        
        Returns:
            List of created memories
        """
        conversation = context or []
        conversation.append({"role": "user", "content": message})
        
        return self.extract_from_conversation(
            user_id=user_id,
            conversation=conversation,
            auto_save=True
        )


class MemoryInjector:
    """
    Injects relevant memories into system prompts
    """
    
    MEMORY_INJECTION_TEMPLATE = """# Relevant Context from Previous Conversations

You have access to the following information about the user from previous interactions:

{memories}

Use this context to provide more personalized and relevant responses. Reference these memories naturally when appropriate, but don't force them into the conversation.
"""
    
    def __init__(self, memory_manager: MemoryManager):
        """
        Initialize memory injector
        
        Args:
            memory_manager: Memory manager instance
        """
        self.memory_manager = memory_manager
    
    def inject_memories_into_prompt(
        self,
        user_id: int,
        current_query: str,
        base_system_prompt: Optional[str] = None,
        max_memories: int = 10,
        memory_types: Optional[List[str]] = None
    ) -> str:
        """
        Inject relevant memories into system prompt
        
        Args:
            user_id: User ID
            current_query: Current user query
            base_system_prompt: Base system prompt to append to
            max_memories: Maximum memories to include
            memory_types: Filter by memory types
        
        Returns:
            Enhanced system prompt with memories
        """
        # Get pinned memories (always include)
        pinned = self.memory_manager.get_pinned_memories(user_id)
        
        # Search for relevant memories based on query
        relevant = self.memory_manager.search_memories(
            user_id=user_id,
            query=current_query,
            memory_types=memory_types,
            limit=max_memories - len(pinned),
            min_similarity=0.6
        )
        
        # Combine pinned and relevant memories
        all_memories = [(m, 1.0) for m in pinned] + relevant
        
        if not all_memories:
            return base_system_prompt or ""
        
        # Format memories
        memory_text = self._format_memories(all_memories)
        
        # Build final prompt
        memory_section = self.MEMORY_INJECTION_TEMPLATE.format(memories=memory_text)
        
        if base_system_prompt:
            return f"{base_system_prompt}\n\n{memory_section}"
        else:
            return memory_section
    
    def _format_memories(self, memories: List[Tuple[Memory, float]]) -> str:
        """Format memories for prompt injection"""
        formatted = []
        
        # Group by type
        by_type = {}
        for memory, score in memories:
            mem_type = memory.memory_type
            if mem_type not in by_type:
                by_type[mem_type] = []
            by_type[mem_type].append((memory, score))
        
        # Format each type
        type_labels = {
            'personal_info': '👤 Personal Information',
            'preference': '⭐ Preferences',
            'fact': '💡 Facts',
            'task': '✅ Tasks',
            'goal': '🎯 Goals',
            'relationship': '👥 Relationships',
            'conversation_summary': '💬 Previous Discussions'
        }
        
        for mem_type, mem_list in by_type.items():
            label = type_labels.get(mem_type, f"📌 {mem_type.replace('_', ' ').title()}")
            formatted.append(f"\n## {label}\n")
            
            for memory, score in sorted(mem_list, key=lambda x: x[0].importance_score, reverse=True):
                # Add importance indicator
                importance = "🔴" if memory.importance_score > 0.8 else "🟡" if memory.importance_score > 0.5 else "⚪"
                
                formatted.append(f"- {importance} {memory.content}")
                
                # Add tags if present
                if memory.tags:
                    formatted.append(f"  *Tags: {', '.join(memory.tags)}*")
        
        return "\n".join(formatted)


# Helper function for easy integration
def extract_and_save_memories(
    user_id: int,
    conversation: List[Dict[str, str]],
    llm_provider: BaseLLMProvider,
    db_session
) -> List[Memory]:
    """
    Helper function to extract and save memories from a conversation
    
    Args:
        user_id: User ID
        conversation: Conversation messages
        llm_provider: LLM provider
        db_session: Database session
    
    Returns:
        List of created memories
    """
    from backend.core.memory_manager import get_memory_manager
    
    memory_manager = get_memory_manager(db_session)
    extractor = MemoryExtractor(llm_provider, memory_manager)
    
    return extractor.extract_from_conversation(
        user_id=user_id,
        conversation=conversation,
        auto_save=True
    )

