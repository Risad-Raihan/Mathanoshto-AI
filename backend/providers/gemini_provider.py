"""
Google Gemini provider implementation
Supports Gemini 1.5 Pro, Flash, and 2.0 models
"""
from typing import List, Dict, Optional, AsyncIterator, Any
import google.generativeai as genai
import google.ai.generativelanguage as glm
import yaml
from PIL import Image
import io

from backend.providers.base import (
    BaseLLMProvider,
    ModelInfo,
    CompletionResponse,
    MessageRole
)
from backend.config.settings import settings

class GeminiProvider(BaseLLMProvider):
    """Google Gemini API provider"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini provider
        
        Args:
            api_key: Gemini API key (defaults to settings)
        """
        api_key = api_key or settings.gemini_api_key
        
        if not api_key:
            raise ValueError("Gemini API key not provided")
        
        super().__init__(api_key)
        
        # Configure Gemini
        genai.configure(api_key=api_key)
    
    @property
    def provider_name(self) -> str:
        return "Gemini"
    
    def _load_models(self) -> None:
        """Load Gemini models from config"""
        config_path = settings.model_config_path
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        gemini_config = config.get('gemini', {})
        
        for model_data in gemini_config.get('models', []):
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
    
    def _convert_messages_to_gemini_format(
        self,
        messages: List[Dict[str, Any]]
    ) -> tuple[Optional[str], List[Dict]]:
        """
        Convert standard message format to Gemini format
        
        Returns:
            (system_instruction, conversation_history)
        """
        system_instruction = None
        conversation = []
        
        for msg in messages:
            role = msg['role']
            content = msg['content']
            
            if role == 'system':
                system_instruction = content
            elif role == 'user':
                conversation.append({
                    'role': 'user',
                    'parts': [content] if isinstance(content, str) else content
                })
            elif role == 'assistant':
                conversation.append({
                    'role': 'model',
                    'parts': [content]
                })
        
        return system_instruction, conversation
    
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
        """Send chat completion request to Gemini"""
        
        if not self.validate_model(model):
            raise ValueError(f"Model {model} not available for Gemini provider")
        
        # Convert messages to Gemini format
        system_instruction, conversation = self._convert_messages_to_gemini_format(messages)
        
        # Create model instance
        generation_config = genai.types.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens or 8192,
        )
        
        # JSON mode
        if json_mode and self.supports_json_mode(model):
            generation_config.response_mime_type = "application/json"
        
        # Create model with optional system instruction
        if system_instruction:
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config,
                system_instruction=system_instruction
            )
        else:
            gemini_model = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )
        
        # Convert tools if provided (Gemini function calling format)
        gemini_tools = None
        if tools and self.supports_tools(model):
            gemini_tools = self._convert_tools_to_gemini_format(tools)
            # Update model with tools
            if gemini_tools:
                if system_instruction:
                    gemini_model = genai.GenerativeModel(
                        model_name=model,
                        generation_config=generation_config,
                        system_instruction=system_instruction,
                        tools=gemini_tools
                    )
                else:
                    gemini_model = genai.GenerativeModel(
                        model_name=model,
                        generation_config=generation_config,
                        tools=gemini_tools
                    )
        
        if stream:
            return self._stream_completion(gemini_model, conversation)
        else:
            return await self._complete(gemini_model, conversation, model)
    
    async def _complete(
        self,
        model_instance: genai.GenerativeModel,
        conversation: List[Dict],
        model_name: str
    ) -> CompletionResponse:
        """Non-streaming completion"""
        try:
            # Start chat or generate content
            if len(conversation) > 1:
                # Multi-turn conversation
                chat = model_instance.start_chat(history=conversation[:-1])
                response = await chat.send_message_async(
                    conversation[-1]['parts'][0]
                )
            else:
                # Single message
                response = await model_instance.generate_content_async(
                    conversation[0]['parts'][0]
                )
            
            # Extract token counts
            usage = response.usage_metadata
            input_tokens = usage.prompt_token_count
            output_tokens = usage.candidates_token_count
            total_tokens = usage.total_token_count
            
            # Calculate cost
            model_info = self.get_model_info(model_name)
            cost = 0.0
            if model_info:
                cost = model_info.calculate_cost(input_tokens, output_tokens)
            
            # Check for function calls
            tool_calls = None
            finish_reason = "stop"
            content = ""
            
            if response.candidates[0].content.parts:
                first_part = response.candidates[0].content.parts[0]
                if hasattr(first_part, 'function_call') and first_part.function_call:
                    # Has function call
                    finish_reason = "tool_calls"
                    import json
                    # Convert args to JSON string
                    args_dict = dict(first_part.function_call.args) if first_part.function_call.args else {}
                    tool_calls = [{
                        "id": f"call_{first_part.function_call.name}",  # Generate ID for compatibility
                        "type": "function",
                        "function": {
                            "name": first_part.function_call.name,
                            "arguments": json.dumps(args_dict)
                        }
                    }]
                    # When there's a function call, there's usually no text content
                    content = ""
                else:
                    # Normal text response
                    content = response.text
            else:
                # No parts, try to get text
                try:
                    content = response.text
                except:
                    content = ""
            
            return CompletionResponse(
                content=content,
                model=model_name,
                provider=self.provider_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                cost=cost,
                finish_reason=finish_reason,
                tool_calls=tool_calls,
                raw_response=response
            )
            
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    async def _stream_completion(
        self,
        model_instance: genai.GenerativeModel,
        conversation: List[Dict]
    ) -> AsyncIterator[str]:
        """Streaming completion"""
        try:
            if len(conversation) > 1:
                chat = model_instance.start_chat(history=conversation[:-1])
                response_stream = await chat.send_message_async(
                    conversation[-1]['parts'][0],
                    stream=True
                )
            else:
                response_stream = await model_instance.generate_content_async(
                    conversation[0]['parts'][0],
                    stream=True
                )
            
            async for chunk in response_stream:
                if chunk.text:
                    yield chunk.text
                    
        except Exception as e:
            raise Exception(f"Gemini streaming error: {str(e)}")
    
    def count_tokens(self, messages: List[Dict[str, Any]], model: str) -> int:
        """
        Count tokens using Gemini's count_tokens API
        """
        try:
            gemini_model = genai.GenerativeModel(model_name=model)
            
            # Convert messages
            _, conversation = self._convert_messages_to_gemini_format(messages)
            
            # Flatten conversation to content list
            content = []
            for msg in conversation:
                content.extend(msg['parts'])
            
            result = gemini_model.count_tokens(content)
            return result.total_tokens
            
        except Exception as e:
            # Fallback: rough estimation (4 chars per token)
            total_chars = sum(len(str(msg.get('content', ''))) for msg in messages)
            return total_chars // 4
    
    def format_message_with_image(
        self,
        text: str,
        image_data: bytes,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Format message with image for Gemini Vision API
        
        Returns message in format:
        {
            "role": "user",
            "content": [PIL.Image, "text"]
        }
        """
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        return {
            "role": "user",
            "content": [image, text]
        }
    
    def _convert_tools_to_gemini_format(self, tools: List[Dict]) -> List[genai.protos.Tool]:
        """Convert OpenAI-style tool definitions to Gemini format"""
        gemini_functions = []
        for tool in tools:
            if tool.get('type') == 'function':
                func = tool['function']
                
                # Convert OpenAI parameters to Gemini format
                parameters = func.get('parameters', {})
                properties = parameters.get('properties', {})
                required = parameters.get('required', [])
                
                # Build Gemini function declaration
                gemini_func = glm.FunctionDeclaration(
                    name=func['name'],
                    description=func['description'],
                    parameters=glm.Schema(
                        type=glm.Type.OBJECT,
                        properties={
                            key: glm.Schema(
                                type=self._convert_type_to_gemini(val.get('type', 'string')),
                                description=val.get('description', '')
                            )
                            for key, val in properties.items()
                        },
                        required=required
                    )
                )
                gemini_functions.append(gemini_func)
        
        return [glm.Tool(function_declarations=gemini_functions)] if gemini_functions else None
    
    def _convert_type_to_gemini(self, openai_type: str) -> glm.Type:
        """Convert OpenAI parameter type to Gemini type"""
        type_mapping = {
            'string': glm.Type.STRING,
            'number': glm.Type.NUMBER,
            'integer': glm.Type.INTEGER,
            'boolean': glm.Type.BOOLEAN,
            'array': glm.Type.ARRAY,
            'object': glm.Type.OBJECT
        }
        return type_mapping.get(openai_type.lower(), glm.Type.STRING)

