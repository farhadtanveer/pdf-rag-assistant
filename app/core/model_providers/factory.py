"""
Factory for creating model provider instances based on configuration.

This factory pattern enables easy switching between different model providers
(Ollama, vLLM, OpenAI) based on runtime configuration without changing application code.
"""

from app.config import settings, ModelProvider
from app.core.model_providers.base import LLMProvider, EmbeddingProvider
from app.core.model_providers.ollama_provider import OllamaLLMProvider, OllamaEmbeddingProvider
from app.core.model_providers.vllm_provider import VLLMLLMProvider, VLLMEmbeddingProvider


def get_llm_provider() -> LLMProvider:
    """
    Get the configured LLM provider instance.

    Returns:
        LLMProvider: The configured LLM provider instance

    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = settings.model_provider

    if provider == ModelProvider.OLLAMA:
        return OllamaLLMProvider()
    elif provider == ModelProvider.VLLM:
        if not settings.vllm_base_url:
            raise ValueError(
                "vLLM provider selected but VLLM_BASE_URL not configured. "
                "Please set VLLM_BASE_URL in your environment."
            )
        return VLLMLLMProvider()
    elif provider == ModelProvider.OPENAI:
        raise ValueError(
            "OpenAI provider not yet implemented. "
            "Please use OLLAMA or VLLM providers."
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


def get_embedding_provider() -> EmbeddingProvider:
    """
    Get the configured embedding provider instance.

    Returns:
        EmbeddingProvider: The configured embedding provider instance

    Raises:
        ValueError: If the configured provider is not supported
    """
    provider = settings.model_provider

    if provider == ModelProvider.OLLAMA:
        return OllamaEmbeddingProvider()
    elif provider == ModelProvider.VLLM:
        if not settings.vllm_base_url:
            raise ValueError(
                "vLLM provider selected but VLLM_BASE_URL not configured. "
                "Please set VLLM_BASE_URL in your environment."
            )
        return VLLMEmbeddingProvider()
    elif provider == ModelProvider.OPENAI:
        raise ValueError(
            "OpenAI provider not yet implemented. "
            "Please use OLLAMA or VLLM providers."
        )
    else:
        raise ValueError(f"Unsupported model provider: {provider}")


async def check_provider_health() -> dict[str, bool]:
    """
    Check health status of configured model providers.

    Returns:
        dict: Health status for LLM and embedding providers

    Example:
        {
            "llm": True,
            "embedding": True,
            "provider": "ollama"
        }
    """
    llm_provider = get_llm_provider()
    embedding_provider = get_embedding_provider()

    llm_healthy = await llm_provider.health_check()
    embedding_healthy = await embedding_provider.health_check()

    return {
        "provider": settings.model_provider,
        "llm": llm_healthy,
        "embedding": embedding_healthy,
        "gpu_enabled": settings.gpu_enabled,
    }
