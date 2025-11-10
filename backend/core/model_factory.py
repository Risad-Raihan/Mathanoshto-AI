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

