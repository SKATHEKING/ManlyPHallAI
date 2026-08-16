# `backend/api/routes.py` — REST endpoints

Design notes extracted from the module's docstrings. HTTP API for the RAG system
(Phase 1e).

## Endpoints

- `POST /ask` — Answer a question using indexed books
- `POST /ingest` — Add a new book to the index
- `GET /status` — System health and statistics
- `GET /books` — List indexed books
- `DELETE /books/{filename}` — Remove a book from the index

All endpoints use the ingestion → indexing → retrieval → generation pipeline.

## Who consumes this layer

- Web applications
- Discord bot backend
- External integrations
- Direct HTTP clients

> In practice the Discord bot does *not* go through HTTP — it imports the backend
> directly and keeps its own store, so the ask path currently exists twice.

## Example usage

```
POST /ask
{"question": "What is enlightenment?"}

Response:
{
    "answer": "Enlightenment is...",
    "citations": ["book.pdf, page 42", ...],
    "confidence": 0.75,
    "num_sources": 3
}
```

## Validation and status codes

Request validation lives in the pydantic models, not in the handlers: `question`
is capped at 1000 characters and `k` is constrained to 1..20, so out-of-range
input produces a 422 before any handler runs.

`DELETE /books/{filename}` returns 404 when nothing was indexed under that name
and no file exists on disk. The filename is resolved against the books directory
and rejected with 400 if it escapes it.
