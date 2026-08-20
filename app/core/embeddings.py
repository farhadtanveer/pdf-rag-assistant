"""
Embedding client - turns text into vectors using configured model provider.

This now supports multiple providers (Ollama, vLLM) through the provider
abstraction layer while maintaining backward compatibility.
"""

from app.core.model_providers import get_embedding_provider
from app.core.model_providers.base import EmbeddingError


# Maintain backward compatibility with existing imports
class OllamaEmbeddingClient:
    """
    Backward-compatible wrapper for embedding client.

    This class now delegates to the configured provider via the factory pattern,
    allowing seamless switching between Ollama, vLLM, and future providers.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None):
        # Store configuration for potential provider-specific initialization
        self._base_url = base_url
        self._model = model
        # Get the configured provider (will use settings from factory)
        self._provider = get_embedding_provider()

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in one request using the configured provider.

        Args:
            texts: List of raw text strings (e.g. chunk texts).

        Returns:
            One embedding vector per input text, same order.

        Raises:
            EmbeddingError: If embedding generation fails
        """
        return await self._provider.embed_batch(texts)

    async def embed_text(self, text: str) -> list[float]:
        """Convenience method for embedding a single string (e.g. a question).

        Args:
            text: The input text to embed

        Returns:
            list[float]: The embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        return await self._provider.embed(text)


# Convenience instance for backward compatibility
embedding_client = OllamaEmbeddingClient()
