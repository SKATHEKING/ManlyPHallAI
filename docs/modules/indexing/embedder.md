# `backend/indexing/embedder.py` — Embedding generation

Design notes extracted from the module's docstrings. Converts text chunks to dense
vector representations using sentence-transformers.

## What the module does

1. Loads the sentence-transformers model (configured in `backend.config`)
2. Generates embeddings for individual texts or batches
3. Returns numpy arrays compatible with the Chroma vector database

## Why sentence-transformers?

- Fast CPU inference (~50ms per query on modern hardware)
- 384-dimensional output (efficient for storage)
- Pre-trained on semantic similarity tasks
- Works out-of-the-box without fine-tuning

## Configuration

From `backend.config`:

- `embedding_model`: `"all-MiniLM-L6-v2"` (22MB model)
- `embedding_dimension`: 384 (output vector size)
- `embedding_batch_size`: 32 (chunk size for batch processing)

## Why this matters

The embeddings are the foundation for semantic retrieval:

- Similar text chunks have similar embeddings
- Enables vector similarity search in Phase 1d
- Allows us to find relevant passages for user questions

## Model lifecycle

The model is loaded lazily on first use and cached in a module-level global, so
the model name is effectively fixed once the first embedding is generated.
