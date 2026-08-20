"""
Embedding client - turns text into vectors using a local Ollama model.

This is intentionally a thin wrapper around Ollama's HTTP API rather than
a heavier library. It's ~30 lines, you can read the whole thing in one
sitting, and if Ollama's API ever changes, only this one file needs updating.
"""

import httpx

from app.config import settings


class EmbeddingError(Exception):
    """Raised when Ollama fails to return an embedding."""


class OllamaEmbeddingClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.embedding_model

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts in one request.

        Args:
            texts: List of raw text strings (e.g. chunk texts).

        Returns:
            One embedding vector per input text, same order.
        """
        if not texts:
            return []

        url = f"{self.base_url}/api/embed"
        payload = {"model": self.model, "input": texts}

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise EmbeddingError(
                    f"Failed to reach Ollama at {url}. "
                    f"Is Ollama running and is '{self.model}' pulled? "
                    f"(ollama pull {self.model}) Original error: {exc}"
                ) from exc

        data = response.json()
        embeddings = data.get("embeddings")
        if not embeddings:
            raise EmbeddingError(f"Ollama returned no embeddings for model '{self.model}'.")
        return embeddings

    async def embed_text(self, text: str) -> list[float]:
        """Convenience method for embedding a single string (e.g. a question)."""
        results = await self.embed_batch([text])
        return results[0]
