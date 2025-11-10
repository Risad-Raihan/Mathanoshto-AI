# Personal LLM Assistant - Implementation Plan

## 🎯 Project Goal
Transform the Tavily search wrapper into a full-fledged personal LLM chat interface with multi-model support, multimodal capabilities, and Tavily search as an optional tool.

---

## 📋 Phase 1: Foundation & Restructuring (Week 1)

### Task 1.1: Project Restructuring
**Goal:** Reorganize codebase into a professional, modular structure.

**Steps:**
1. Create new directory structure:
```bash
mkdir -p backend/{config,core,providers,tools,utils,database}
mkdir -p frontend/streamlit/components
mkdir -p frontend/streamlit/styles
mkdir -p tests/{unit,integration}
mkdir -p docs
```

2. Create `__init__.py` files in all Python packages:
```bash
touch backend/__init__.py
touch backend/config/__init__.py
touch backend/core/__init__.py
touch backend/providers/__init__.py
touch backend/tools/__init__.py
touch backend/utils/__init__.py
touch backend/database/__init__.py
touch frontend/__init__.py
touch frontend/streamlit/__init__.py
```

3. Move existing code:
   - Keep current `tavily_search.py` as reference
   - Extract Tavily functions → `backend/tools/tavily_search.py`
   - Extract OpenAI wrapper → `backend/providers/openai_provider.py`
   - Extract Gemini wrapper → `backend/providers/gemini_provider.py`

**Files to create:**
- `backend/config/settings.py`
- `backend/config/models.yaml`
- `backend/core/chat_manager.py`
- `backend/core/model_factory.py`
- `backend/providers/base.py`

---

### Task 1.2: Configuration Management
**Goal:** Create centralized configuration system with model definitions.

**File: `backend/config/settings.py`**
```python
"""
Centralized configuration management using Pydantic
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os
from pathlib import Path

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    tavily_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    openai_base_url: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./chat_history.db"
    
    # Application
    app_name: str = "Personal LLM Assistant"
    debug_mode: bool = False
    
    # File Storage
    upload_dir: Path = Path("uploads")
    max_upload_size_mb: int = 10
    
    # Model Configuration
    model_config_path: Path = Path("backend/config/models.yaml")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )

# Global settings instance
settings = Settings()
```

**File: `backend/config/models.yaml`**
```yaml
# Model Registry - All available models and their capabilities

openai:
  provider_name: "OpenAI"
  base_url: "https://api.openai.com/v1"
  models:
    - name: "gpt-4o"
      display_name: "GPT-4o"
      description: "Most advanced multimodal model"
      context_window: 128000
      max_output_tokens: 16384
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 2.50
      cost_per_1m_output_tokens: 10.00
      
    - name: "gpt-4o-mini"
      display_name: "GPT-4o Mini"
      description: "Fast and affordable multimodal model"
      context_window: 128000
      max_output_tokens: 16384
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 0.15
      cost_per_1m_output_tokens: 0.60
      
    - name: "gpt-4-turbo"
      display_name: "GPT-4 Turbo"
      description: "Previous generation flagship model"
      context_window: 128000
      max_output_tokens: 4096
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 10.00
      cost_per_1m_output_tokens: 30.00
      
    - name: "gpt-4"
      display_name: "GPT-4"
      description: "Original GPT-4 model"
      context_window: 8192
      max_output_tokens: 8192
      supports_vision: false
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 30.00
      cost_per_1m_output_tokens: 60.00
      
    - name: "gpt-3.5-turbo"
      display_name: "GPT-3.5 Turbo"
      description: "Fast and efficient model"
      context_window: 16385
      max_output_tokens: 4096
      supports_vision: false
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 0.50
      cost_per_1m_output_tokens: 1.50

gemini:
  provider_name: "Google Gemini"
  models:
    - name: "gemini-2.0-flash-exp"
      display_name: "Gemini 2.0 Flash (Experimental)"
      description: "Next generation experimental model"
      context_window: 1048576
      max_output_tokens: 8192
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 0.0  # Free during preview
      cost_per_1m_output_tokens: 0.0
      
    - name: "gemini-1.5-pro"
      display_name: "Gemini 1.5 Pro"
      description: "Most capable model with 1M context"
      context_window: 1048576
      max_output_tokens: 8192
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 1.25
      cost_per_1m_output_tokens: 5.00
      
    - name: "gemini-1.5-flash"
      display_name: "Gemini 1.5 Flash"
      description: "Fast and efficient with 1M context"
      context_window: 1048576
      max_output_tokens: 8192
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 0.075
      cost_per_1m_output_tokens: 0.30
      
    - name: "gemini-1.5-flash-8b"
      display_name: "Gemini 1.5 Flash-8B"
      description: "Smallest and fastest model"
      context_window: 1048576
      max_output_tokens: 8192
      supports_vision: true
      supports_tools: true
      supports_json_mode: true
      cost_per_1m_input_tokens: 0.0375
      cost_per_1m_output_tokens: 0.15

anthropic:
  provider_name: "Anthropic Claude"
  base_url: "https://api.anthropic.com/v1"
  models:
    - name: "claude-3-5-sonnet-20241022"
      display_name: "Claude 3.5 Sonnet"
      description: "Most intelligent model"
      context_window: 200000
      max_output_tokens: 8192
      supports_vision: true
      supports_tools: true
      supports_json_mode: false
      cost_per_1m_input_tokens: 3.00
      cost_per_1m_output_tokens: 15.00
      
    - name: "claude-3-5-haiku-20241022"
      display_name: "Claude 3.5 Haiku"
      description: "Fast and affordable"
      context_window: 200000
      max_output_tokens: 8192
      supports_vision: false
      supports_tools: true
      supports_json_mode: false
      cost_per_1m_input_tokens: 1.00
      cost_per_1m_output_tokens: 5.00
      
    - name: "claude-3-opus-20240229"
      display_name: "Claude 3 Opus"
      description: "Previous flagship model"
      context_window: 200000
      max_output_tokens: 4096
      supports_vision: true
      supports_tools: true
      supports_json_mode: false
      cost_per_1m_input_tokens: 15.00
      cost_per_1m_output_tokens: 75.00
```

