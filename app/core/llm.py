"""
LLM client - sends a prompt to a configured model and gets back an answer.

This now supports multiple providers (Ollama, vLLM) through the provider
abstraction layer while maintaining backward compatibility.
"""

from app.core.model_providers import get_llm_provider
from app.core.model_providers.base import LLMError


# Maintain backward compatibility with existing imports
class OllamaLLMClient:
    """
    Backward-compatible wrapper for LLM client.

    This class now delegates to the configured provider via the factory pattern,
    allowing seamless switching between Ollama, vLLM, and future providers.
    """

    def __init__(self, base_url: str | None = None, model: str | None = None):
        # Store configuration for potential provider-specific initialization
        self._base_url = base_url
        self._model = model
        # Get the configured provider (will use settings from factory)
        self._provider = get_llm_provider()

    async def generate(self, prompt: str, temperature: float = 0.2) -> str:
        """Send a prompt to the LLM and return its text response.

        Args:
            prompt: The input prompt for text generation
            temperature: Controls randomness (0.2 = more deterministic)

        Returns:
            str: The generated text response

        Raises:
            LLMError: If generation fails

        Note:
            temperature defaults low (0.2) because for a document Q&A tool we
            want faithful, consistent answers grounded in the retrieved text,
            not creative variation.
        """
        return await self._provider.generate(prompt, temperature=temperature)


# Convenience instance for backward compatibility
llm_client = OllamaLLMClient()
