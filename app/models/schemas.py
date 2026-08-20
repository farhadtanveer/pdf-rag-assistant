"""
Data models shared across the application.

Keeping these separate from the logic that uses them means the API layer,
service layer, and core layer all agree on exactly what a "chunk" or an
"answer" looks like, and FastAPI auto-generates API docs from them for free.
"""

from pydantic import BaseModel, Field


class PageContent(BaseModel):
    """Raw text extracted from a single PDF page."""

    page_number: int  # 1-indexed, matches what a human sees in a PDF viewer
    text: str


class Chunk(BaseModel):
    """A piece of a document, small enough to embed, with enough metadata
    to trace it back to an exact page for citation purposes."""

    chunk_id: str
    text: str
    source_filename: str
    page_number: int
    chunk_index: int  # position of this chunk within the page (0, 1, 2...)


class UploadResponse(BaseModel):
    filename: str
    total_pages: int
    total_chunks: int
    message: str = "Document ingested successfully."


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, description="The user's question in German or English.")
    top_k: int | None = Field(
        default=None,
        description="Override how many chunks to retrieve. Defaults to config value.",
    )


class SourceReference(BaseModel):
    """A single retrieved chunk shown to the user as proof/citation."""

    source_filename: str
    page_number: int
    excerpt: str  # short preview of the chunk text, so the user can sanity-check


class AskResponse(BaseModel):
    answer: str
    sources: list[SourceReference]
