"""
Query-based retrieval of relevant book passages.

This module handles Phase 1d (retrieval step):
1. Convert user query to embedding
2. Search vector database for similar chunks
3. Filter by relevance threshold
4. Return ranked results with metadata for citation

Main function: retrieve_chunks(query, store, k=5) -> List[dict]

The retriever bridges user queries and the indexed knowledge base.
Input: Natural language query (string)
Process: Embed → Search → Filter → Rank
Output: List of relevant passages with sources for answer generation

Example usage:
    from backend.retrieval import retrieve_chunks
    from backend.indexing import ChromaStore
    
    # Load existing store
    store = ChromaStore()
    
    # Retrieve relevant chunks
    results = retrieve_chunks("What is enlightenment?", store, k=5)
    
    # Results contain:
    # - text: chunk content
    # - source: filename
    # - page: page number (for PDFs)
    # - chapter: chapter name (for EPUBs)
    # - score: similarity score
"""

from __future__ import annotations

import logging
from typing import Any

from backend.indexing.embedder import embed_texts
from backend.config import get_settings


logger = logging.getLogger(__name__)


# k and threshold default to None rather than to config values directly. A default
# argument is evaluated once, when the function is defined, so binding config at
# that point froze the value at import time and made overriding it impossible.
# Resolving None against the settings at call time is what makes them tunable.
def retrieve_chunks(
    query: str,
    store: Any,
    k: int | None = None,
    threshold: float | None = None,
) -> list[dict]:
    """
    Retrieve relevant chunks for a user query.
    
    This is the core retrieval pipeline:
    1. Embed the user query using the same model as chunks
    2. Search the vector store for most similar chunks
    3. Filter by relevance threshold (0.5 by default)
    4. Return formatted results for generation phase
    
    The query embedding is compared against all stored chunk embeddings
    using cosine similarity. Higher similarity means more relevant.
    
    Args:
        query: User question or search query (string)
        store: ChromaStore instance from Phase 1c
        k: Number of results to retrieve (default 5)
        threshold: Minimum similarity score (0-1, default 0.5)
                   Results below this are filtered out
        
    Returns:
        List of dicts with keys:
        - text: Chunk text content
        - source: Original filename (for citation)
        - filename: Same as source
        - page: Page number (for PDFs, if available)
        - chapter: Chapter name (for EPUBs, if available)
        - chunk_index: Index within source document
        - score: Cosine similarity (0-1, 1 = identical)
        - metadata: Full metadata dict
        
    Note:
        If no results meet threshold, empty list is returned.
        This prevents low-confidence retrieval from feeding bad info to LLM.
    """
    if not query or not query.strip():
        logger.warning("Empty query provided to retrieve_chunks")
        return []

    settings = get_settings()
    k = settings.retrieval_k if k is None else k
    threshold = settings.relevance_threshold if threshold is None else threshold

    # Step 1: Convert query to embedding
    # Use same embedding model as chunks for consistency
    query_embedding = embed_texts(query)[0]  # Returns 384-dim vector
    
    # Step 2: Search the vector store
    # Chroma returns: ids, distances, metadatas, documents
    # Distance is L2 (Euclidean), so lower = more similar
    # We convert to similarity: 1 - distance (higher = more similar)
    search_results = store.search(query_embedding, k=k)
    
    # Step 3: Process and filter results
    formatted_results = []
    
    if not search_results or not search_results.get("ids"):
        logger.info(f"No results found for query: {query}")
        return []
    
    # Results are organized by query (first dimension)
    # Since we have one query, we get [results_for_query_0]
    ids = search_results["ids"][0] if search_results["ids"] else []
    distances = search_results["distances"][0] if search_results["distances"] else []
    metadatas = search_results["metadatas"][0] if search_results["metadatas"] else []
    documents = search_results["documents"][0] if search_results["documents"] else []
    
    for i, (chunk_id, distance, metadata, text) in enumerate(
        zip(ids, distances, metadatas, documents)
    ):
        # Convert distance to similarity score (0-1)
        # Cosine distance ranges from 0 to 2, so formula: (2 - distance) / 2
        similarity = 1 - distance  # For normalized vectors
        
        # Step 3: Apply threshold filter
        if similarity < threshold:
            logger.debug(f"Skipping chunk {chunk_id}: score {similarity:.2%} < threshold {threshold:.2%}")
            continue
        
        # Step 4: Format result for generation phase
        result = {
            "text": text,
            "source": metadata.get("source", "unknown"),
            "filename": metadata.get("filename", "unknown"),
            "page": metadata.get("page", None),
            "chapter": metadata.get("chapter", None),
            "chunk_index": metadata.get("chunk_index", i),
            "score": similarity,
            "metadata": metadata,
            "rank": len(formatted_results) + 1,  # 1-indexed rank
        }
        
        formatted_results.append(result)
        
        logger.debug(f"Retrieved: {metadata.get('filename')} (score: {similarity:.2%})")
    
    logger.info(f"Retrieved {len(formatted_results)} chunks for query: '{query}'")
    
    return formatted_results


def retrieve_with_filters(
    query: str,
    store: Any,
    k: int | None = None,
    threshold: float | None = None,
    source_filter: str | None = None,
) -> list[dict]:
    """
    Advanced retrieval with optional metadata filtering.
    
    This is an extension of retrieve_chunks that allows filtering
    results by source filename (useful for single-book searches).
    
    Args:
        query: User question or search query
        store: ChromaStore instance
        k: Number of results before filtering
        threshold: Minimum similarity score
        source_filter: Optional filename to restrict results to
        
    Returns:
        List of filtered results (same format as retrieve_chunks)
    """
    k = get_settings().retrieval_k if k is None else k

    # Get all results first
    results = retrieve_chunks(query, store, k=k * 2, threshold=threshold)  # Get more to filter
    
    # Filter by source if requested
    if source_filter:
        results = [r for r in results if r["filename"] == source_filter]
        logger.info(f"Filtered to {len(results)} results from {source_filter}")
    
    # Return top k after filtering
    return results[:k]


__all__ = ["retrieve_chunks", "retrieve_with_filters"]
