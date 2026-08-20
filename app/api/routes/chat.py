"""
Question-answering endpoint.
"""

from fastapi import APIRouter, HTTPException

from app.core.embeddings import EmbeddingError
from app.core.llm import LLMError
from app.models.schemas import AskRequest, AskResponse
from app.services.query_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest) -> AskResponse:
    try:
        return await answer_question(request.question, top_k=request.top_k)
    except (EmbeddingError, LLMError) as exc:
        # These indicate Ollama isn't reachable/configured correctly -
        # a 503 tells the frontend "the service is down", not "your request is bad".
        raise HTTPException(status_code=503, detail=str(exc)) from exc