**Testing:**
```python
# Test configuration loading
from backend.config.settings import settings
print(f"App name: {settings.app_name}")
print(f"OpenAI Key exists: {bool(settings.openai_api_key)}")
```

---

### Task 1.3: Provider Base Class
**Goal:** Create abstract base class that all LLM providers will implement.

**File: `backend/providers/base.py`**
```python
"""
Abstract base class for all LLM providers
Defines the interface that all providers must implement
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, AsyncIterator, Any
from dataclasses import dataclass
from enum import Enum

class MessageRole(str, Enum):
    """Message roles in a conversation"""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"

@dataclass
class ModelInfo:
    """Information about a specific model"""
    name: str
    display_name: str
    description: str
    context_window: int
    max_output_tokens: int
    supports_vision: bool
    supports_tools: bool
    supports_json_mode: bool
    cost_per_1m_input_tokens: float
    cost_per_1m_output_tokens: float
    
    def calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for given token counts"""
        input_cost = (input_tokens / 1_000_000) * self.cost_per_1m_input_tokens
        output_cost = (output_tokens / 1_000_000) * self.cost_per_1m_output_tokens
        return input_cost + output_cost

@dataclass
class CompletionResponse:
    """Response from a chat completion"""
    content: str
    model: str
    provider: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost: float
    finish_reason: str
    tool_calls: Optional[List[Dict]] = None
    raw_response: Optional[Any] = None

class BaseLLMProvider(ABC):
    """
    Abstract base class for LLM providers
    All providers (OpenAI, Gemini, Anthropic) must implement this interface
    """
    
    def __init__(self, api_key: str, base_url: Optional[str] = None):
        """
        Initialize the provider
        
        Args:
            api_key: API key for the provider
            base_url: Optional custom base URL for the API
        """
        self.api_key = api_key
        self.base_url = base_url
        self._models: Dict[str, ModelInfo] = {}
        self._load_models()
    
    @abstractmethod
    def _load_models(self) -> None:
        """Load available models from config"""
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name (e.g., 'OpenAI', 'Gemini')"""
        pass
    
    def get_available_models(self) -> List[ModelInfo]:
        """Return list of available models"""
        return list(self._models.values())
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model"""
        return self._models.get(model_name)
    
    @abstractmethod
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
        Send a chat completion request
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            tools: Optional list of tool definitions
            tool_choice: How to handle tool calls ('auto', 'none', or specific tool)
            json_mode: Whether to return JSON output
            **kwargs: Additional provider-specific parameters
            
        Returns:
            CompletionResponse object or AsyncIterator for streaming
        """
        pass
    
    @abstractmethod
    def count_tokens(self, messages: List[Dict[str, Any]], model: str) -> int:
        """
        Count tokens in a message list
        
        Args:
            messages: List of message dicts
            model: Model name (for provider-specific tokenization)
            
        Returns:
            Total token count
        """
        pass
    
    @abstractmethod
    def format_message_with_image(
        self,
        text: str,
        image_data: bytes,
        mime_type: str
    ) -> Dict[str, Any]:
        """
        Format a message with an image attachment
        Different providers have different formats for vision messages
        
        Args:
            text: Text content
            image_data: Image bytes
            mime_type: MIME type (e.g., 'image/jpeg')
            
        Returns:
            Formatted message dict
        """
        pass
    
    def validate_model(self, model: str) -> bool:
        """Check if model is available"""
        return model in self._models
    
    def supports_vision(self, model: str) -> bool:
        """Check if model supports vision"""
        model_info = self._models.get(model)
        return model_info.supports_vision if model_info else False
    
    def supports_tools(self, model: str) -> bool:
        """Check if model supports function calling"""
        model_info = self._models.get(model)
        return model_info.supports_tools if model_info else False
    
    def supports_json_mode(self, model: str) -> bool:
        """Check if model supports JSON mode"""
        model_info = self._models.get(model)
        return model_info.supports_json_mode if model_info else False
```

