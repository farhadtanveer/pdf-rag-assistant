"""
Document upload endpoint.

This route deliberately does almost nothing itself - it saves the upload
to disk and hands off to the ingestion service. Keeping HTTP concerns
(file upload handling, status codes) separate from business logic (parsing,
chunking, embedding) is what makes each piece independently testable.
"""

import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile

from app.config import settings
from app.core.pdf_parser import PDFParseError
from app.core.vector_store import vector_store
from app.models.schemas import UploadResponse
from app.services.ingestion_service import ingest_pdf

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("")
def list_documents() -> dict[str, int]:
    """List every document currently ingested, with chunk counts.

    A chunk count roughly double what you'd expect for a file's size is
    the tell-tale sign it was uploaded twice before the dedup fix.
    """
    return vector_store.list_source_filenames()


@router.delete("/{source_filename}")
def delete_document(source_filename: str) -> dict:
    deleted_count = vector_store.delete_document(source_filename)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"No chunks found for '{source_filename}'.")
    return {"source_filename": source_filename, "chunks_deleted": deleted_count}


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile) -> UploadResponse:
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save with a random name on disk to avoid collisions, but keep the
    # original filename separately for citations shown to the user.
    temp_path = settings.upload_dir / f"{uuid.uuid4()}.pdf"
    contents = await file.read()
    temp_path.write_bytes(contents)

    try:
        result = await ingest_pdf(str(temp_path), original_filename=file.filename)
    except PDFParseError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    finally:
        # We only needed the file on disk long enough to parse it once.
        Path(temp_path).unlink(missing_ok=True)

    return result
