"""
Text chunking utilities for semantic splitting with overlap.
Uses LangChain's RecursiveCharacterTextSplitter.

Why chunking, why recursive splitting, why overlap, and the configuration:
docs/modules/ingestion/chunker.md
"""

from __future__ import annotations

import logging
from backend.core.types import TextSegment

from langchain_text_splitters import RecursiveCharacterTextSplitter
from tokenizers import Tokenizer as TokenizerLib

from backend.config import CHUNK_OVERLAP, CHUNK_SIZE


logger = logging.getLogger(__name__)


# One shared type replaces the three identical NamedTuples that used to exist.
# The name is kept as an alias so `from backend.ingestion.chunker import TextChunk`
# still works; the original docstring now lives on TextSegment.
TextChunk = TextSegment


# Initialize tokenizer for accurate token counting
# Using the same tokenizer as sentence-transformers for consistency
try:
    _tokenizer = TokenizerLib.from_pretrained("bert-base-uncased")
except Exception:
    logger.warning("Could not load BERT tokenizer; using approximate token counting")
    _tokenizer = None


def count_tokens(text: str) -> int:
    """
    Count tokens in text using BERT tokenizer.
    Falls back to approximate word count if tokenizer unavailable.
    
    Why accurate token counting?
    - We want chunks to be approximately CHUNK_SIZE tokens
    - But text length (characters) doesn't always equal token count
    - BERT tokenizer breaks text into subword units (more granular than words)
    - Example: "don't" = 3 tokens: "do", "##n", "'t"
    
    The BERT tokenizer matches what sentence-transformers uses,
    so this gives us accurate chunk sizes for embedding.
    
    Fallback (4 chars per token):
    - If tokenizer unavailable, use rough approximation
    - Better than character-based splitting
    
    Args:
        text: Text to count tokens in
        
    Returns:
        Approximate token count
    """
    if _tokenizer:
        try:
            # Use the tokenizer to get exact token count
            tokens = _tokenizer.encode(text)
            return len(tokens.ids)
        except Exception:
            # If tokenizer fails, fall back to approximation
            pass
    
    # Fallback: rough approximation (1 token ≈ 4 characters)
    # This is based on empirical observations from various corpora
    return len(text) // 4


def create_chunks(text: str, metadata: dict) -> list[TextChunk]:
    """
    Split text into semantic chunks with overlap.
    
    Process:
    1. Calculate overlap amount in tokens from CHUNK_OVERLAP percentage
    2. Create RecursiveCharacterTextSplitter with:
       - Chunk size: CHUNK_SIZE tokens
       - Overlap: calculated from CHUNK_OVERLAP percentage
       - Separators: hierarchy from paragraphs → lines → sentences → words
       - Token counter: our token counting function
    3. Split the text
    4. Create TextChunk objects with enriched metadata:
       - chunk_index: position in sequence
       - total_chunks: total count
       - chunk_tokens: actual token count of this chunk
    
    Args:
        text: Text to chunk
        metadata: Original metadata from parser (passed through to chunks)
        
    Returns:
        List of TextChunk objects with enhanced metadata
    """
    # Calculate how many tokens of overlap we want
    # Example: CHUNK_SIZE=256, CHUNK_OVERLAP=50% → overlap_tokens=128
    overlap_tokens = int(CHUNK_SIZE * (CHUNK_OVERLAP / 100.0))
    
    # Create the text splitter with our configuration
    # Separators are tried in order until chunks are small enough
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,                           # Target chunk size in tokens
        chunk_overlap=overlap_tokens,                     # Overlap in tokens
        separators=["\n\n", "\n", ". ", " ", ""],        # Split hierarchy
        length_function=count_tokens,                     # Use our token counter
    )
    
    # Actually split the text
    chunks_text = splitter.split_text(text)
    
    # Create TextChunk objects with metadata for each chunk
    chunks = []
    for i, chunk_text in enumerate(chunks_text):
        # Copy original metadata so we know where this chunk came from
        chunk_metadata = metadata.copy()
        
        # Add chunk-specific metadata
        chunk_metadata["chunk_index"] = i                    # Which chunk (0-indexed)
        chunk_metadata["total_chunks"] = len(chunks_text)    # How many total
        chunk_metadata["chunk_tokens"] = count_tokens(chunk_text)  # Actual token count
        
        chunks.append(TextChunk(text=chunk_text, metadata=chunk_metadata))
    
    logger.debug(f"Created {len(chunks)} chunks (avg ~{CHUNK_SIZE} tokens)")
    
    return chunks
