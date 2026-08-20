# Internal Document RAG Assistant

Ask questions about internal PDFs (supplier datasheets, technical docs) and get
answers with page-level citations, so anyone can verify the source. Fully
self-hosted — no data ever leaves your machine.

## How it works

```
Upload PDF  ->  extract text per page  ->  split into chunks  ->  embed  ->  store in Chroma
Ask question -> embed question -> retrieve similar chunks -> build prompt -> local LLM -> answer + sources
```

Every chunk keeps its exact page number from the moment it's extracted, which
is what makes the citations trustworthy instead of guessed.

## Project structure

```
app/
  config.py              <- all settings in one place
  main.py                <- FastAPI app, wires routes together
  api/routes/
    documents.py          <- POST /documents/upload
    chat.py                <- POST /chat/ask
  core/                   <- single-responsibility building blocks
    pdf_parser.py          <- PDF -> text per page
    chunker.py              <- text -> overlapping chunks
    embeddings.py           <- Ollama embedding client
    llm.py                  <- Ollama chat client
    vector_store.py         <- Chroma wrapper
    prompts.py               <- prompt templates (tune answer quality here)
  services/                <- orchestrates core modules for one use case
    ingestion_service.py
    query_service.py
  models/
    schemas.py             <- Pydantic request/response contracts
tests/                     <- unit tests, run with `pytest`
data/
  uploads/                <- temp storage during ingestion (auto-cleaned)
  chroma_db/               <- persistent vector index (survives restarts)
```

**Why layered like this:** the API layer only knows HTTP. Services only know
"do this business task." Core modules each do exactly one thing (parse, chunk,
embed, store, generate) and don't know about each other. This is what lets you
change one piece — e.g. swap Chroma for Qdrant, or add a reranker — without
touching the rest of the app.

## Prerequisites

1. **Python 3.11+**
2. **[Ollama](https://ollama.com)** installed and running locally
3. Pull the two models used by default:
   ```bash
   ollama pull phi4-mini
   ollama pull bge-m3
   ```

## Setup

```bash
cd pdf-rag-assistant
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env             # defaults already match the models above
```

## Run

```bash
uvicorn app.main:app --reload
```

- API docs (interactive, test everything from the browser): http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Try it

**Upload a PDF:**
```bash
curl -X POST http://localhost:8000/documents/upload \
  -F "file=@/path/to/your/datasheet.pdf"
```

**List what's currently ingested** (chunk count per file — handy for spotting accidental double-uploads):
```bash
curl http://localhost:8000/documents
```

**Delete a document** (removes all its chunks):
```bash
curl -X DELETE "http://localhost:8000/documents/your-file.pdf"
```

Re-uploading the same filename overwrites its old chunks rather than duplicating them — chunk IDs are deterministic (hashed from filename + page + position), not random.

**Ask a question:**
```bash
curl -X POST http://localhost:8000/chat/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the maximum operating temperature?"}'
```

Response includes the answer plus a `sources` list with exact filename + page
number for every chunk that was actually used — this list is built directly
from the retrieval results, so it's accurate even if the model's own inline
citation isn't perfect.

## Run the tests

```bash
pytest tests/ -v
```

Covers chunking logic and PDF page-extraction accuracy — the two things that
matter most for citation correctness. These tests don't need Ollama running.

## Known limitations (v1, on purpose — see "Next steps")

- **Scanned PDFs** (image-only, no text layer) aren't handled — `parse_pdf`
  will raise a clear error rather than silently returning nothing. Add OCR
  (Tesseract) later if you need this.
- **No streaming** — answers come back as one response, not token-by-token.
  Fine for a v1 internal tool; add later if answers feel slow.
- **No auth** — this is meant to sit inside your office network. Add an auth
  layer before exposing it more broadly.
- **Chroma telemetry warnings** in the console (`Failed to send telemetry
  event...`) are a harmless known bug in Chroma's own code, unrelated to
  your data — safe to ignore.
- **Sequential embedding on ingestion** — fine for a handful of PDFs; if you
  batch-upload hundreds at once, see "When to scale" below.

## Moving from laptop to the office server

Change **`.env`** only:
```
OLLAMA_BASE_URL=http://<office-server-ip>:11434
EMBEDDING_MODEL=bge-m3
LLM_MODEL=qwen3:30b-a3b        # or whatever fits the server's GPU
```
No code changes needed — this is the entire point of keeping config
centralized in `app/config.py`.

## Next steps (roughly in the order I'd tackle them)

1. **React frontend** — chat UI + a PDF viewer (`react-pdf`) that jumps to
   the cited page when a source is clicked.
2. **Streaming answers** — switch `llm.py`'s `stream: False` to `True` and
   forward chunks via FastAPI's `StreamingResponse`.
3. **OCR fallback** for scanned PDFs (Tesseract).
4. **Delete/list endpoints** for uploaded documents (currently upload-only).
5. **When to scale past Chroma:** once you're past ~500K–1M chunks (a LOT of
   PDFs), look at Qdrant or Milvus. Until then, don't — it's not the
   bottleneck.
6. **Reranking**: add a second-stage reranker model after retrieval if answer
   quality needs a boost on larger document sets.
