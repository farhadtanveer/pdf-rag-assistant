"""
Query service: orchestrates embed question -> retrieve -> prompt -> answer.

Note on citations: sources returned to the user are built directly from
what the vector store actually retrieved, NOT parsed out of the LLM's
text response. This means even if the model forgets to cite properly in
its answer text, the UI still shows the real, verifiable source list.
The LLM's inline citations are a nice-to-have on top of this guarantee,
not a replacement for it.
"""

from app.config import settings
from app.core.embeddings import OllamaEmbeddingClient
from app.core.llm import OllamaLLMClient
from app.core.prompts import build_answer_prompt
from app.core.vector_store import vector_store
from app.models.schemas import AskResponse, SourceReference

_embedding_client = OllamaEmbeddingClient()
_llm_client = OllamaLLMClient()

_EXCERPT_LENGTH = 200  # characters shown in the source preview


async def answer_question(question: str, top_k: int | None = None) -> AskResponse:
    """Run the full RAG pipeline for one user question."""
    # explicit `is not None` check so an intentional top_k=0 isn't
    # silently overridden by the default (0 is falsy in Python, `or` would
    # have masked it)
    k = top_k if top_k is not None else settings.top_k_chunks

    question_embedding = await _embedding_client.embed_text(question)
    retrieved = vector_store.query(question_embedding, top_k=k)

    if not retrieved:
        return AskResponse(
            answer="No documents have been uploaded yet, so I have nothing to search.",
            sources=[],
        )

    prompt = build_answer_prompt(question, retrieved)
    answer_text = await _llm_client.generate(prompt)

    sources = [
        SourceReference(
            source_filename=chunk["source_filename"],
            page_number=chunk["page_number"],
            excerpt=_truncate(chunk["text"]),
        )
        for chunk in retrieved
    ]

    return AskResponse(answer=answer_text, sources=sources)


def _truncate(text: str) -> str:
    if len(text) <= _EXCERPT_LENGTH:
        return text
    return text[:_EXCERPT_LENGTH].rsplit(" ", 1)[0] + "..."
