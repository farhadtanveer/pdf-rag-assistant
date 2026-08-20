"""
Chunking: splitting page text into small overlapping pieces suitable for
embedding.

Design decision: we chunk WITHIN a page, never across pages. This costs us
a little bit of context at page boundaries, but it guarantees every chunk
has exactly one correct page number - which matters more for a tool whose
whole purpose is trustworthy citations.

The splitting itself uses a simple character-based sliding window. It's not
as linguistically clever as sentence-aware splitting, but it's predictable,
fast, has no extra dependencies, and is easy to reason about - a good
starting point that can be upgraded later without touching any other layer.
"""

import hashlib

from app.config import settings
from app.models.schemas import Chunk, PageContent


def _deterministic_chunk_id(source_filename: str, page_number: int, chunk_index: int) -> str:
    """Build a stable ID from WHERE a chunk came from, not a random uuid.

    This means re-uploading the same file produces the SAME chunk IDs,
    so storing it again overwrites the old copy instead of duplicating it
    (see vector_store.py, which upserts rather than blindly adds).
    """
    key = f"{source_filename}:{page_number}:{chunk_index}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def chunk_page(page: PageContent, source_filename: str) -> list[Chunk]:
    """Split a single page's text into overlapping chunks.

    Args:
        page: The extracted page content (text + page number).
        source_filename: Original filename, stored on every chunk so we
            know which document a citation refers to.

    Returns:
        List of Chunk objects, empty if the page text is shorter than
        one chunk (in which case the whole page becomes a single chunk).
    """
    text = page.text
    size = settings.chunk_size
    overlap = settings.chunk_overlap
    step = size - overlap

    chunks: list[Chunk] = []
    start = 0
    index = 0

    while start < len(text):
        piece = text[start : start + size].strip()
        if piece:  # avoid empty chunks from trailing whitespace
            chunks.append(
                Chunk(
                    chunk_id=_deterministic_chunk_id(source_filename, page.page_number, index),
                    text=piece,
                    source_filename=source_filename,
                    page_number=page.page_number,
                    chunk_index=index,
                )
            )
            index += 1
        start += step

    return chunks


def chunk_document(pages: list[PageContent], source_filename: str) -> list[Chunk]:
    """Chunk every page of a document and return one flat list of chunks."""
    all_chunks: list[Chunk] = []
    for page in pages:
        all_chunks.extend(chunk_page(page, source_filename))
    return all_chunks
