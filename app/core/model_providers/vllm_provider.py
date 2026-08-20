"""
vLLM provider implementation for GPU-accelerated LLM and embedding services.

This provider interfaces with vLLM deployments for high-performance,
GPU-accelerated model serving in production environments.
"""

import httpx

from app.config import settings
from app.core.model_providers.base import LLMProvider, EmbeddingProvider, LLMError, EmbeddingError


class VLLMLLMProvider(LLMProvider):
    """vLLM implementation of LLM provider for GPU-accelerated serving."""

    def __init__(self, base_url: str | None = None, model: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or settings.vllm_base_url).rstrip("/")
        self.model = model or settings.llm_model
        self.api_key = api_key or settings.vllm_api_key
        self.timeout = settings.llm_timeout

    async def generate(self, prompt: str, **kwargs) -> str:
        """Send a prompt to the vLLM LLM and return its text response.

        Args:
            prompt: The input prompt for text generation
            **kwargs: Additional parameters like temperature, max_tokens

        Returns:
            str: The generated text response

        Raises:
            LLMError: If generation fails
        """
        temperature = kwargs.get('temperature', 0.2)
        max_tokens = kwargs.get('max_tokens', 1024)

        url = f"{self.base_url}/v1/completions"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise LLMError(
                f"Failed to reach vLLM at {url}. "
                f"Is vLLM running and is '{self.model}' available? "
                f"Original error: {exc}"
            ) from exc

        data = response.json()

        # vLLM uses OpenAI-compatible API format
        if "choices" in data and len(data["choices"]) > 0:
            return data["choices"][0]["text"].strip()
        else:
            raise LLMError(f"vLLM returned unexpected response format")

    async def health_check(self) -> bool:
        """Check if vLLM service is healthy."""
        try:
            url = f"{self.base_url}/health"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False

    async def stream_generate(self, prompt: str, **kwargs):
        """Stream text generation using vLLM's streaming API.

        Args:
            prompt: The input prompt for text generation
            **kwargs: Additional parameters

        Yields:
            str: Text chunks as they are generated

        Raises:
            LLMError: If streaming fails
        """
        temperature = kwargs.get('temperature', 0.2)
        max_tokens = kwargs.get('max_tokens', 1024)

        url = f"{self.base_url}/v1/completions"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream("POST", url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.strip():
                            if line.startswith("data: "):
                                data_str = line[6:]  # Remove "data: " prefix
                                if data_str.strip() == "[DONE]":
                                    break
                                try:
                                    import json
                                    data = json.loads(data_str)
                                    if "choices" in data and len(data["choices"]) > 0:
                                        delta = data["choices"][0].get("text", "")
                                        if delta:
                                            yield delta
                                except json.JSONDecodeError:
                                    continue
        except httpx.HTTPError as exc:
            raise LLMError(f"vLLM streaming failed: {exc}") from exc


class VLLMEmbeddingProvider(EmbeddingProvider):
    """vLLM implementation of embedding provider for GPU acceleration."""

    def __init__(self, base_url: str | None = None, model: str | None = None, api_key: str | None = None):
        self.base_url = (base_url or settings.vllm_base_url).rstrip("/")
        self.model = model or settings.embedding_model
        self.api_key = api_key or settings.vllm_api_key
        self.timeout = settings.embedding_timeout
        self.batch_size = settings.gpu_batch_size_embeddings

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
        """Generate embeddings for multiple texts with GPU batching optimization.

        Args:
            texts: List of input texts to embed

        Returns:
            list[list[float]]: List of embedding vectors

        Raises:
            EmbeddingError: If batch embedding fails
        """
        if not texts:
            return []

        # Process in batches for GPU optimization
        all_embeddings = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_embeddings = await self._process_batch(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings

    async def _process_batch(self, texts: list[str]) -> list[list[float]]:
        """Process a single batch of texts.

        Args:
            texts: Batch of texts to embed

        Returns:
            list[list[float]]: Embedding vectors for the batch

        Raises:
            EmbeddingError: If batch processing fails
        """
        url = f"{self.base_url}/v1/embeddings"
        payload = {
            "model": self.model,
            "input": texts,
        }

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise EmbeddingError(
                f"Failed to generate embeddings with vLLM at {url}. "
                f"Is vLLM running and is '{self.model}' available? "
                f"Original error: {exc}"
            ) from exc

        data = response.json()

        # vLLM uses OpenAI-compatible API format
        if "data" in data:
            # OpenAI format returns data as a list of embedding objects
            return [item["embedding"] for item in data["data"]]
        else:
            raise EmbeddingError(f"vLLM returned unexpected response format")

    async def health_check(self) -> bool:
        """Check if vLLM service is healthy."""
        try:
            url = f"{self.base_url}/health"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                return response.status_code == 200
        except Exception:
            return False
