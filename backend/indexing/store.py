"""
Vector store management using Chroma.
Handles vector insertion, retrieval, and persistence.

This module provides a clean interface to Chroma:
1. Initializes a persistent vector database on disk
2. Stores embeddings + metadata together
3. Enables semantic search over stored vectors
4. Persists data between sessions

Why Chroma?
- Zero-setup: no separate database server needed
- Stores vectors AND metadata together (unlike pure vector DBs)
- Persistent storage (vectors survive program restarts)
- Built-in similarity search (find similar vectors)
- Easy to migrate later (Phase 2 can move to PostgreSQL)

Configuration (from backend.config):
- CHROMA_COLLECTION_NAME: "books" (collection to use)
- CHROMA_PERSIST_DIR: "data/chroma_db/" (where vectors are stored)
- EMBEDDING_DIMENSION: 384 (vector size)

Data flow:
1. Index phase creates Chroma store
2. Adds chunks + embeddings + metadata
3. Retrieval phase searches for similar chunks
4. Generation phase uses retrieved chunks for grounded answers

Example usage:
    store = ChromaStore()
    store.add_chunks([chunk1, chunk2, chunk3], embeddings)
    similar = store.search("What is enlightenment?", k=5)
"""

from __future__ import annotations

import logging
from pathlib import Path

import chromadb

from typing import Any, Sequence, cast

from backend.config import get_settings
from backend.core.types import ChunkMetadata, SearchHit, TextSegment


logger = logging.getLogger(__name__)


