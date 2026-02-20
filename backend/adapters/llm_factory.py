"""LLM factory"""
from adapters.llm_interface import LLMInterface
from adapters.openai_adapter import OpenAIAdapter
from adapters.anthropic_adapter import AnthropicAdapter
from utils.config import settings


def get_llm() -> LLMInterface:
    """Get LLM adapter based on configuration"""
    provider = settings.LLM_PROVIDER.lower()
    
    if provider == "openai":
        return OpenAIAdapter()
    elif provider == "anthropic":
        return AnthropicAdapter()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}")
