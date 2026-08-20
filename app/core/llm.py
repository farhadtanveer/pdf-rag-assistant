"""
LLM client - sends a prompt to a local Ollama model and gets back an answer.

Same philosophy as embeddings.py: a small, readable wrapper. Not streaming
yet (v1 keeps things simple) - see README "Next steps" for how to add
streaming later without restructuring anything else.
"""

import httpx

from app.config import settings


class LLMError(Exception):
    """Raised when Ollama fails to generate a response."""


class OllamaLLMClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.model = model or settings.llm_model

    async def generate(self, prompt: str, temperature: float = 0.2) -> str:
        """Send a prompt to the LLM and return its text response.

        temperature defaults low (0.2) because for a document Q&A tool we
        want faithful, consistent answers grounded in the retrieved text,
        not creative variation.
        """
        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": temperature},
        }

        async with httpx.AsyncClient(timeout=180.0) as client:
            try:
                response = await client.post(url, json=payload)
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise LLMError(
                    f"Failed to reach Ollama at {url}. "
                    f"Is Ollama running and is '{self.model}' pulled? "
                    f"(ollama pull {self.model}) Original error: {exc}"
                ) from exc

        data = response.json()
        answer = data.get("response")
        if answer is None:
            raise LLMError(f"Ollama returned no response for model '{self.model}'.")
        return answer.strip()
