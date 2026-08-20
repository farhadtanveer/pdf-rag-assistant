"""
Abstract base classes for model providers.

All model providers (Ollama, vLLM, OpenAI) must implement these interfaces
to ensure consistent behavior across different deployment scenarios.
"""

from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """
    Abstract interface for Large Language Model providers.

    Implementations must support:
    - Text generation with prompts
    - Health checks for service availability
    - Optional streaming support for future enhancement
    """

    @abstractmethod
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text response for a given prompt.

        Args:
            prompt: The input prompt for text generation
            **kwargs: Additional provider-specific parameters

        Returns:
            str: The generated text response

        Raises:
            LLMError: If the generation fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the LLM service is healthy and available.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        pass

    @abstractmethod
    async def stream_generate(self, prompt: str, **kwargs):
        """
        Stream text generation (optional, for future implementation).

        Args:
            prompt: The input prompt for text generation
            **kwargs: Additional provider-specific parameters

        Returns:
            Async generator yielding text chunks
        """
        pass


class EmbeddingProvider(ABC):
    """
    Abstract interface for embedding model providers.

    Implementations must support:
    - Single text embedding
    - Batch text embedding for GPU optimization
    - Health checks for service availability
    """

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The input text to embed

        Returns:
            list[float]: The embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts (optimized for GPU).

        Args:
            texts: List of input texts to embed

        Returns:
            list[list[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If batch embedding fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the embedding service is healthy and available.

        Returns:
            bool: True if service is healthy, False otherwise
        """
        pass


class LLMError(Exception):
    """Exception raised when LLM generation fails."""
    pass


class EmbeddingError(Exception):
    """Exception raised when embedding generation fails."""
    pass
