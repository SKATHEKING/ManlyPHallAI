# Package overviews

Design notes extracted from the `__init__.py` docstrings. Each package's `__init__`
now carries a one-line summary and re-exports; the pipeline narrative lives here,
in one place, instead of being restated in seven files.

The pipeline runs left to right:

```
ingestion → indexing → retrieval → generation → api / bot
```

---

## `backend.ingestion`

Parsing and extracting text from book files. Handles PDF, EPUB, and plain text.

Orchestrates the entire ingestion pipeline:

1. Parse documents (PDF/EPUB/TXT) → extract text and structure
2. Clean text → remove control chars, HTML, normalize whitespace
3. Chunk text → split into semantic pieces with overlap

Main entry point: `ingest_document(file_path) -> list[Chunk]`

```python
from backend.ingestion import ingest_document

chunks = ingest_document("data/books/my_book.pdf")
for chunk in chunks:
    print(f"Text: {chunk.text[:100]}...")
    print(f"Page: {chunk.metadata['page']}")
    print(f"Chunk {chunk.metadata['chunk_index']} of {chunk.metadata['total_chunks']}")
```

The ingestion pipeline is the foundation for the entire system:

- Output chunks are passed to the indexing layer (for embeddings + vector DB)
- Metadata is preserved so we can cite sources accurately
- Cleaning ensures text quality for downstream ML models

---

## `backend.indexing`

Embedding and storing vectors. Handles text embedding generation and vector
persistence.

Orchestrates Phase 1c:

1. Takes chunks from ingestion (Phase 1b)
2. Generates embeddings using sentence-transformers
3. Stores chunks + embeddings in the Chroma vector DB

Main entry point: `index_chunks(chunks) -> ChromaStore`

The indexing pipeline is the bridge between ingestion and retrieval:

- **Input**: chunks from `ingest_document()` (text + metadata)
- **Process**: generate embeddings for each chunk
- **Output**: searchable vector database for Phase 1d

```python
from backend.ingestion import ingest_document
from backend.indexing import index_chunks

chunks = ingest_document("my_book.pdf")   # Phase 1b: ingest
store = index_chunks(chunks)              # Phase 1c: index
results = store.search(query_embedding, k=5)  # Phase 1d: search
```

---

## `backend.retrieval`

Searching and ranking relevant passages. Handles vector similarity search and
passage ranking.

Main function: `retrieve_chunks(query, store, k=5) -> list[dict]`

Phase 1d, the retrieval half:

- Convert query to embedding
- Search vector database for similar chunks
- Filter by relevance threshold
- Return ranked results with metadata

```python
from backend.retrieval import retrieve_chunks
from backend.indexing import ChromaStore

store = ChromaStore()
results = retrieve_chunks("What is enlightenment?", store, k=5)

for result in results:
    print(result["text"])
    print(f"Source: {result['source']}, Score: {result['score']:.2%}")
```

---

## `backend.generation`

LLM-based answer generation. Handles prompt construction and LLM integration.

Main entry point: `answer_question(question, store) -> Answer`

Phase 1d, the generation half:

- Retrieve relevant chunks for a question
- Build prompt with context
- Call Ollama LLM for generation
- Format answer with citations

```python
from backend.generation import answer_question
from backend.indexing import ChromaStore

store = ChromaStore()
answer = answer_question("What is enlightenment?", store)
```

---

## `backend.api`

REST endpoints. Handles request/response models and route definitions.

Main exports:

- `router`: FastAPI router with all endpoints
- `initialize_store`: initialize the ChromaStore
- Request/response models for validation

Endpoints:

- `POST /api/ask` — Answer a question
- `POST /api/ingest` — Add a book to the index
- `GET /api/status` — System status
- `GET /api/books` — List indexed books
- `DELETE /api/books/{filename}` — Remove a book

---

## `bot`

Discord bot for Manly P. Hall AI.

Main exports:

- `bot`: the Discord bot instance
- `main`: entry point function

```python
from bot import main
main()
```

> Importing this package currently constructs a real Discord client as a side
> effect, because the bot instance is built at module level so the command
> decorators have something to attach to.
