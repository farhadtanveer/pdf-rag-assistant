"""
Central configuration for the whole application.

Every tunable value (model names, chunk size, ports, paths) lives here and
ONLY here. If you want to swap the LLM model, change the Ollama host, or
move to the office server later, this is the one file you touch.

Values are loaded from environment variables / a .env file, with sensible
local-development defaults so the app runs out of the box.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # --- Ollama connection -------------------------------------------------
    # When you move this to the office server, this is usually the ONLY
    # thing that changes (e.g. http://192.168.1.50:11434).
    ollama_base_url: str = "http://localhost:11434"

    # --- Models --------------------------------------------------------
    # Small models for local laptop development. Swap to bigger models
    # once deployed on the office GPU server.
    embedding_model: str = "bge-m3"
    llm_model: str = "phi4-mini"

    # --- Chunking ------------------------------------------------------
    chunk_size: int = 800          # characters per chunk (simple, predictable)
    chunk_overlap: int = 150       # overlap so we don't cut sentences in half

    # --- Retrieval -------------------------------------------------------
    top_k_chunks: int = 5          # how many chunks to retrieve per question

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
