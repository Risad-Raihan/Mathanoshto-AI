"""
OpenAI provider implementation
Supports all OpenAI models including GPT-4, GPT-4o, GPT-3.5, etc.
"""
import base64
from typing import List, Dict, Optional, AsyncIterator, Any
from openai import AsyncOpenAI
import tiktoken
import yaml
from pathlib import Path

from backend.providers.base import (
    BaseLLMProvider, 
    ModelInfo, 
    CompletionResponse,
    MessageRole
)
from backend.config.settings import settings

class OpenAIProvider(BaseLLMProvider):
    """OpenAI API provider"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key (defaults to settings)
            base_url: Custom base URL for OpenAI-compatible endpoints
        """
        api_key = api_key or settings.openai_api_key
        base_url = base_url or settings.openai_base_url
        
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        
        super().__init__(api_key, base_url)
        
        # Initialize async client
        if base_url:
            self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        else:
            self.client = AsyncOpenAI(api_key=api_key)
    
    @property
    def provider_name(self) -> str:
        return "OpenAI"
    
    def _load_models(self) -> None:
        """Load OpenAI models from config"""
        config_path = settings.model_config_path
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        openai_config = config.get('openai', {})
        
        for model_data in openai_config.get('models', []):
            model_info = ModelInfo(
                name=model_data['name'],
                display_name=model_data['display_name'],
                description=model_data['description'],
                context_window=model_data['context_window'],
                max_output_tokens=model_data['max_output_tokens'],
                supports_vision=model_data['supports_vision'],
                supports_tools=model_data['supports_tools'],
                supports_json_mode=model_data['supports_json_mode'],
                cost_per_1m_input_tokens=model_data['cost_per_1m_input_tokens'],
                cost_per_1m_output_tokens=model_data['cost_per_1m_output_tokens']
            )
            self._models[model_info.name] = model_info
    
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
        """Send chat completion request to OpenAI"""
        
        if not self.validate_model(model):
            raise ValueError(f"Model {model} not available for OpenAI provider")
        
        # Prepare request parameters
        params = {
            "model": model,
            "messages": messages,
        }
        
        # Handle temperature (some models like o1, gpt-5 have restrictions)
        if model.startswith('gpt-5'):
            # GPT-5 only supports temperature=1
            params["temperature"] = 1
        elif not model.startswith('o1'):
            # o1 models don't support temperature at all
            params["temperature"] = temperature
        
        # Handle max_tokens vs max_completion_tokens
        if max_tokens:
            # Newer models use max_completion_tokens (GPT-5, GPT-4o, o1, o3)
            if model.startswith(('gpt-5', 'gpt-4o', 'o1', 'o3')):
                params["max_completion_tokens"] = max_tokens
            else:
                params["max_tokens"] = max_tokens
        
        # Add tools if provided
        if tools:
            params["tools"] = tools
            if tool_choice:
                params["tool_choice"] = tool_choice
        
        # JSON mode
        if json_mode and self.supports_json_mode(model):
            params["response_format"] = {"type": "json_object"}
        
        # Add any additional kwargs
        params.update(kwargs)
        
        if stream:
            return self._stream_completion(params)
        else:
            return await self._complete(params)
    
    async def _complete(self, params: Dict) -> CompletionResponse:
        """Non-streaming completion"""
        try:
            # Debug logging (optional - set DEBUG=true in .env to enable)
            if settings.debug_mode:
                print(f"\n{'='*60}")
                print(f"🔍 DEBUG: Making OpenAI API call")
                print(f"Model: {params.get('model')}")
                print(f"Temperature: {params.get('temperature')}")
                print(f"Message count: {len(params.get('messages', []))}")
                print(f"{'='*60}\n")
            
            response = await self.client.chat.completions.create(**params)
            
            message = response.choices[0].message
            usage = response.usage
            model_info = self.get_model_info(params['model'])
            
            # Extract tool calls if present
            tool_calls = None
            if message.tool_calls:
                tool_calls = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            # Calculate cost
            cost = 0.0
            if model_info:
                cost = model_info.calculate_cost(
                    usage.prompt_tokens,
                    usage.completion_tokens
                )
            
            return CompletionResponse(
                content=message.content or "",
                model=response.model,
                provider=self.provider_name,
                input_tokens=usage.prompt_tokens,
                output_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                cost=cost,
                finish_reason=response.choices[0].finish_reason,
                tool_calls=tool_calls,
                raw_response=response
            )
            
        except Exception as e:
            # Error logging
            if settings.debug_mode:
                print(f"\n❌ ERROR: OpenAI API call failed")
                print(f"Model: {params.get('model')}")
                print(f"Error: {str(e)}\n")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    async def _stream_completion(self, params: Dict) -> AsyncIterator[str]:
        """Streaming completion"""
        params["stream"] = True
        
        try:
            stream = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            raise Exception(f"OpenAI streaming error: {str(e)}")
    
    def count_tokens(self, messages: List[Dict[str, Any]], model: str) -> int:
        """
        Count tokens using tiktoken
        
        Note: This is an approximation. Exact count may vary slightly.
        """
        try:
            # Try to get encoding for specific model
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            # Fall back to cl100k_base (used by gpt-4, gpt-3.5-turbo)
            encoding = tiktoken.get_encoding("cl100k_base")
        
        num_tokens = 0
        
        for message in messages:
            # Every message follows <|start|>{role/name}\n{content}<|end|>\n
            num_tokens += 4
            
            for key, value in message.items():
                if isinstance(value, str):
                    num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += -1  # Role is always 1 token, name is variable
        
        num_tokens += 2  # Every reply is primed with <|start|>assistant
        
        return num_tokens
    
    def format_message_with_image(
        self,
        text: str,
        image_data: bytes,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Format message with image for OpenAI Vision API
        
        Returns message in format:
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "..."},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
        """
        # Encode image to base64
        base64_image = base64.b64encode(image_data).decode('utf-8')
        data_url = f"data:{mime_type};base64,{base64_image}"
        
        return {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": text
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": data_url
                    }
                }
            ]
        }