**Testing:**
```python
# This is an abstract class, will test with concrete implementations
```

---

### Task 1.4: OpenAI Provider Implementation
**Goal:** Implement OpenAI provider with all models and features.

**File: `backend/providers/openai_provider.py`**
```python
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
            "temperature": temperature,
        }
        
        # Handle max_tokens vs max_completion_tokens
        if max_tokens:
            # Newer models use max_completion_tokens
            if model.startswith(('gpt-4o', 'o1', 'o3')):
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
```

**Testing:**
```python
# Test OpenAI provider
import asyncio
from backend.providers.openai_provider import OpenAIProvider

async def test_openai():
    provider = OpenAIProvider()
    
    # List models
    models = provider.get_available_models()
    print(f"Available models: {[m.display_name for m in models]}")
    
    # Test completion
    messages = [{"role": "user", "content": "Say hello!"}]
    response = await provider.chat_completion(
        messages=messages,
        model="gpt-3.5-turbo",
        max_tokens=50
    )
    
    print(f"Response: {response.content}")
    print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")
    print(f"Cost: ${response.cost:.6f}")

asyncio.run(test_openai())
```

---

### Task 1.5: Gemini Provider Implementation
**Goal:** Implement Gemini provider with all models.

**File: `backend/providers/gemini_provider.py`**
```python
"""
Google Gemini provider implementation
Supports Gemini 1.5 Pro, Flash, and 2.0 models
"""
from typing import List, Dict, Optional, AsyncIterator, Any
import google.generativeai as genai
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
            
            if response.candidates[0].content.parts:
                first_part = response.candidates[0].content.parts[0]
                if hasattr(first_part, 'function_call'):
                    # Has function call
                    finish_reason = "tool_calls"
                    tool_calls = [{
                        "type": "function",
                        "function": {
                            "name": first_part.function_call.name,
                            "arguments": str(first_part.function_call.args)
                        }
                    }]
            
            return CompletionResponse(
                content=response.text,
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
    
    def _convert_tools_to_gemini_format(self, tools: List[Dict]) -> List:
        """Convert OpenAI-style tool definitions to Gemini format"""
        # This is a placeholder - implement actual conversion
        # Gemini uses a different function calling format
        return tools
```

**Testing:**
```python
# Test Gemini provider
import asyncio
from backend.providers.gemini_provider import GeminiProvider

async def test_gemini():
    provider = GeminiProvider()
    
    # List models
    models = provider.get_available_models()
    print(f"Available models: {[m.display_name for m in models]}")
    
    # Test completion
    messages = [{"role": "user", "content": "Say hello!"}]
    response = await provider.chat_completion(
        messages=messages,
        model="gemini-1.5-flash",
        max_tokens=50
    )
    
    print(f"Response: {response.content}")
    print(f"Tokens: {response.input_tokens} in, {response.output_tokens} out")
    print(f"Cost: ${response.cost:.6f}")

asyncio.run(test_gemini())
```

---

### Task 1.6: Model Factory
**Goal:** Create a factory to instantiate and manage providers.

**File: `backend/core/model_factory.py`**
```python
"""
Model Factory - Central hub for managing LLM providers and models
"""
from typing import Dict, List, Optional
from enum import Enum

from backend.providers.base import BaseLLMProvider, ModelInfo
from backend.providers.openai_provider import OpenAIProvider
from backend.providers.gemini_provider import GeminiProvider
from backend.config.settings import settings

class ProviderType(str, Enum):
    """Available provider types"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"

class ModelFactory:
    """
    Factory for creating and managing LLM providers
    Singleton pattern to maintain provider instances
    """
    
    _instance = None
    _providers: Dict[str, BaseLLMProvider] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelFactory, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self._initialized = True
        self._load_providers()
    
    def _load_providers(self):
        """Initialize all available providers based on API keys"""
        
        # OpenAI
        if settings.openai_api_key:
            try:
                self._providers[ProviderType.OPENAI] = OpenAIProvider()
                print(f"✓ Loaded OpenAI provider")
            except Exception as e:
                print(f"⚠️ Failed to load OpenAI: {e}")
        
        # Gemini
        if settings.gemini_api_key:
            try:
                self._providers[ProviderType.GEMINI] = GeminiProvider()
                print(f"✓ Loaded Gemini provider")
            except Exception as e:
                print(f"⚠️ Failed to load Gemini: {e}")
        
        # Anthropic (future)
        # if settings.anthropic_api_key:
        #     self._providers[ProviderType.ANTHROPIC] = AnthropicProvider()
    
    def get_provider(self, provider_type: str) -> Optional[BaseLLMProvider]:
        """Get a provider instance"""
        return self._providers.get(provider_type)
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self._providers.keys())
    
    def get_all_models(self) -> Dict[str, List[ModelInfo]]:
        """Get all available models grouped by provider"""
        all_models = {}
        
        for provider_name, provider in self._providers.items():
            all_models[provider_name] = provider.get_available_models()
        
        return all_models
    
    def get_models_for_provider(self, provider_type: str) -> List[ModelInfo]:
        """Get models for a specific provider"""
        provider = self.get_provider(provider_type)
        if provider:
            return provider.get_available_models()
        return []
    
    def get_model_info(self, provider_type: str, model_name: str) -> Optional[ModelInfo]:
        """Get info for a specific model"""
        provider = self.get_provider(provider_type)
        if provider:
            return provider.get_model_info(model_name)
        return None

# Global factory instance
model_factory = ModelFactory()
```

