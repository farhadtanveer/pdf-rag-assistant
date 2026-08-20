"""
Ingestion service: orchestrates parse -> chunk -> embed -> store.

This is the only place that knows the FULL upload pipeline. The API route
just calls one function here; it doesn't know or care about PDF parsing,
chunking, or embeddings internally. That separation is what lets you test
or change any single step without touching the HTTP layer.
"""

from app.core.chunker import chunk_document
from app.core.embeddings import OllamaEmbeddingClient
from app.core.pdf_parser import parse_pdf
from app.core.vector_store import vector_store
from app.models.schemas import UploadResponse

_embedding_client = OllamaEmbeddingClient()


async def ingest_pdf(file_path: str, original_filename: str) -> UploadResponse:
    """Run the full ingestion pipeline for one uploaded PDF.

    Args:
        file_path: Where the uploaded file currently sits on disk.
        original_filename: The name to store as citation metadata (so
            citations show "datasheet.pdf" rather than a random temp path).
    """
    pages = parse_pdf(file_path)
    chunks = chunk_document(pages, source_filename=original_filename)

    embeddings = await _embedding_client.embed_batch([c.text for c in chunks])
    vector_store.add_chunks(chunks, embeddings)

    return UploadResponse(
        filename=original_filename,
        total_pages=len(pages),
        total_chunks=len(chunks),
    )
