"""
Central configuration for the whole application.

Every tunable value (model names, chunk size, ports, paths) lives here and
ONLY here. If you want to swap the LLM model, change the Ollama host, or
move to the office server later, this is the one file you touch.

Values are loaded from environment variables / a .env file, with sensible
local-development defaults so the app runs out of the box.
"""

from enum import Enum
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ModelProvider(str, Enum):
    """Supported model providers for LLM and embedding services."""
    OLLAMA = "ollama"
    VLLM = "vllm"
    OPENAI = "openai"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Server Configuration ---------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000

    # --- Model Provider Selection -----------------------------------------
    # Choose between ollama (local), vllm (GPU deployment), or openai (cloud)
    model_provider: ModelProvider = ModelProvider.OLLAMA

    # --- Ollama Configuration ---------------------------------------------
    # Local development setup - default for laptop deployment
    ollama_base_url: str = "http://localhost:11434"

    # --- vLLM Configuration (GPU Deployment) -----------------------------
    # GPU server deployment for scalable model hosting
    vllm_base_url: str | None = None
    vllm_api_key: str | None = None

    # --- OpenAI Configuration (Optional) ----------------------------------
    openai_api_key: str | None = None

    # --- Models -----------------------------------------------------------
    # Small models for local laptop development. Swap to bigger models
    # once deployed on the office GPU server.
    embedding_model: str = "bge-m3"
    llm_model: str = "phi4-mini"

    # --- Chunking --------------------------------------------------------
    chunk_size: int = 800          # characters per chunk (simple, predictable)
    chunk_overlap: int = 150       # overlap so we don't cut sentences in half

    # --- Retrieval ---------------------------------------------------------
    top_k_chunks: int = 5          # how many chunks to retrieve per question

    # --- GPU Optimization Settings ----------------------------------------
    gpu_enabled: bool = False      # Set to true when using GPU deployment
    gpu_batch_size_embeddings: int = 32   # Batch size for embedding operations
    gpu_batch_size_llm: int = 4           # Concurrent LLM requests
    max_concurrent_requests: int = 8     # Maximum concurrent API requests
    enable_streaming: bool = False        # Enable streaming responses (future)

    # --- Performance Tuning -----------------------------------------------
    embedding_timeout: int = 120   # Timeout for embedding operations (seconds)
    llm_timeout: int = 300         # Timeout for LLM generation (seconds)

    # --- Storage paths ---------------------------------------------------
    base_dir: Path = Path(__file__).resolve().parent.parent
    upload_dir: Path = base_dir / "data" / "uploads"
    chroma_persist_dir: Path = base_dir / "data" / "chroma_db"
    chroma_collection_name: str = "documents"

    # --- API ---------------------------------------------------------------
    cors_allow_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


# Single shared instance imported everywhere else in the app.
settings = Settings()

# Make sure the storage directories always exist.
settings.upload_dir.mkdir(parents=True, exist_ok=True)
settings.chroma_persist_dir.mkdir(parents=True, exist_ok=True)