**Testing:**
```python
# Test model factory
from backend.core.model_factory import model_factory

# Get available providers
providers = model_factory.get_available_providers()
print(f"Available providers: {providers}")

# Get all models
all_models = model_factory.get_all_models()
for provider, models in all_models.items():
    print(f"\n{provider}:")
    for model in models:
        print(f"  - {model.display_name} ({model.name})")
        print(f"    Context: {model.context_window:,} tokens")
        print(f"    Vision: {model.supports_vision}")
```

---

## 📋 Phase 2: Database & Chat Management (Week 2)

### Task 2.1: Database Models
**Goal:** Set up SQLAlchemy models for storing conversations.

**File: `backend/database/models.py`**
```python
"""
Database models for storing conversations, messages, and attachments
"""
from sqlalchemy import (
    Column, Integer, String, Text, Float, 
    DateTime, ForeignKey, Boolean, LargeBinary
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Conversation(Base):
    """Conversation/Chat session"""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_archived = Column(Boolean, default=False)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}')>"

class Message(Base):
    """Individual message in a conversation"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    
    # Message content
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    
    # Model info
    model = Column(String(100), nullable=True)  # Which model generated this (for assistant messages)
    provider = Column(String(50), nullable=True)  # Which provider (openai, gemini, etc.)
    
    # Token usage
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    cost = Column(Float, default=0.0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    finish_reason = Column(String(50), nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    attachments = relationship("Attachment", back_populates="message", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="message", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', content='{self.content[:30]}...')>"

class Attachment(Base):
    """File attachments (images, PDFs, etc.)"""
    __tablename__ = 'attachments'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    
    # File info
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'image', 'pdf', 'text'
    mime_type = Column(String(100), nullable=False)
    file_size = Column(Integer, nullable=False)  # Size in bytes
    file_path = Column(String(500), nullable=True)  # Path to stored file
    file_data = Column(LargeBinary, nullable=True)  # Or store inline for small files
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment(id={self.id}, filename='{self.filename}')>"

class ToolCall(Base):
    """Function/tool calls made during conversation"""
    __tablename__ = 'tool_calls'
    
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    
    # Tool info
    tool_name = Column(String(100), nullable=False)  # e.g., 'tavily_search'
    tool_input = Column(Text, nullable=False)  # JSON string of input arguments
    tool_output = Column(Text, nullable=True)  # JSON string of output
    
    # Status
    status = Column(String(20), default='pending')  # 'pending', 'success', 'error'
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    message = relationship("Message", back_populates="tool_calls")
    
    def __repr__(self):
        return f"<ToolCall(id={self.id}, tool='{self.tool_name}', status='{self.status}')>"
```

