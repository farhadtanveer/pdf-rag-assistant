"""
Vector store - wraps Chroma so the rest of the app never imports chromadb
directly. If you outgrow Chroma later (see README "When to scale"), this
is the ONLY file you'd need to rewrite to switch to Qdrant/Milvus/etc.,
because everything else talks to this interface, not to Chroma itself.
"""

import chromadb

from app.config import settings
from app.models.schemas import Chunk


class VectorStore:
    def __init__(self):
        # PersistentClient writes to disk, so your index survives restarts.
        # anonymized_telemetry=False just silences Chroma's noisy telemetry
        # log lines - has no effect on functionality.
        self._client = chromadb.PersistentClient(
            path=str(settings.chroma_persist_dir),
            settings=chromadb.Settings(anonymized_telemetry=False),
        )
        self._collection = self._client.get_or_create_collection(
            name=settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"},  # cosine similarity fits text embeddings
        )

    def add_chunks(self, chunks: list[Chunk], embeddings: list[list[float]]) -> None:
        """Store chunks and their pre-computed embeddings.

        Uses upsert (not add): chunk IDs are deterministic based on
        filename/page/position (see chunker.py), so re-uploading the same
        PDF overwrites its old chunks instead of duplicating them.

        Chroma requires string-keyed metadata, so we flatten each chunk's
        fields (page number, filename, etc.) into a plain dict.
        """
        if not chunks:
            return

        self._collection.upsert(
            ids=[c.chunk_id for c in chunks],
            embeddings=embeddings,
            documents=[c.text for c in chunks],
            metadatas=[
                {
                    "source_filename": c.source_filename,
                    "page_number": c.page_number,
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ],
        )

    def query(self, query_embedding: list[float], top_k: int) -> list[dict]:
        """Find the top_k most similar chunks to a query embedding.

        Returns:
            List of dicts with keys: text, source_filename, page_number, distance.
            Lower distance = more similar (cosine distance).
        """
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )

        if not results["ids"] or not results["ids"][0]:
            return []

        hits = []
        for i in range(len(results["ids"][0])):
            metadata = results["metadatas"][0][i]
            hits.append(
                {
                    "text": results["documents"][0][i],
                    "source_filename": metadata["source_filename"],
                    "page_number": metadata["page_number"],
                    "distance": results["distances"][0][i],
                }
            )
        return hits

    def document_count(self) -> int:
        return self._collection.count()

    def list_source_filenames(self) -> dict[str, int]:
        """Return {filename: chunk_count} for everything currently stored.

        Useful for spotting exactly the kind of duplicate-ingestion issue
        this was added to debug - if a filename's count looks doubled,
        it was uploaded more than once.
        """
        all_items = self._collection.get(include=["metadatas"])
        counts: dict[str, int] = {}
        for metadata in all_items["metadatas"]:
            filename = metadata["source_filename"]
            counts[filename] = counts.get(filename, 0) + 1
        return counts

    def delete_document(self, source_filename: str) -> int:
        """Delete every chunk belonging to one source file. Returns how many were removed."""
        matches = self._collection.get(
            where={"source_filename": source_filename}, include=[]
        )
        ids = matches["ids"]
        if ids:
            self._collection.delete(ids=ids)
        return len(ids)


# Single shared instance - Chroma's PersistentClient is safe to reuse
# across requests within one process.
vector_store = VectorStore()
