"""
Retrieval module for searching and ranking relevant passages.
Handles vector similarity search and passage ranking.

Main function: retrieve_chunks(query, store, k=5) -> List[dict]

This module handles the retrieval phase (Phase 1d):
- Convert query to embedding
- Search vector database for similar chunks
- Filter by relevance threshold
- Return ranked results with metadata

Example usage:
    from backend.retrieval import retrieve_chunks
    from backend.indexing import ChromaStore
    
    store = ChromaStore()
    results = retrieve_chunks("What is enlightenment?", store, k=5)
    
    for result in results:
        print(result["text"])
        print(f"Source: {result['source']}, Score: {result['score']:.2%}")
"""

from backend.retrieval.retriever import retrieve_chunks, retrieve_with_filters


__all__ = ["retrieve_chunks", "retrieve_with_filters"]