**File: `backend/database/operations.py`**
```python
"""
Database operations for conversations and messages
"""
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime

from backend.database.models import Base, Conversation, Message, Attachment, ToolCall
from backend.config.settings import settings

# Create engine and session
engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Don't close here, let caller manage

class ConversationDB:
    """Database operations for conversations"""
    
    @staticmethod
    def create_conversation(title: str = "New Conversation") -> Conversation:
        """Create a new conversation"""
        db = get_db()
        try:
            conversation = Conversation(title=title)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)
            return conversation
        finally:
            db.close()
    
    @staticmethod
    def get_conversation(conversation_id: int) -> Optional[Conversation]:
        """Get a conversation by ID"""
        db = get_db()
        try:
            return db.query(Conversation).filter(Conversation.id == conversation_id).first()
        finally:
            db.close()
    
    @staticmethod
    def list_conversations(limit: int = 50, include_archived: bool = False) -> List[Conversation]:
        """List all conversations"""
        db = get_db()
        try:
            query = db.query(Conversation)
            if not include_archived:
                query = query.filter(Conversation.is_archived == False)
            return query.order_by(desc(Conversation.updated_at)).limit(limit).all()
        finally:
            db.close()
    
    @staticmethod
    def update_conversation_title(conversation_id: int, title: str):
        """Update conversation title"""
        db = get_db()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.title = title
                conversation.updated_at = datetime.utcnow()
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def archive_conversation(conversation_id: int):
        """Archive a conversation"""
        db = get_db()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.is_archived = True
                db.commit()
        finally:
            db.close()
    
    @staticmethod
    def delete_conversation(conversation_id: int):
        """Permanently delete a conversation"""
        db = get_db()
        try:
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                db.delete(conversation)
                db.commit()
        finally:
            db.close()

class MessageDB:
    """Database operations for messages"""
    
    @staticmethod
    def add_message(
        conversation_id: int,
        role: str,
        content: str,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        finish_reason: Optional[str] = None
    ) -> Message:
        """Add a message to a conversation"""
        db = get_db()
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                model=model,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
                cost=cost,
                finish_reason=finish_reason
            )
            db.add(message)
            
            # Update conversation timestamp
            conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
            if conversation:
                conversation.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(message)
            return message
        finally:
            db.close()
    
    @staticmethod
    def get_messages(conversation_id: int) -> List[Message]:
        """Get all messages in a conversation"""
        db = get_db()
        try:
            return db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).order_by(Message.created_at).all()
        finally:
            db.close()
    
    @staticmethod
    def get_conversation_tokens(conversation_id: int) -> dict:
        """Get total token usage for a conversation"""
        db = get_db()
        try:
            messages = db.query(Message).filter(
                Message.conversation_id == conversation_id
            ).all()
            
            total_input = sum(m.input_tokens for m in messages)
            total_output = sum(m.output_tokens for m in messages)
            total_cost = sum(m.cost for m in messages)
            
            return {
                "input_tokens": total_input,
                "output_tokens": total_output,
                "total_tokens": total_input + total_output,
                "total_cost": total_cost
            }
        finally:
            db.close()
```

**Testing:**
```python
# Test database
from backend.database.operations import init_database, ConversationDB, MessageDB

# Initialize
init_database()

# Create conversation
conv = ConversationDB.create_conversation("Test Chat")
print(f"Created conversation: {conv.id}")

# Add messages
MessageDB.add_message(
    conversation_id=conv.id,
    role="user",
    content="Hello!"
)

MessageDB.add_message(
    conversation_id=conv.id,
    role="assistant",
    content="Hi there!",
    model="gpt-4o",
    provider="openai",
    input_tokens=10,
    output_tokens=5,
    cost=0.0001
)

# Get messages
messages = MessageDB.get_messages(conv.id)
print(f"Messages: {len(messages)}")

# Get token stats
stats = MessageDB.get_conversation_tokens(conv.id)
print(f"Stats: {stats}")
```

---

### Task 2.2: Chat Manager
**Goal:** Create the core chat management logic.

**File: `backend/core/chat_manager.py`**
```python
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
            response = await llm_provider.chat_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False,
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
```

**Testing:**
```python
# Test chat manager
import asyncio
from backend.core.chat_manager import ChatManager

async def test_chat():
    # Create new chat
    chat = ChatManager()
    
    # Send message
    response = await chat.send_message(
        user_message="What is the capital of France?",
        provider="openai",
        model="gpt-3.5-turbo"
    )
    
    print(f"Response: {response.content}")
    print(f"Tokens: {response.input_tokens} + {response.output_tokens} = {response.total_tokens}")
    print(f"Cost: ${response.cost:.6f}")
    
    # Get usage
    usage = chat.get_token_usage()
    print(f"Total usage: {usage}")
    
    # Auto-generate title
    await chat.auto_generate_title()

asyncio.run(test_chat())
```

---

## 📋 Phase 3: Streamlit Frontend (Week 2-3)

### Task 3.1: Basic Streamlit App
**Goal:** Create the main Streamlit application.

**File: `frontend/streamlit/app.py`**
```python
"""
Personal LLM Assistant - Streamlit Frontend
Main application entry point
"""
import streamlit as st
import asyncio
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Personal LLM Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
from backend.database.operations import init_database
init_database()

# Import components
from frontend.streamlit.components.sidebar import render_sidebar
from frontend.streamlit.components.chat import render_chat

# Custom CSS
st.markdown("""
<style>
    /* Main chat container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Chat messages */
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Sidebar */
    .css-1d391kg {
        padding-top: 3rem;
    }
    
    /* Token counter */
    .token-counter {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'chat_manager' not in st.session_state:
    st.session_state.chat_manager = None
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Render sidebar (returns settings)
settings = render_sidebar()

# Render main chat interface
render_chat(settings)
```

