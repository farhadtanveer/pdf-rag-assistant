"""
Model provider abstraction layer.

This package provides a unified interface for different model providers
(Ollama, vLLM, OpenAI) to enable GPU scalability and flexible deployment.
"""

from app.core.model_providers.base import LLMProvider, EmbeddingProvider
from app.core.model_providers.factory import (
    get_llm_provider,
    get_embedding_provider,
    check_provider_health,
)

__all__ = [
    "LLMProvider",
    "EmbeddingProvider",
    "get_llm_provider",
    "get_embedding_provider",
    "check_provider_health",
]
