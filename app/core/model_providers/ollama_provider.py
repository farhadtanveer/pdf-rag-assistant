"""
Ollama provider implementation for LLM and embedding services.

This provider interfaces with local Ollama instances for development
and small-scale deployments.
"""

import httpx

from app.config import settings
from app.core.model_providers.base import LLMProvider, EmbeddingProvider, LLMError, EmbeddingError


class OllamaLLMProvider(LLMProvider):
    """Ollama implementation of LLM provider for local development."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.llm_model
        self.timeout = settings.llm_timeout

    async def generate(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the Ollama LLM and return its text response.

        Args:
            prompt: The input prompt for text generation
            **kwargs: Additional parameters like temperature

        Returns:
            str: The generated text response

        Raises:
            LLMError: If generation fails
        """
        temperature = kwargs.get('temperature', 0.2)
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(
                f"Failed to reach Ollama at {url}. "
                f"Is Ollama running and is '{self.model}' available? "
                f"(ollama pull {self.model}) Original error: {exc}"
            ) from exc

        data = response.json()
        answer = data.get("response")
        if answer is None:
            raise LLMError(f"Ollama returned no response for model '{self.model}'.")

        return answer.strip()

    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            url = f"{self.base_url}/api/tags"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

    async def stream_generate(self, prompt: str, **kwargs):
        """Stream text generation (placeholder for future implementation)."""
        raise NotImplementedError("Streaming not implemented for Ollama provider yet")


class OllamaEmbeddingProvider(EmbeddingProvider):
    """Ollama implementation of embedding provider."""

    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.embedding_model
        self.timeout = settings.embedding_timeout

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: The input text to embed

        Returns:
            list[float]: The embedding vector

        Raises:
            EmbeddingError: If embedding generation fails
        """
        embeddings = await self.embed_batch([text])
        return embeddings[0]

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of input texts to embed

        Returns:
            list[list[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If batch embedding fails
        """
        if not texts:
            return []

        url = f"{self.base_url}/api/embed"
        payload = {
            "model": self.model,
            "input": texts,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingError(
                f"Failed to generate embeddings with Ollama at {url}. "
                f"Is Ollama running and is '{self.model}' available? "
                f"(ollama pull {self.model}) Original error: {exc}"
            ) from exc

        data = response.json()

        # Ollama returns embeddings in different formats depending on input size
        if "embeddings" in data:
            return data["embeddings"]
        elif "embedding" in data:
            return [data["embedding"]]
        else:
            raise EmbeddingError(f"Ollama returned unexpected response format")

    async def health_check(self) -> bool:
        """Check if Ollama service is healthy."""
        try:
            url = f"{self.base_url}/api/tags"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False
