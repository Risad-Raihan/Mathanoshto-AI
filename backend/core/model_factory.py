"""
Model Factory - Central hub for managing LLM providers and models
"""
from typing import Dict, List, Optional
from enum import Enum

from backend.providers.base import BaseLLMProvider, ModelInfo
from backend.providers.openai_provider import OpenAIProvider
from backend.providers.gemini_provider import GeminiProvider
from backend.providers.anthropic_provider import AnthropicProvider
from backend.config.settings import settings
from backend.database.user_operations import UserAPIKeyDB

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
        
        # Anthropic
        if settings.anthropic_api_key:
            try:
                self._providers[ProviderType.ANTHROPIC] = AnthropicProvider()
                print(f"✓ Loaded Anthropic provider")
            except Exception as e:
                print(f"⚠️ Failed to load Anthropic: {e}")
    
    def get_provider(self, provider_type: str) -> Optional[BaseLLMProvider]:
        """Get a provider instance"""
        return self._providers.get(provider_type)
    
    def get_user_provider(self, user_id: int, provider_type: str) -> Optional[BaseLLMProvider]:
        """
        Get a provider instance for a specific user using their API keys from database
        
        Args:
            user_id: User ID
            provider_type: Provider type (openai, gemini, anthropic)
            
        Returns:
            Initialized provider or None if API key not found
        """
        try:
            # Get user's API keys from database
            user_keys = UserAPIKeyDB.get_all_user_keys(user_id)
            
            if provider_type == ProviderType.OPENAI:
                api_key = user_keys.get('openai')
                if not api_key:
                    # Fallback to settings if no user key
                    api_key = settings.openai_api_key
                if api_key:
                    base_url = user_keys.get('openai_base_url')
                    return OpenAIProvider(api_key=api_key, base_url=base_url)
                    
            elif provider_type == ProviderType.GEMINI:
                api_key = user_keys.get('gemini')
                if not api_key:
                    # Fallback to settings if no user key
                    api_key = settings.gemini_api_key
                if api_key:
                    return GeminiProvider(api_key=api_key)
                    
            elif provider_type == ProviderType.ANTHROPIC:
                api_key = user_keys.get('anthropic')
                if not api_key:
                    # Fallback to settings if no user key
                    api_key = settings.anthropic_api_key
                if api_key:
                    return AnthropicProvider(api_key=api_key)
            
        except Exception as e:
            print(f"⚠️ Failed to load provider {provider_type} for user {user_id}: {e}")
            # Fallback to global provider
            return self.get_provider(provider_type)
        
        return None
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self._providers.keys())
    
    def get_user_available_providers(self, user_id: int) -> List[str]:
        """
        Get list of available providers for a specific user based on their API keys
        
        Args:
            user_id: User ID
            
        Returns:
            List of provider names that the user has API keys for
        """
        try:
            user_keys = UserAPIKeyDB.get_all_user_keys(user_id)
            available = []
            
            if user_keys.get('openai') or settings.openai_api_key:
                available.append(ProviderType.OPENAI)
            if user_keys.get('gemini') or settings.gemini_api_key:
                available.append(ProviderType.GEMINI)
            if user_keys.get('anthropic') or settings.anthropic_api_key:
                available.append(ProviderType.ANTHROPIC)
                
            return available
        except Exception as e:
            print(f"⚠️ Failed to get user providers: {e}")
            return self.get_available_providers()
    
    def get_all_models(self) -> Dict[str, List[ModelInfo]]:
        """Get all available models grouped by provider"""
        all_models = {}
        
        for provider_name, provider in self._providers.items():
            all_models[provider_name] = provider.get_available_models()
        
        return all_models
    
    def get_models_for_provider(self, provider_type: str, user_id: Optional[int] = None) -> List[ModelInfo]:
        """
        Get models for a specific provider
        
        Args:
            provider_type: Provider type
            user_id: Optional user ID to get user-specific provider
            
        Returns:
            List of available models
        """
        # If user_id provided, get user-specific provider
        if user_id:
            provider = self.get_user_provider(user_id, provider_type)
        else:
            provider = self.get_provider(provider_type)
            
        if provider:
            return provider.get_available_models()
        return []
    
    def get_model_info(self, provider_type: str, model_name: str, user_id: Optional[int] = None) -> Optional[ModelInfo]:
        """
        Get info for a specific model
        
        Args:
            provider_type: Provider type
            model_name: Model name
            user_id: Optional user ID to get user-specific provider
            
        Returns:
            ModelInfo or None
        """
        # If user_id provided, get user-specific provider
        if user_id:
            provider = self.get_user_provider(user_id, provider_type)
        else:
            provider = self.get_provider(provider_type)
            
        if provider:
            return provider.get_model_info(model_name)
        return None

# Global factory instance
model_factory = ModelFactory()

