# `backend/indexing/store.py` — Vector store management

Design notes extracted from the module's docstrings. The source keeps its summary
lines and every `Args`/`Returns`/`Raises` contract; the conceptual material lives
here.

## What the module does

Handles vector insertion, retrieval, and persistence.

This module provides a clean interface to Chroma:

1. Initializes a persistent vector database on disk
2. Stores embeddings + metadata together
3. Enables semantic search over stored vectors
4. Persists data between sessions

## Why Chroma?

- Zero-setup: no separate database server needed
- Stores vectors AND metadata together (unlike pure vector DBs)
- Persistent storage (vectors survive program restarts)
- Built-in similarity search (find similar vectors)
- Easy to migrate later (Phase 2 can move to PostgreSQL)

> Note on that last point: the migration is easier than it was, but not free.
> `search()` now returns `SearchHit` rather than Chroma's raw response, so callers
> no longer depend on Chroma's nested-list layout or its distance metric. What a
> replacement still has to reproduce is the `add_chunks` id scheme and the
> metadata filter used by `delete_by_source`.

## Configuration

Values come from `backend.config`:

- `chroma_collection_name`: `"books"` (collection to use)
- `chroma_dir`: `data/chroma_db/` (where vectors are stored)
- `embedding_dimension`: 384 (vector size)

Both the persist directory and the collection name can also be passed to
`ChromaStore(...)` directly, which is what lets tests point at a temp directory.

## Data flow

1. Index phase creates Chroma store
2. Adds chunks + embeddings + metadata
3. Retrieval phase searches for similar chunks
4. Generation phase uses retrieved chunks for grounded answers

## Example usage

```python
store = ChromaStore()
store.add_chunks([chunk1, chunk2, chunk3], embeddings)
similar = store.search(query_embedding, k=5)
```

## `add_chunks`

Process:

1. Prepare chunk IDs (unique identifiers)
2. Extract text from chunks
3. Extract metadata from chunks
4. Add to Chroma collection
5. Persist to disk

Chroma uses IDs to track vectors:

- IDs must be unique within collection
- Easier to update/delete specific chunks later
- We use filename + chunk index as ID

> Caveat on that id scheme: `chunk_index` restarts at 0 for every parsed segment,
> so a multi-page PDF produces several chunks whose id ends `_0` and they collide.
> See the chunk-ID collision fix in the refactor plan.

## `search`

Process:

1. Accept query embedding (vector representation of user question)
2. Use Chroma to find k nearest neighbors
3. Return chunks with similarity scores and metadata

Why embeddings for search?

- Semantic: finds meaning, not just keyword matches
- Fast: vector similarity is fast compared to text matching
- Flexible: works across different phrasings of same concept

The collection is configured for cosine distance, where 0 means identical, so the
similarity a caller sees is `1 - distance`. That conversion happens in this class
because this class is what chose the metric.