**File: `frontend/streamlit/components/sidebar.py`**
```python
"""
Sidebar component with settings and controls
"""
import streamlit as st
from backend.core.model_factory import model_factory
from backend.database.operations import ConversationDB

def render_sidebar() -> dict:
    """
    Render sidebar with settings
    
    Returns:
        dict: Current settings (provider, model, temperature, etc.)
    """
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Provider selection
        available_providers = model_factory.get_available_providers()
        
        if not available_providers:
            st.error("❌ No LLM providers available. Please check your API keys.")
            return {}
        
        provider = st.selectbox(
            "Provider",
            available_providers,
            format_func=lambda x: x.upper()
        )
        
        # Model selection (dynamic based on provider)
        models = model_factory.get_models_for_provider(provider)
        model_options = {m.display_name: m.name for m in models}
        
        selected_display_name = st.selectbox(
            "Model",
            list(model_options.keys())
        )
        model = model_options[selected_display_name]
        
        # Show model info
        model_info = model_factory.get_model_info(provider, model)
        if model_info:
            with st.expander("ℹ️ Model Info"):
                st.write(f"**Description:** {model_info.description}")
                st.write(f"**Context Window:** {model_info.context_window:,} tokens")
                st.write(f"**Max Output:** {model_info.max_output_tokens:,} tokens")
                st.write(f"**Vision Support:** {'✅' if model_info.supports_vision else '❌'}")
                st.write(f"**Tools Support:** {'✅' if model_info.supports_tools else '❌'}")
                st.write(f"**Cost:** ${model_info.cost_per_1m_input_tokens:.2f} / ${model_info.cost_per_1m_output_tokens:.2f} per 1M tokens")
        
        st.divider()
        
        # Advanced settings
        with st.expander("🎛️ Advanced Settings"):
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=0.7,
                step=0.1,
                help="Higher values make output more random"
            )
            
            max_tokens = st.number_input(
                "Max Tokens",
                min_value=100,
                max_value=4000,
                value=2000,
                step=100,
                help="Maximum tokens to generate"
            )
            
            system_prompt = st.text_area(
                "System Prompt (Optional)",
                placeholder="You are a helpful assistant...",
                help="Set the behavior of the assistant"
            )
        
        st.divider()
        
        # Tools
        st.subheader("🛠️ Tools")
        use_tavily = st.checkbox(
            "Enable Web Search (Tavily)",
            value=False,
            help="Allow assistant to search the web"
        )
        
        st.divider()
        
        # Conversation management
        st.subheader("💬 Conversations")
        
        if st.button("➕ New Conversation", use_container_width=True):
            st.session_state.chat_manager = None
            st.session_state.current_conversation_id = None
            st.session_state.messages = []
            st.rerun()
        
        # List recent conversations
        conversations = ConversationDB.list_conversations(limit=10)
        
        if conversations:
            st.write("Recent:")
            for conv in conversations:
                col1, col2 = st.columns([4, 1])
                with col1:
                    if st.button(
                        f"📝 {conv.title[:30]}...",
                        key=f"conv_{conv.id}",
                        use_container_width=True
                    ):
                        # Load conversation
                        from backend.core.chat_manager import ChatManager
                        st.session_state.chat_manager = ChatManager(conversation_id=conv.id)
                        st.session_state.current_conversation_id = conv.id
                        st.session_state.messages = st.session_state.chat_manager.get_conversation_history()
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"del_{conv.id}"):
                        ConversationDB.delete_conversation(conv.id)
                        st.rerun()
    
    return {
        "provider": provider,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "system_prompt": system_prompt if system_prompt else None,
        "use_tavily": use_tavily
    }
```

**File: `frontend/streamlit/components/chat.py`**
```python
"""
Main chat interface component
"""
import streamlit as st
import asyncio
from backend.core.chat_manager import ChatManager
from backend.database.operations import MessageDB

def render_chat(settings: dict):
    """
    Render the main chat interface
    
    Args:
        settings: Settings dict from sidebar
    """
    st.title("💬 Personal LLM Assistant")
    
    # Initialize chat manager if needed
    if st.session_state.chat_manager is None:
        st.session_state.chat_manager = ChatManager()
        st.session_state.current_conversation_id = st.session_state.chat_manager.conversation_id
        st.session_state.messages = []
    
    # Token counter in header
    if st.session_state.current_conversation_id:
        usage = st.session_state.chat_manager.get_token_usage()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Input Tokens", f"{usage['input_tokens']:,}")
        with col2:
            st.metric("Output Tokens", f"{usage['output_tokens']:,}")
        with col3:
            st.metric("Total Tokens", f"{usage['total_tokens']:,}")
        with col4:
            st.metric("Total Cost", f"${usage['total_cost']:.4f}")
        
        st.divider()
    
    # Display chat messages
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        # Skip system messages
        if role == "system":
            continue
        
        with st.chat_message(role):
            st.markdown(content)
    
    # Chat input
    if prompt := st.chat_input("What can I help you with?"):
        # Add user message to display
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get AI response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run async function
                response = asyncio.run(
                    st.session_state.chat_manager.send_message(
                        user_message=prompt,
                        provider=settings["provider"],
                        model=settings["model"],
                        temperature=settings["temperature"],
                        max_tokens=settings["max_tokens"],
                        system_prompt=settings.get("system_prompt"),
                        stream=False
                    )
                )
                
                st.markdown(response.content)
                
                # Show token info
                st.caption(
                    f"🔢 {response.input_tokens} + {response.output_tokens} = "
                    f"{response.total_tokens} tokens | "
                    f"💰 ${response.cost:.6f} | "
                    f"🤖 {response.provider}/{response.model}"
                )
        
        # Add assistant message to display
        st.session_state.messages.append({
            "role": "assistant",
            "content": response.content
        })
        
        # Auto-generate title after first exchange
        if len(st.session_state.messages) == 2:
            asyncio.run(
                st.session_state.chat_manager.auto_generate_title(
                    provider=settings["provider"],
                    model=settings["model"]
                )
            )
        
        st.rerun()
```

