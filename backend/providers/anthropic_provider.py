"""
Anthropic Claude provider implementation
Supports Claude Sonnet 4.0, Sonnet 4.5, and other models
"""
from typing import List, Dict, Optional, AsyncIterator, Any
import anthropic
import yaml
import base64

from backend.providers.base import (
    BaseLLMProvider,
    ModelInfo,
    CompletionResponse,
    MessageRole
)
from backend.config.settings import settings

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key (defaults to settings)
        """
        api_key = api_key or settings.anthropic_api_key
        
        if not api_key:
            raise ValueError("Anthropic API key not provided")
        
        super().__init__(api_key)
        
        # Initialize async client
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
    
    @property
    def provider_name(self) -> str:
        return "Anthropic"
    
    def _load_models(self) -> None:
        """Load Anthropic models from config"""
        config_path = settings.model_config_path
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        anthropic_config = config.get('anthropic', {})
        
        for model_data in anthropic_config.get('models', []):
            model_info = ModelInfo(
                name=model_data['name'],
                display_name=model_data['display_name'],
                description=model_data['description'],
                context_window=model_data['context_window'],
                max_output_tokens=model_data['max_output_tokens'],
                supports_vision=model_data['supports_vision'],
                supports_tools=model_data['supports_tools'],
                supports_json_mode=model_data.get('supports_json_mode', False),
                cost_per_1m_input_tokens=model_data['cost_per_1m_input_tokens'],
                cost_per_1m_output_tokens=model_data['cost_per_1m_output_tokens']
            )
            self._models[model_info.name] = model_info
    
    def _convert_messages_to_anthropic_format(
        self,
        messages: List[Dict[str, Any]]
    ) -> tuple[Optional[str], List[Dict]]:
        """
        Convert OpenAI-style messages to Anthropic format
        
        Returns:
            (system_prompt, anthropic_messages)
        """
        system_prompt = None
        anthropic_messages = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                system_prompt = content
                continue
            
            # Skip tool role messages (OpenAI format) - they should be handled differently
            if role == 'tool':
                continue
            
            # Handle images for vision models
            if isinstance(content, list):
                # Check if this is already in Anthropic format (from tool results or raw blocks)
                # Check first item - if it's not a dict, it's already Anthropic blocks
                if content and not isinstance(content[0], dict):
                    # Raw Anthropic blocks, pass through
                    anthropic_messages.append({
                        'role': 'user' if role == 'user' else 'assistant',
                        'content': content
                    })
                    continue
                
                # Check if content contains tool_result or tool_use types (Anthropic format dicts)
                if any(isinstance(item, dict) and item.get('type') in ['tool_result', 'tool_use'] for item in content):
                    # Already in Anthropic format, pass through
                    anthropic_messages.append({
                        'role': 'user' if role == 'user' else 'assistant',
                        'content': content
                    })
                    continue
                
                # Multi-modal content (text + images)
                formatted_content = []
                for item in content:
                    if item.get('type') == 'text':
                        formatted_content.append({
                            'type': 'text',
                            'text': item['text']
                        })
                    elif item.get('type') == 'image_url':
                        # Extract base64 image data
                        image_url = item['image_url']['url']
                        if image_url.startswith('data:image'):
                            # Parse base64 data
                            media_type = image_url.split(';')[0].split(':')[1]
                            base64_data = image_url.split(',')[1]
                            formatted_content.append({
                                'type': 'image',
                                'source': {
                                    'type': 'base64',
                                    'media_type': media_type,
                                    'data': base64_data
                                }
                            })
                
                anthropic_messages.append({
                    'role': 'user' if role == 'user' else 'assistant',
                    'content': formatted_content
                })
            else:
                # Simple text content
                anthropic_messages.append({
                    'role': 'user' if role == 'user' else 'assistant',
                    'content': content
                })
        
        return system_prompt, anthropic_messages
    
    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        tools: Optional[List[Dict]] = None,
        tool_choice: Optional[str] = None,
        json_mode: bool = False,
        **kwargs
    ) -> CompletionResponse | AsyncIterator[str]:
        """
        Generate chat completion using Anthropic Claude
        
        Args:
            messages: Conversation history
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            tools: Tool definitions for function calling
            tool_choice: Tool choice strategy
            json_mode: Whether to output JSON
            **kwargs: Additional provider-specific arguments
            
        Returns:
            CompletionResponse or AsyncIterator for streaming
        """
        # Convert messages to Anthropic format
        system_prompt, anthropic_messages = self._convert_messages_to_anthropic_format(messages)
        
        # Set default max_tokens if not provided
        if max_tokens is None:
            max_tokens = 4096
        
        # Build request parameters
        request_params = {
            'model': model,
            'messages': anthropic_messages,
            'max_tokens': max_tokens,
            'temperature': temperature,
        }
        
        if system_prompt:
            request_params['system'] = system_prompt
        
        # Add tools if provided
        if tools:
            # Convert OpenAI tool format to Anthropic format
            anthropic_tools = []
            for tool in tools:
                if tool.get('type') == 'function':
                    func = tool['function']
                    anthropic_tools.append({
                        'name': func['name'],
                        'description': func['description'],
                        'input_schema': func['parameters']
                    })
            
            if anthropic_tools:
                request_params['tools'] = anthropic_tools
        
        try:
            if stream:
                # Streaming response
                async def stream_generator():
                    async with self.client.messages.stream(**request_params) as stream:
                        async for text in stream.text_stream:
                            yield text
                
                return stream_generator()
            else:
                # Non-streaming response
                response = await self.client.messages.create(**request_params)
                
                # Extract text content
                content = ""
                for block in response.content:
                    if block.type == 'text':
                        content += block.text
                
                # Handle tool calls
                tool_calls = None
                if hasattr(response, 'stop_reason') and response.stop_reason == 'tool_use':
                    tool_calls = []
                    for block in response.content:
                        if block.type == 'tool_use':
                            # Convert input dict to JSON string for compatibility with OpenAI format
                            import json
                            arguments_json = json.dumps(block.input) if isinstance(block.input, dict) else str(block.input)
                            tool_calls.append({
                                'id': block.id,
                                'type': 'function',
                                'function': {
                                    'name': block.name,
                                    'arguments': arguments_json
                                }
                            })
                
                # Calculate cost
                model_info = self.get_model_info(model)
                cost = 0.0
                if model_info:
                    cost = model_info.calculate_cost(
                        response.usage.input_tokens,
                        response.usage.output_tokens
                    )
                
                return CompletionResponse(
                    content=content,
                    model=model,
                    provider=self.provider_name,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    total_tokens=response.usage.input_tokens + response.usage.output_tokens,
                    cost=cost,
                    finish_reason=response.stop_reason,
                    tool_calls=tool_calls,
                    raw_response=response
                )
                
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def count_tokens(self, text: str, model: str = "claude-sonnet-4-20250514") -> int:
        """
        Estimate token count for text
        
        Note: Anthropic doesn't provide a public tokenizer,
        so we use a rough estimation (1 token ≈ 4 characters)
        """
        return len(text) // 4
    
    def supports_vision(self, model: str) -> bool:
        """Check if model supports vision/images"""
        model_info = self.get_model_info(model)
        return model_info.supports_vision if model_info else False
    
    def supports_function_calling(self, model: str) -> bool:
        """Check if model supports function calling"""
        model_info = self.get_model_info(model)
        return model_info.supports_tools if model_info else False
    
    def format_message_with_image(
        self,
        text: str,
        image_data: bytes,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Format a message with an image attachment for Anthropic's format
        
        Args:
            text: Text content
            image_data: Image bytes
            mime_type: MIME type (e.g., 'image/jpeg', 'image/png')
            
        Returns:
            Message dict in Anthropic's format
        """
        # Anthropic expects base64 encoded images
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        return {
            'role': 'user',
            'content': [
                {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': mime_type,
                        'data': image_base64
                    }
                },
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }

