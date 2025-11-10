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

