# `backend/retrieval/retriever.py` — Query-based retrieval

Design notes extracted from the module's docstrings. Handles Phase 1d, the
retrieval step.

## What the module does

1. Convert user query to embedding
2. Search vector database for similar chunks
3. Filter by relevance threshold
4. Return ranked results with metadata for citation

Main function: `retrieve_chunks(query, store, k=5) -> list[dict]`

The retriever bridges user queries and the indexed knowledge base.

- **Input**: natural language query (string)
- **Process**: embed → search → filter → rank
- **Output**: list of relevant passages with sources for answer generation

## Example usage

```python
from backend.retrieval import retrieve_chunks
from backend.indexing import ChromaStore

# Load existing store
store = ChromaStore()

# Retrieve relevant chunks
results = retrieve_chunks("What is enlightenment?", store, k=5)
```

Results contain:

- `text`: chunk content
- `source`: full path of the originating file
- `filename`: basename of that file
- `page`: page number (for PDFs)
- `chapter`: chapter number (for EPUBs)
- `chunk_index`, `score`, `metadata`, `rank`

> `source` is a full path while `filename` is a basename, and consumers disagree
> about which to display — citations render the basename but de-duplicate on the
> path, while the Discord `/search` command prints the path.

## Scores and the threshold

The store returns a similarity already normalised to 0..1, where higher is more
similar. Anything below `relevance_threshold` (default 0.3) is dropped before the
LLM ever sees it, which is the cheapest available defence against irrelevant
context.

`k` and `threshold` default to `None` and are resolved from settings at call time,
rather than being bound as default arguments — a default argument is evaluated
once at import, which previously froze the configuration permanently.
