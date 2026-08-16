"""
Ingestion module for parsing and extracting text from book files.
Handles PDF, EPUB, and plain text formats.

This module orchestrates the entire ingestion pipeline:
1. Parse documents (PDF/EPUB/TXT) → extract text and structure
2. Clean text → remove control chars, HTML, normalize whitespace
3. Chunk text → split into semantic pieces with overlap

Main entry point: ingest_document(file_path) -> list[Chunk]

Example usage:
    from backend.ingestion import ingest_document
    
    chunks = ingest_document("data/books/my_book.pdf")
    for chunk in chunks:
        print(f"Text: {chunk.text[:100]}...")
        print(f"Page: {chunk.metadata['page']}")
        print(f"Chunk {chunk.metadata['chunk_index']} of {chunk.metadata['total_chunks']}")

The ingestion pipeline is the foundation for the entire system:
- Output chunks are passed to the indexing layer (for embeddings + vector DB)
- Metadata is preserved so we can cite sources accurately
- Cleaning ensures text quality for downstream ML models
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.core.types import TextSegment
from backend.ingestion.parsers import parse_document
from backend.ingestion.cleaner import clean_text
from backend.ingestion.chunker import create_chunks, TextChunk


logger = logging.getLogger(__name__)


# Alias onto the shared type; the original docstring now lives on TextSegment.
# Because Chunk and TextChunk are now the same type, the pipeline below no longer
# needs to rebuild one from the other field by field.
Chunk = TextSegment


def ingest_document(file_path: Path | str) -> list[Chunk]:
    """
    End-to-end ingestion pipeline: parse → clean → chunk.
    
    This is the main entry point. It:
    1. Validates the file exists
    2. Calls parse_document() to extract text and preserve structure
    3. Cleans each parsed segment
    4. Chunks each segment with overlap
    5. Converts to final Chunk format
    6. Returns all chunks ready for indexing
    
    Error handling:
    - If file doesn't exist, logs error and returns empty list
    - If parsing fails, logs warning and skips that document
    - If text is empty after cleaning, logs warning and skips
    - Designed to fail gracefully (return what could be processed)
    
    Args:
        file_path: Path to document file (PDF, EPUB, or TXT)
        
    Returns:
        List of ingested chunks ready for indexing (or empty list on error)
    """
    file_path = Path(file_path)
    
    # Validate that the file exists before attempting to parse
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return []
    
    logger.info(f"Ingesting: {file_path}")
    
    # Step 1: PARSE - Extract text and structure from document
    # Returns list of ParsedDocument (one per page/chapter for PDF/EPUB)
    parsed_docs = parse_document(file_path)
    if not parsed_docs:
        logger.warning(f"No content parsed from {file_path}")
        return []
    
    # Step 2-3: Process each parsed segment (page or chapter)
    # For PDFs: each page becomes a ParsedDocument
    # For EPUBs: each chapter becomes a ParsedDocument
    # For TXT: the whole file is one ParsedDocument
    all_chunks: list[Chunk] = []
    
    for parsed_doc in parsed_docs:
        # CLEAN - Remove formatting artifacts and normalize
        cleaned_text = clean_text(parsed_doc.text)
        
        # Skip if nothing left after cleaning
        if not cleaned_text:
            logger.warning(f"Empty text after cleaning for {file_path}")
            continue
        
        # CHUNK - Split into semantic pieces with overlap
        text_chunks = create_chunks(cleaned_text, parsed_doc.metadata)
        
        # Chunk and TextChunk are the same type now, so the chunks the chunker
        # produced are already the final output format.
        all_chunks.extend(text_chunks)
    
    logger.info(f"✓ Ingestion complete: {len(all_chunks)} chunks from {file_path}")
    
    return all_chunks


__all__ = ["ingest_document", "Chunk"]
