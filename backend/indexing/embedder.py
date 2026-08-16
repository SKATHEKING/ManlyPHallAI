"""
Embedding generation using sentence-transformers.
Converts text chunks to dense vector representations.

Why sentence-transformers, the configuration and the model lifecycle:
docs/modules/indexing/embedder.md
"""

from __future__ import annotations

import logging
from typing import Iterable

import numpy as np
from sentence_transformers import SentenceTransformer

from backend.config import EMBEDDING_BATCH_SIZE, EMBEDDING_MODEL


logger = logging.getLogger(__name__)

# Global model instance (loaded once, reused)
# This is important for performance - loading the model is expensive
_model: SentenceTransformer | None = None


def _load_model() -> SentenceTransformer:
    """
    Load the embedding model (with caching).
    
    Why cache?
    - Loading the model is slow (network download + initialization)
    - We'll call this many times during indexing
    - Caching avoids reloading
    
    Returns:
        Loaded SentenceTransformer model instance
    """
    global _model
    
    if _model is None:
        logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
        _model = SentenceTransformer(EMBEDDING_MODEL)
        logger.info(f"✓ Model loaded: {EMBEDDING_MODEL}")
    
    return _model


def embed_texts(texts: str | Iterable[str], batch_size: int | None = None) -> np.ndarray:
    """
    Generate embeddings for one or more texts.
    
    Process:
    1. Accept either a single text string or list of texts
    2. Convert single text to list for uniform processing
    3. Load model if not already loaded
    4. Generate embeddings in batches (batch_size controls memory usage)
    5. Return as numpy array
    
    Why batching?
    - Processing 1000 chunks one-at-a-time is slow
    - Processing all at once could cause out-of-memory
    - Batch size balances speed (larger batches) with memory (smaller batches)
    - Default: EMBEDDING_BATCH_SIZE from config
    
    Args:
        texts: Single text string or list of text strings to embed
        batch_size: Batch size for processing (default: EMBEDDING_BATCH_SIZE)
        
    Returns:
        numpy array of shape (num_texts, 384) with embeddings
    """
    # Use default batch size if not specified
    if batch_size is None:
        batch_size = EMBEDDING_BATCH_SIZE
    
    # Convert single string to list
    if isinstance(texts, str):
        texts = [texts]
    else:
        texts = list(texts)
    
    # Load model (will use cached instance if already loaded)
    model = _load_model()
    
    # Generate embeddings using the model
    # The encode() method handles batching internally for efficiency
    embeddings = model.encode(texts, batch_size=batch_size, show_progress_bar=False)
    
    # Ensure output is numpy array
    if not isinstance(embeddings, np.ndarray):
        embeddings = np.array(embeddings)
    
    logger.debug(f"Generated embeddings for {len(texts)} texts (shape: {embeddings.shape})")
    
    return embeddings


def get_embedding_dimension() -> int:
    """
    Get the dimension of embeddings from this model.
    
    Returns:
        Integer dimension (typically 384 for all-MiniLM-L6-v2)
    """
    model = _load_model()
    return model.get_sentence_embedding_dimension()
