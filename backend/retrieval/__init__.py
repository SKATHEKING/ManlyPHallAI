"""
Retrieval module for searching and ranking relevant passages.

Main function: retrieve_chunks(query, store, k=5) -> list[dict]

Pipeline overview and examples: docs/modules/packages.md
"""

from backend.retrieval.retriever import retrieve_chunks, retrieve_with_filters


__all__ = ["retrieve_chunks", "retrieve_with_filters"]
