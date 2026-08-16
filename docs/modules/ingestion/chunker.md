# `backend/ingestion/chunker.py` — Semantic chunking with overlap

Design notes extracted from the module's docstrings. Uses LangChain's
`RecursiveCharacterTextSplitter`.

## Why chunking?

Large documents need to be broken into smaller pieces for:

1. Embedding (models have max input length)
2. Retrieval (find relevant passages, not whole books)
3. Context windows (LLM prompt size is limited)

## Why "recursive" splitting?

It respects document structure by trying separators in order:

1. First split on paragraph breaks (`\n\n`) — preserve paragraphs
2. If too large, split on newlines (`\n`) — preserve lines
3. If still too large, split on sentences (`. `)
4. If still too large, split on spaces — last resort

This keeps semantic units together.

## Why overlap?

Chunks at boundaries might lose context. 50% overlap means concepts appearing at
the end of chunk N also appear at the start of chunk N+1.

Example: `"Concept X is important. Concept X helps with Y."`
If `"Concept X is important."` is at a chunk boundary:

- Chunk 1 ends: `"Concept X is important."`
- Chunk 2 starts: `"Concept X helps with Y."`

Both chunks have "Concept X", so a query for "Concept" finds both.

## Configuration

From `backend.config`:

- `chunk_size`: 256 tokens (roughly 1000 characters)
- `chunk_overlap`: 50% (overlap amount calculated from size)
- `tokenizer_model`: `bert-base-uncased`, used only to count tokens

## Token counting

`count_tokens` uses a real tokenizer, falling back to `len(text) // 4` if it
cannot be loaded. That fallback silently changes every chunk boundary, so a
characterization test pins `count_tokens("hello world") == 4` as a canary — the
approximation would return 2.

## Known issue: chunk index restarts per call

`create_chunks` numbers chunks from 0 on every call, and `ingest_document` calls
it once per parsed segment (per page for PDFs, per chapter for EPUBs). Combined
with the store's `f"{filename}_{chunk_index}"` id scheme, every page yields an id
ending `_0`, so segments collide and most of a multi-page book is never indexed.
