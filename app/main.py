"""
Application entrypoint.

Run with:  uvicorn app.main:app --reload
Docs at:   http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents
from app.config import settings
from app.core.model_providers import check_provider_health

app = FastAPI(
    title="Internal Document RAG Assistant",
    description="Ask questions about uploaded PDFs (supplier datasheets, technical docs) and get answers with page-level citations.",
    version="0.2.0",
)

# Allows a local React dev server to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)


@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Enhanced health check that verifies:
    - API server is running
    - Model provider is accessible
    - GPU configuration status

    Returns comprehensive health status for monitoring and debugging.
    """
    base_health = {"status": "ok", "api": "healthy"}

    try:
        provider_health = await check_provider_health()
        base_health.update({
            "model_provider": provider_health["provider"],
            "llm_service": "healthy" if provider_health["llm"] else "unhealthy",
            "embedding_service": "healthy" if provider_health["embedding"] else "unhealthy",
            "gpu_enabled": provider_health["gpu_enabled"],
        })
    except Exception as exc:
        base_health.update({
            "model_provider": "error",
            "llm_service": f"error: {str(exc)}",
            "embedding_service": f"error: {str(exc)}",
            "gpu_enabled": settings.gpu_enabled,
        })

    return base_health
