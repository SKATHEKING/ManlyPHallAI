# Demo scripts

Design notes extracted from the `scripts/` module docstrings.

These are **demonstration and smoke scripts, not tests**, despite three of them
being named `test_*.py`. They contain no assertions — they run a pipeline stage
and print formatted output for a human to inspect. Because several of their
functions are also named `test_*`, a bare `pytest` from the repo root used to
collect them and run the whole pipeline, including Ollama calls; `pyproject.toml`
now restricts collection to `tests/`.

The real assertions live in `tests/`.

---

## `scripts/test_ingestion.py` — Phase 1b

Validates the ingestion pipeline:

- Parsing (extract text from documents)
- Cleaning (normalize and format text)
- Chunking (split into semantic pieces with overlap)

Creates a sample book, ingests it, and prints ingestion statistics (chunk count,
sizes, metadata) plus sample chunks for quality inspection.

```bash
PYTHONPATH=. python scripts/test_ingestion.py
```

Expected output:

```
✓ Created sample book: data/books/sample_book.txt
📖 Ingesting document...
✓ Ingestion took 0.XX seconds

📊 Ingestion Statistics:
  • Total chunks: N
  • Total text length: X,XXX characters
  • Average chunk length: XXX characters
  • Min/Max chunk lengths

🏷️  Metadata (from first chunk):
  • source, format, filename, chunk_index, etc.

📑 Sample Chunks (first 3):
  --- Chunk 1 ---
  Metadata: {...}
  Text (XXX chars):
  [First 300 characters of chunk]...
```

---

## `scripts/test_indexing.py` — Phase 1c

Validates the complete indexing workflow:

1. Ingest a sample book (Phase 1b)
2. Generate embeddings for all chunks (Phase 1c)
3. Store in Chroma vector database (Phase 1c)
4. Verify retrieval capability (Phase 1d preview)

The first end-to-end run combining Phase 1b + 1c:

- **Input**: book file
- **Process**: ingest → chunk → embed → index
- **Output**: searchable vector database

```bash
PYTHONPATH=. python scripts/test_indexing.py
```

Expected output:

```
🚀 Testing Indexing Pipeline (Phase 1c)

[Phase 1b: Ingestion]
✓ Created sample book
✓ Ingested and chunked

[Phase 1c: Indexing]
📝 Generating embeddings
✓ Indexed N chunks

[Verification: Retrieval]
🔍 Testing similarity search
✓ Retrieved K similar chunks

📊 Results:
• Store size: N chunks
• Sample query: "enlightenment"
• Top 3 results with scores...
```

---

## `scripts/test_retrieval_generation.py` — Phase 1d

Exercises the full RAG loop: ingest, index, retrieve, build a prompt and generate
an answer. Requires a running Ollama:

```bash
ollama serve
ollama pull llama2:7b
PYTHONPATH=. python scripts/test_retrieval_generation.py
```

---

## `scripts/ingest_book.py`

The real ingestion entry point for adding a book to the index:

```bash
PYTHONPATH=. python scripts/ingest_book.py data/books/my_book.pdf
```

---

## Known duplication

All three `test_*` scripts define their own `create_sample_book()` — roughly 216
lines generating near-identical fake esoteric text, 63–82% similar pairwise. A
fourth copy of the same fixture idea lives in `tests/conftest.py`. Consolidating
them is a pending item in the refactor plan.