**Testing:**
Run the Streamlit app:
```bash
streamlit run frontend/streamlit/app.py
```

---

## 📋 Phase 4: Multimodal Support (Week 3)

### Task 4.1: File Upload Handler
**Goal:** Add support for image and file uploads.

**File: `backend/utils/file_handler.py`**
```python
"""
File handling utilities for uploads
"""
import io
from PIL import Image
from typing import Tuple, Optional
import magic
from pathlib import Path

class FileHandler:
    """Handle file uploads and processing"""
    
    SUPPORTED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
    SUPPORTED_DOC_TYPES = ['application/pdf', 'text/plain', 'text/markdown']
    MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_file(file_data: bytes, filename: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate uploaded file
        
        Returns:
            (is_valid, mime_type, error_message)
        """
        # Check file size
        if len(file_data) > FileHandler.MAX_IMAGE_SIZE:
            return False, "", "File too large (max 10MB)"
        
        # Detect MIME type
        mime = magic.from_buffer(file_data, mime=True)
        
        # Validate type
        if mime in FileHandler.SUPPORTED_IMAGE_TYPES:
            return True, mime, None
        elif mime in FileHandler.SUPPORTED_DOC_TYPES:
            return True, mime, None
        else:
            return False, mime, f"Unsupported file type: {mime}"
    
    @staticmethod
    def process_image(image_data: bytes) -> Tuple[bytes, str]:
        """
        Process and optimize image
        
        Returns:
            (processed_bytes, mime_type)
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                image = image.convert('RGB')
            
            # Resize if too large (max 2048px on longest side)
            max_size = 2048
            if max(image.size) > max_size:
                ratio = max_size / max(image.size)
                new_size = tuple(int(dim * ratio) for dim in image.size)
                image = image.resize(new_size, Image.Resampling.LANCZOS)
            
            # Save to bytes
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.read(), 'image/jpeg'
            
        except Exception as e:
            raise ValueError(f"Failed to process image: {e}")
    
    @staticmethod
    def extract_text_from_pdf(pdf_data: bytes) -> str:
        """Extract text from PDF"""
        try:
            import PyPDF2
            
            pdf_file = io.BytesIO(pdf_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n\n"
            
            return text.strip()
            
        except Exception as e:
            raise ValueError(f"Failed to extract PDF text: {e}")
```

**File: `frontend/streamlit/components/file_upload.py`**
```python
"""
File upload component for Streamlit
"""
import streamlit as st
from backend.utils.file_handler import FileHandler

def render_file_upload(supports_vision: bool) -> tuple:
    """
    Render file upload widget
    
    Args:
        supports_vision: Whether current model supports vision
        
    Returns:
        (file_data, file_type, mime_type) or (None, None, None)
    """
    if not supports_vision:
        st.info("💡 Select a vision-capable model to upload images")
        return None, None, None
    
    uploaded_file = st.file_uploader(
        "📎 Upload Image or Document",
        type=['png', 'jpg', 'jpeg', 'webp', 'pdf', 'txt', 'md'],
        help="Upload an image or document to include in your message"
    )
    
    if uploaded_file is not None:
        # Read file
        file_data = uploaded_file.read()
        
        # Validate
        is_valid, mime_type, error = FileHandler.validate_file(
            file_data,
            uploaded_file.name
        )
        
        if not is_valid:
            st.error(f"❌ {error}")
            return None, None, None
        
        # Process based on type
        if mime_type.startswith('image/'):
            # Show preview
            st.image(file_data, caption=uploaded_file.name, use_column_width=True)
            
            # Process image
            processed_data, final_mime = FileHandler.process_image(file_data)
            return processed_data, 'image', final_mime
            
        elif mime_type == 'application/pdf':
            # Extract text
            text = FileHandler.extract_text_from_pdf(file_data)
            st.text_area("📄 Extracted Text (Preview)", text[:500] + "...", height=150)
            return text, 'text', 'text/plain'
            
        elif mime_type in ['text/plain', 'text/markdown']:
            # Read text
            text = file_data.decode('utf-8')
            st.text_area("📄 File Content (Preview)", text[:500] + "...", height=150)
            return text, 'text', mime_type
    
    return None, None, None
```

