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
    
    def __init__(self, user_id: int, conversation_id: Optional[int] = None):
        """
        Initialize chat manager
        
        Args:
            user_id: User ID who owns this conversation
            conversation_id: Existing conversation ID, or None to create new
        """
        self.user_id = user_id
        
        if conversation_id:
            self.conversation_id = conversation_id
        else:
            # Create new conversation for this user
            conversation = ConversationDB.create_conversation(user_id=user_id)
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
        images: Optional[List[Dict]] = None,
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
            tools: Optional tool definitions
            images: Optional list of image data dicts (with 'data' as base64)
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
        
        # Handle images if provided (for vision models)
        if images and len(images) > 0:
            # Check if model supports vision
            model_info = llm_provider.get_model_info(model)
            if model_info and model_info.supports_vision:
                # Replace the last user message with multimodal content
                # Find the last user message
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i]["role"] == "user":
                        # Format message with images
                        if provider.lower() == "openai":
                            # OpenAI format
                            content_parts = [
                                {"type": "text", "text": messages[i]["content"]}
                            ]
                            
                            for img in images:
                                # Assume image data is already base64 encoded
                                img_format = img.get('format', 'png').lower()
                                mime_type = f"image/{img_format}"
                                data_url = f"data:{mime_type};base64,{img['data']}"
                                
                                content_parts.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": data_url,
                                        "detail": "auto"  # or "low", "high"
                                    }
                                })
                            
                            messages[i]["content"] = content_parts
                        
                        elif provider.lower() == "gemini":
                            # Gemini format (similar but slightly different)
                            content_parts = [messages[i]["content"]]
                            
                            for img in images:
                                import base64
                                # Gemini expects parts with inline_data
                                content_parts.append({
                                    "inline_data": {
                                        "mime_type": f"image/{img.get('format', 'png').lower()}",
                                        "data": img['data']
                                    }
                                })
                            
                            messages[i]["parts"] = content_parts
                        
                        break
            else:
                # Model doesn't support vision, add image info to text
                image_info_text = "\n\n[Note: User attached images but this model doesn't support vision. "
                image_info_text += f"Attached: {', '.join([img.get('filename', 'image') for img in images])}]"
                messages[-1]["content"] += image_info_text
        
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
                
                # Limit to maximum 2 tool calls to prevent excessive API usage
                max_tools = 2
                if len(response.tool_calls) > max_tools:
                    print(f"⚠️ LLM requested {len(response.tool_calls)} tool calls, limiting to {max_tools}")
                    response.tool_calls = response.tool_calls[:max_tools]
                
                # Execute tool and get results
                tool_results = []
                for tool_call in response.tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    print(f"🔧 Tool Call: {function_name}({function_args.get('query', function_args.get('url', '')[:50])})")
                    
                    # Execute the tool
                    result = None
                    if function_name == "web_search":
                        tool = get_tavily_tool()
                        result = tool.execute(function_args)
                    elif function_name in ["scrape_url", "monitor_url"]:
                        from backend.tools.scraper_tool import execute_scraper_tool
                        result = execute_scraper_tool(function_name, function_args)
                    elif function_name in ["summarize_youtube_video", "get_playlist_summary"]:
                        from backend.tools.youtube_integration import execute_youtube_tool
                        result = execute_youtube_tool(function_name, function_args)
                    elif function_name in ["analyze_dataset", "create_visualization", "generate_pandas_code"]:
                        from backend.tools.data_analyzer_integration import execute_data_analyzer_tool
                        result = execute_data_analyzer_tool(function_name, function_args)
                    elif function_name == "generate_image":
                        from backend.tools.image_generator import execute_image_generation_tool
                        result = execute_image_generation_tool(function_name, function_args)
                    
                    if result:
                        tool_results.append({
                            "tool_call_id": tool_call['id'],
                            "role": "tool",
                            "name": function_name,
                            "content": result
                        })
                        print(f"✅ Tool {function_name} executed successfully")
                
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
                        print(f"📤 Sending tool result to LLM: {tool_result['content'][:200]}...")
                    
                    # Make second API call with tool results
                    print("🔄 Generating response with search results...")
                    print(f"📝 Total messages in conversation: {len(messages)}")
                    # Don't include tools in second call to prevent infinite loop
                    # Remove 'tools' from kwargs if present
                    kwargs_without_tools = {k: v for k, v in kwargs.items() if k != 'tools'}
                    response = await llm_provider.chat_completion(
                        messages=messages,
                        model=model,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=False,
                        **kwargs_without_tools
                    )
                    print(f"✅ Got final response (has tool_calls: {bool(response.tool_calls)})")
                    
                    # Prepend tool results to the response content so images are displayed
                    tool_results_content = "\n\n".join([tr['content'] for tr in tool_results])
                    response.content = f"{tool_results_content}\n\n---\n\n{response.content}"
                    print(f"📝 Combined tool results with LLM response for display")
            
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

