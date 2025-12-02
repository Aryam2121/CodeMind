"""
Advanced LLM Configuration for CodeMind
Supports multiple LLM providers with fallback
"""

import os
from typing import Optional, Dict, Any
from langchain_openai import ChatOpenAI
import logging

logger = logging.getLogger(__name__)

class LLMConfig:
    """Advanced LLM configuration with multiple providers"""
    
    # Supported models
    OPENAI_MODELS = {
        'gpt-4-turbo': {'context': 128000, 'cost_per_1k': 0.01},
        'gpt-4': {'context': 8192, 'cost_per_1k': 0.03},
        'gpt-3.5-turbo': {'context': 16385, 'cost_per_1k': 0.002},
        'gpt-3.5-turbo-16k': {'context': 16385, 'cost_per_1k': 0.003}
    }
    
    @staticmethod
    def get_llm(
        provider: str = "openai",
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ):
        """
        Get configured LLM instance
        
        Args:
            provider: LLM provider (openai, anthropic, etc.)
            model: Specific model name
            temperature: Creativity (0.0-2.0)
            max_tokens: Max response length
            streaming: Enable streaming responses
        """
        use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
        
        if use_mock:
            logger.info("Using mock LLM (development mode)")
            from rag import MockLLM
            return MockLLM()
        
        if provider == "openai":
            return LLMConfig._get_openai_llm(model, temperature, max_tokens, streaming)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    @staticmethod
    def _get_openai_llm(
        model: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
        streaming: bool
    ):
        """Get OpenAI LLM with configuration"""
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            logger.warning("No OPENAI_API_KEY found, falling back to mock LLM")
            from rag import MockLLM
            return MockLLM()
        
        # Default model
        if not model:
            model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        
        # Validate model
        if model not in LLMConfig.OPENAI_MODELS:
            logger.warning(f"Unknown model {model}, falling back to gpt-3.5-turbo")
            model = "gpt-3.5-turbo"
        
        # Configuration
        config = {
            'openai_api_key': api_key,
            'model': model,
            'temperature': temperature,
            'streaming': streaming
        }
        
        if max_tokens:
            config['max_tokens'] = max_tokens
        
        logger.info(f"Initializing OpenAI LLM: {model} (temp={temperature})")
        
        return ChatOpenAI(**config)
    
    @staticmethod
    def get_model_info(model: str) -> Dict[str, Any]:
        """Get information about a model"""
        if model in LLMConfig.OPENAI_MODELS:
            return {
                'provider': 'openai',
                'model': model,
                **LLMConfig.OPENAI_MODELS[model]
            }
        return {'error': 'Model not found'}
    
    @staticmethod
    def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimate cost for API call"""
        info = LLMConfig.get_model_info(model)
        if 'cost_per_1k' in info:
            total_tokens = input_tokens + output_tokens
            return (total_tokens / 1000) * info['cost_per_1k']
        return 0.0


class LLMSettings:
    """User-configurable LLM settings"""
    
    def __init__(self):
        self.model = os.getenv("LLM_MODEL", "gpt-3.5-turbo")
        self.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        self.max_tokens = int(os.getenv("LLM_MAX_TOKENS", "1000")) if os.getenv("LLM_MAX_TOKENS") else None
        self.streaming = os.getenv("LLM_STREAMING", "false").lower() == "true"
    
    def update(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        streaming: Optional[bool] = None
    ):
        """Update settings"""
        if model:
            self.model = model
        if temperature is not None:
            self.temperature = temperature
        if max_tokens:
            self.max_tokens = max_tokens
        if streaming is not None:
            self.streaming = streaming
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'streaming': self.streaming
        }
    
    def get_llm(self):
        """Get LLM instance with current settings"""
        return LLMConfig.get_llm(
            provider="openai",
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            streaming=self.streaming
        )


# Global settings instance
_llm_settings = None

def get_llm_settings() -> LLMSettings:
    """Get or create LLM settings instance"""
    global _llm_settings
    if _llm_settings is None:
        _llm_settings = LLMSettings()
    return _llm_settings