---

### Task 4.2: Integrate File Upload in Chat
**Goal:** Update chat interface to handle file attachments.

Update `frontend/streamlit/components/chat.py` to include file upload functionality. Add file preview and handling for vision models.

---

## 📋 Phase 5: Tools Integration (Week 3-4)

### Task 5.1: Tool Base Class
**Goal:** Create framework for tools.

**File: `backend/tools/base.py`**
```python
"""
Base class for all tools (function calling)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ToolDefinition:
    """Tool definition for function calling"""
    name: str
    description: str
    parameters: Dict[str, Any]

class BaseTool(ABC):
    """Abstract base class for tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """JSON schema for tool parameters"""
        pass
    
    def get_definition(self) -> Dict[str, Any]:
        """Get OpenAI-style tool definition"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
    
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        """
        Execute the tool
        
        Returns:
            String result to send back to LLM
        """
        pass
```

### Task 5.2: Tavily Search Tool
**Goal:** Refactor Tavily search as a tool.

**File: `backend/tools/tavily_search.py`**
```python
"""
Tavily web search tool
"""
from typing import Dict, Any
from tavily import TavilyClient
from backend.tools.base import BaseTool
from backend.config.settings import settings

class TavilySearchTool(BaseTool):
    """Web search using Tavily API"""
    
    def __init__(self):
        if not settings.tavily_api_key:
            raise ValueError("Tavily API key not configured")
        
        self.client = TavilyClient(api_key=settings.tavily_api_key)
    
    @property
    def name(self) -> str:
        return "web_search"
    
    @property
    def description(self) -> str:
        return "Search the web for current information. Use this when you need up-to-date information or facts."
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (1-10)",
                    "default": 5
                }
            },
            "required": ["query"]
        }
    
    async def execute(self, query: str, max_results: int = 5, **kwargs) -> str:
        """Execute web search"""
        try:
            response = self.client.search(
                query=query,
                max_results=max_results,
                search_depth="advanced",
                include_answer=True
            )
            
            # Format results
            result_text = f"# Search Results for: {query}\n\n"
            
            if response.get('answer'):
                result_text += f"## Summary\n{response['answer']}\n\n"
            
            result_text += "## Sources\n"
            for i, result in enumerate(response.get('results', []), 1):
                result_text += f"\n{i}. **{result.get('title', 'Untitled')}**\n"
                result_text += f"   URL: {result.get('url', 'N/A')}\n"
                result_text += f"   {result.get('content', 'No content')}\n"
            
            return result_text
            
        except Exception as e:
            return f"Search failed: {str(e)}"
```

---

## 📋 Phase 6: Testing & Polish (Week 4+)

### Task 6.1: Update Requirements
**Goal:** Create comprehensive requirements file.

**File: `requirements.txt`**
```
# Core dependencies
tavily-python>=0.3.0
google-generativeai>=0.3.0
openai>=1.0.0
python-dotenv>=1.0.0

# Configuration
pydantic>=2.0.0
pydantic-settings>=2.0.0
PyYAML>=6.0.0

# Database
SQLAlchemy>=2.0.0

# File handling
Pillow>=10.0.0
PyPDF2>=3.0.0
python-magic>=0.4.27

# Token counting
tiktoken>=0.5.0

# Async
aiohttp>=3.9.0

# Frontend
streamlit>=1.30.0

# Testing (development)
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-mock>=3.12.0
```

---

## 🎯 Summary Checklist

### Phase 1: Foundation ✅
- [ ] Project restructuring
- [ ] Configuration management
- [ ] Provider base class
- [ ] OpenAI provider
- [ ] Gemini provider
- [ ] Model factory

### Phase 2: Database ✅
- [ ] Database models
- [ ] Database operations
- [ ] Chat manager

### Phase 3: Frontend ✅
- [ ] Basic Streamlit app
- [ ] Sidebar component
- [ ] Chat component
- [ ] Token counter

### Phase 4: Multimodal ✅
- [ ] File upload handler
- [ ] Image processing
- [ ] PDF text extraction
- [ ] Integrate in chat

### Phase 5: Tools ✅
- [ ] Tool base class
- [ ] Tavily search tool
- [ ] Tool integration in chat

### Phase 6: Polish ✅
- [ ] Testing
- [ ] Documentation
- [ ] Error handling
- [ ] Performance optimization

---

## 🚀 Getting Started

1. **Set up environment:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

2. **Configure API keys:**
Create `.env` file:
```
TAVILY_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
GEMINI_API_KEY=your_key_here
```

3. **Run the app:**
```bash
streamlit run frontend/streamlit/app.py
```

---

## 📚 Next Steps After MVP

1. **Anthropic Claude Support**
2. **Streaming responses**
3. **Voice input/output**
4. **Export conversations**
5. **Next.js frontend**
6. **Docker deployment**
7. **Cloud hosting**

---

**Good luck with your implementation! 🚀**