class ChromaStore:
    """
    Wrapper around Chroma vector database.
    
    Handles initialization, insertion, and retrieval of vectors.
    All operations go through this class to keep database details
    encapsulated (easier to swap for PostgreSQL later if needed).
    
    Attributes:
        client: Chroma client instance
        collection: Active collection for book vectors
    """
    
    def __init__(
        self,
        persist_dir: Path | str | None = None,
        collection_name: str | None = None,
    ):
        """
        Initialize Chroma store with persistent storage.

        Creates:
        - Persistent Chroma client (stores vectors to disk)
        - Collection named after CHROMA_COLLECTION_NAME
        - Metadata indexing for fast filtering

        Args:
            persist_dir: Where to keep the index. Defaults to the configured
                         location. Taking it as an argument is what allows a test
                         to point at a temporary directory instead of the real
                         index, which previously was impossible.
            collection_name: Collection to open. Defaults to the configured name.
        """
        settings = get_settings()

        # Ensure data directory exists
        persist_dir = Path(settings.chroma_dir if persist_dir is None else persist_dir)
        persist_dir.mkdir(parents=True, exist_ok=True)

        self.collection_name = (
            settings.chroma_collection_name if collection_name is None else collection_name
        )

        # Initialize Chroma client with persistent storage
        # Uses new Chroma API (v0.4+) with PersistentClient
        # Automatically manages database and vector storage
        self.client = chromadb.PersistentClient(path=str(persist_dir))

        # Get or create the collection for storing book chunks
        # If collection exists, get it; if not, create it
        # Metadata field is for filtering (e.g., by source file)
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity for search
        )

        logger.info(f"✓ Chroma store initialized: {self.collection_name}")
    
    def add_chunks(self, chunks: Sequence[TextSegment], embeddings_matrix) -> int:
        """
        Add chunks and their embeddings to the store.
        
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
        
        Args:
            chunks: List of Chunk objects (from ingestion phase)
            embeddings_matrix: numpy array of embeddings (shape: num_chunks x 384)
            
        Returns:
            Number of chunks added
        """
        if len(chunks) == 0:
            logger.warning("No chunks to add")
            return 0
        
        # Prepare data for Chroma
        ids = []
        texts = []
        metadatas = []
        
        for i, chunk in enumerate(chunks):
            # Create unique ID: filename_chunk_index
            # This allows us to identify and cite specific chunks later
            chunk_id = f"{chunk.metadata['filename']}_{chunk.metadata['chunk_index']}"
            ids.append(chunk_id)
            
            # Extract text
            texts.append(chunk.text)
            
            # Extract metadata (Chroma can store and filter on metadata)
            # We keep source, page/chapter, etc. for later citation
            metadatas.append(chunk.metadata)
        
        # Add to Chroma
        # Parameters:
        # - ids: unique identifiers
        # - embeddings: the vectors (pre-computed)
        # - metadatas: associated metadata
        # - documents: the text (for display/debugging)
        self.collection.add(
            ids=ids,
            embeddings=embeddings_matrix.tolist(),  # Convert numpy array to list
            # cast only to satisfy Chroma's very broad metadata stub; a TypedDict
            # is an ordinary dict at runtime, so nothing is converted here.
            metadatas=cast(Any, metadatas),
            documents=texts,
        )
        
        # Note: Chroma v0.4+ persists automatically, no explicit persist() call needed
        
        logger.info(f"✓ Added {len(chunks)} chunks to store")
        return len(chunks)
    
    def search(self, query_embedding, k: int = 5) -> list[SearchHit]:
        """
        Search for similar chunks using vector similarity.
        
        Process:
        1. Accept query embedding (vector representation of user question)
        2. Use Chroma to find k nearest neighbors
        3. Return chunks with similarity scores and metadata
        
        Why embeddings for search?
        - Semantic: finds meaning, not just keyword matches
        - Fast: vector similarity is fast compared to text matching
        - Flexible: works across different phrasings of same concept
        
        Args:
            query_embedding: Embedding vector of user question (shape: 384,)
            k: Number of results to return (default 5)
            
        Returns:
            List of SearchHit, ordered most similar first, each carrying an id,
            the chunk text, its metadata and a similarity score in 0..1.

            This used to return Chroma's raw response: a dict of parallel lists,
            each nested one level deeper because Chroma can answer several queries
            per call. Callers unpacked that themselves and converted the distance
            into a similarity, which spread knowledge of Chroma's response format
            and its distance metric into the retrieval layer. Both now stop here.
        """
        # Query the collection
        # query_embeddings is a list of embeddings (we send 1)
        # n_results is how many to return
        # include specifies what to return
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],  # Convert numpy to list
            n_results=k,
            # Embeddings are deliberately not requested: no caller reads them, and
            # pulling every 384-float vector back for each query is pure overhead.
            include=["metadatas", "documents", "distances"],
        )

        # Chroma answers per query, so every field is a list-of-lists and we want
        # index 0. Missing keys yield empty lists rather than raising.
        ids = (results.get("ids") or [[]])[0]
        distances = (results.get("distances") or [[]])[0]
        metadatas = (results.get("metadatas") or [[]])[0]
        documents = (results.get("documents") or [[]])[0]

        hits = [
            SearchHit(
                id=chunk_id,
                text=text,
                # Chroma types its metadata as a broad Mapping of primitives; this
                # is the same dict we wrote at ingestion time.
                metadata=cast(ChunkMetadata, metadata or {}),
                # The collection is configured for cosine distance above, where 0
                # means identical, so similarity is its complement. This belongs
                # here because this class chose the metric.
                score=1 - distance,
            )
            for chunk_id, distance, metadata, text in zip(
                ids, distances, metadatas, documents
            )
        ]

        logger.debug(f"Found {len(hits)} similar chunks")

        return hits
    
    def get_collection_size(self) -> int:
        """
        Get number of chunks in the collection.
        
        Returns:
            Integer count of chunks
        """
        return self.collection.count()
    
    def clear_collection(self) -> None:
        """
        Delete all chunks from collection.
        
        Use with caution! This removes all stored vectors.
        Useful for testing or rebuilding the index.
        """
        # Get all IDs and delete them
        all_data = self.collection.get()
        if all_data["ids"]:
            self.collection.delete(ids=all_data["ids"])
            # Note: Chroma v0.4+ persists automatically, no explicit persist() call needed
            logger.warning(f"✗ Cleared collection: {len(all_data['ids'])} chunks deleted")
    
    def delete_by_source(self, source_filename: str) -> int:
        """
        Delete all chunks from a specific source file.
        
        Useful for re-ingesting a single book without deleting others.
        
        Args:
            source_filename: Filename to match (from chunk metadata['filename'])
            
        Returns:
            Number of chunks deleted
        """
        # Get all chunks from this source, using Chroma's metadata filter DSL
        all_data = self.collection.get(
            where=cast(Any, {"filename": {"$eq": source_filename}})
        )
        
        if all_data["ids"]:
            self.collection.delete(ids=all_data["ids"])
            # Note: Chroma v0.4+ persists automatically, no explicit persist() call needed
            count = len(all_data["ids"])
            logger.info(f"Deleted {count} chunks from {source_filename}")
            return count
        
        return 0
