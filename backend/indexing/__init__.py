"""
Indexing module for embedding and storing vectors.
Handles text embedding generation and vector persistence.

This module orchestrates Phase 1c:
1. Takes chunks from ingestion (Phase 1b)
2. Generates embeddings using sentence-transformers
3. Stores chunks + embeddings in Chroma vector DB

Main entry point: index_chunks(chunks) -> ChromaStore

The indexing pipeline is the bridge between ingestion and retrieval:
- Input: chunks from ingest_document() (text + metadata)
- Process: generate embeddings for each chunk
- Output: searchable vector database for Phase 1d

Example usage:
    from backend.ingestion import ingest_document
    from backend.indexing import index_chunks
    
    # Phase 1b: Ingest book
    chunks = ingest_document("my_book.pdf")
    
    # Phase 1c: Index for retrieval
    store = index_chunks(chunks)
    
    # Phase 1d: Search
    results = store.search(query_embedding, k=5)
"""

from __future__ import annotations

import logging

from backend.indexing.embedder import embed_texts
from backend.indexing.store import ChromaStore


logger = logging.getLogger(__name__)


def index_chunks(chunks: list, show_progress: bool = True) -> ChromaStore:
    """
    End-to-end indexing pipeline: embed chunks and store in Chroma.
    
    This function:
    1. Validates input chunks
    2. Extracts text from chunks
    3. Generates embeddings in batches
    4. Creates/initializes Chroma store
    5. Adds embeddings + metadata to store
    6. Returns the store for querying
    
    Process flow:
    Chunks → Extract text → Generate embeddings → Create store → Add to store → Return
    
    Args:
        chunks: List of Chunk objects from backend.ingestion.ingest_document()
        show_progress: Whether to show progress information (default True)
        
    Returns:
        ChromaStore instance ready for semantic search
    """
    if not chunks:
        logger.error("No chunks to index")
        return None
    
    if show_progress:
        print(f"\n🔍 Indexing {len(chunks)} chunks...")
    
    # Step 1: Extract text from chunks
    # Prepare text list for embedding
    chunk_texts = [chunk.text for chunk in chunks]
    
    if show_progress:
        print(f"   📝 Generating embeddings for {len(chunk_texts)} texts...")
    
    # Step 2: Generate embeddings
    # This converts each text chunk into a 384-dimensional vector
    # Similar texts will have similar vectors (enabling semantic search)
    embeddings_matrix = embed_texts(chunk_texts)
    
    if show_progress:
        print(f"   ✓ Generated embeddings (shape: {embeddings_matrix.shape})")
    
    # Step 3: Initialize Chroma store
    # This creates the vector database on disk if it doesn't exist
    store = ChromaStore()
    
    # Step 4: Add chunks and embeddings to store
    # Metadata (source, page, chunk index, etc.) is stored for citation
    added_count = store.add_chunks(chunks, embeddings_matrix)
    
    if show_progress:
        print(f"   ✓ Added {added_count} chunks to vector store")
        print(f"✓ Indexing complete!")
    
    return store


__all__ = ["index_chunks", "ChromaStore"]
