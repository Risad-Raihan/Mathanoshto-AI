"""
Chat Manager - Handles conversation flow and LLM interactions
"""
from typing import List, Dict, Optional, AsyncIterator
import asyncio

from backend.core.model_factory import model_factory
from backend.providers.base import CompletionResponse
from backend.database.operations import ConversationDB, MessageDB
from backend.database.models import Message

class ChatManager:
    """
    Manages chat conversations and coordinates with LLM providers
    """
    
    def __init__(self, conversation_id: Optional[int] = None):
        """
        Initialize chat manager
        
        Args:
            conversation_id: Existing conversation ID, or None to create new
        """
        if conversation_id:
            self.conversation_id = conversation_id
        else:
            # Create new conversation
            conversation = ConversationDB.create_conversation()
            self.conversation_id = conversation.id
        
        self.factory = model_factory
    
    def get_conversation_history(self) -> List[Dict]:
        """
        Get conversation history in LLM format
        
        Returns:
            List of message dicts with 'role' and 'content'
        """
        messages = MessageDB.get_messages(self.conversation_id)
        
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    async def send_message(
        self,
        user_message: str,
        provider: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        system_prompt: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> CompletionResponse | AsyncIterator[str]:
        """
        Send a message and get LLM response
        
        Args:
            user_message: User's message
            provider: Provider name (openai, gemini)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            stream: Whether to stream response
            system_prompt: Optional system prompt
            **kwargs: Additional provider-specific args
            
        Returns:
            CompletionResponse or AsyncIterator for streaming
        """
        # Get provider instance
        llm_provider = self.factory.get_provider(provider)
        if not llm_provider:
            raise ValueError(f"Provider {provider} not available")
        
        # Add user message to database
        MessageDB.add_message(
            conversation_id=self.conversation_id,
            role="user",
            content=user_message
        )
        
        # Build message history
        messages = self.get_conversation_history()
        
        # Add system prompt if provided
        if system_prompt:
            messages.insert(0, {"role": "system", "content": system_prompt})
        
        # Get LLM response
        if stream:
            return await llm_provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
        else:
            # Add tools to kwargs if provided
            if tools:
                kwargs['tools'] = tools
            
            response = await llm_provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
                **kwargs
            )
            
            # Handle tool calls if present
            if response.tool_calls:
                # Import here to avoid circular dependency
                from backend.tools.tavily_search import get_tavily_tool
                import json
                
                # Execute tool and get results
                tool_results = []
                for tool_call in response.tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    print(f"🔧 Tool Call: {function_name}({function_args.get('query', '')})")
                    
                    # Execute the tool
                    if function_name == "web_search":
                        tool = get_tavily_tool()
                        result = tool.execute(function_args)
                        tool_results.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "name": function_name,
                            "content": result
                        })
                        print(f"✅ Tool executed successfully")
                
                # If we have tool results, make a second call with the results
                if tool_results:
                    # Add assistant's tool call message
                    messages.append({
                        "role": "assistant",
                        "content": response.content or "",
                        "tool_calls": response.tool_calls
                    })
                    
                    # Add tool results
                    for tool_result in tool_results:
                        messages.append(tool_result)
                    
                    # Make second API call with tool results
                    print("🔄 Generating response with search results...")
                    response = await llm_provider.chat_completion(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False,
                        tools=tools,
                        **kwargs
                    )
            
            # Save assistant response to database
            MessageDB.add_message(
                conversation_id=self.conversation_id,
                role="assistant",
                content=response.content,
                model=response.model,
                provider=response.provider,
                input_tokens=response.input_tokens,
                output_tokens=response.output_tokens,
                cost=response.cost,
                finish_reason=response.finish_reason
            )
            
            return response
    
    def get_token_usage(self) -> Dict:
        """Get token usage statistics for this conversation"""
        return MessageDB.get_conversation_tokens(self.conversation_id)
    
    def update_title(self, title: str):
        """Update conversation title"""
        ConversationDB.update_conversation_title(self.conversation_id, title)
    
    async def auto_generate_title(self, provider: str = "openai", model: str = "gpt-3.5-turbo"):
        """
        Auto-generate a title based on conversation content
        Uses first few messages to create a concise title
        """
        messages = self.get_conversation_history()
        
        if len(messages) < 2:
            return
        
        # Take first few messages for context
        context_messages = messages[:4]
        context_text = "\n".join([f"{m['role']}: {m['content']}" for m in context_messages])
        
        # Ask LLM to generate title
        title_prompt = [
            {
                "role": "system",
                "content": "Generate a short, concise title (3-6 words) for this conversation. Only return the title, nothing else."
            },
            {
                "role": "user",
                "content": f"Conversation:\n{context_text}"
            }
        ]
        
        llm_provider = self.factory.get_provider(provider)
        if llm_provider:
            try:
                response = await llm_provider.chat_completion(
                    messages=title_prompt,
                    model=model,
                    temperature=0.7,
                    max_tokens=20
                )
                title = response.content.strip().strip('"').strip("'")
                self.update_title(title)
            except Exception as e:
                print(f"Failed to auto-generate title: {e}")

