"""
Application entrypoint.

Run with:  uvicorn app.main:app --reload
Docs at:   http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat, documents
from app.config import settings

app = FastAPI(
    title="Internal Document RAG Assistant",
    description="Ask questions about uploaded PDFs (supplier datasheets, technical docs) and get answers with page-level citations.",
    version="0.1.0",
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
def health_check() -> dict:
    """Simple liveness check - also useful to confirm the server is up
    before you start debugging why Ollama calls are failing."""
    return {"status": "ok"}
