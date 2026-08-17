"""
FastAPI route definitions for REST endpoints.

This module provides HTTP API endpoints for the RAG system (Phase 1e):
- POST /ask: Answer a question using indexed books
- POST /ingest: Add a new book to the index
- GET /status: System health and statistics
- GET /books: List indexed books
- DELETE /books/{filename}: Remove a book from index

All endpoints use the ingestion → indexing → retrieval → generation pipeline.

This layer exposes the RAG system for:
- Web applications
- Discord bot backend
- External integrations
- Direct HTTP clients

Example usage:
    POST /ask
    {"question": "What is enlightenment?"}
    
    Response:
    {
        "answer": "Enlightenment is...",
        "citations": ["book.pdf, page 42", ...],
        "confidence": 0.75,
        "num_sources": 3
    }
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File

from backend.api.models import (
    AskRequest,
    AskResponse,
    BooksResponse,
    DeleteResponse,
    IngestResponse,
    StatusResponse,
)
from backend.generation import answer_question
from backend.indexing import ChromaStore
from backend.indexing.embedder import embed_texts
from backend.ingestion import ingest_document
from backend.config import BOOKS_DIR


logger = logging.getLogger(__name__)

# Create router for all /api routes
router = APIRouter(prefix="/api", tags=["RAG"])

# Global store instance (initialized on startup)
_store: Optional[ChromaStore] = None


# ============================================================================
# Initialization
# ============================================================================


def initialize_store() -> ChromaStore:
    """
    Initialize the global ChromaStore.
    
    Called on startup to load existing indexed data.
    
    Returns:
        ChromaStore instance
        
    Raises:
        RuntimeError: If store cannot be initialized
    """
    global _store
    
    try:
        _store = ChromaStore()
        count = _store.get_collection_size()
        logger.info(f"✓ Initialized store with {count} indexed chunks")
        return _store
    except Exception as e:
        logger.error(f"Failed to initialize store: {e}")
        raise RuntimeError(f"Cannot initialize vector store: {e}")


# ============================================================================
# Endpoints
# ============================================================================


@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """
    Answer a question using indexed books.
    
    This is the main endpoint for Q&A. The question is:
    1. Embedded using sentence-transformers
    2. Searched against indexed chunks
    3. Used to generate a grounded answer via Ollama
    4. Returned with citations
    
    Args:
        request: AskRequest with question and optional filters
        
    Returns:
        AskResponse with answer, citations, and metadata
        
    Raises:
        HTTPException: If question is empty or generation fails
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    if _store is None:
        raise HTTPException(status_code=500, detail="Store not initialized")
    
    try:
        logger.info(f"Question: {request.question[:100]}")
        
        # Generate answer
        if request.source_filter:
            # TODO: Implement source filtering
            logger.warning(f"Source filter not yet implemented: {request.source_filter}")
        
        result = answer_question(request.question, _store, k=request.k)
        
        return AskResponse(
            answer=result.text,
            citations=result.citations,
            confidence=result.confidence,
            num_sources=len(result.retrieved_chunks),
            question=request.question,
        )
        
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.post("/ingest", response_model=IngestResponse)
async def ingest(
    file: UploadFile = File(...),
) -> IngestResponse:
    """
    Ingest a new book document and add to index.
    
    Uploaded file must be one of: PDF, EPUB, or TXT.
    
    Process:
    1. Save uploaded file temporarily
    2. Ingest document (parse, clean, chunk)
    3. Generate embeddings
    4. Store in vector DB
    5. Return statistics
    
    Args:
        file: Uploaded document file
        
    Returns:
        IngestResponse with statistics
        
    Raises:
        HTTPException: If file format unsupported or ingestion fails
    """
    if _store is None:
        raise HTTPException(status_code=500, detail="Store not initialized")
    
    try:
        # Validate file extension
        suffix = Path(file.filename).suffix.lower()
        if suffix not in [".pdf", ".epub", ".txt"]:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {suffix}. Supported: .pdf, .epub, .txt"
            )
        
        # Save file temporarily
        file_path = BOOKS_DIR / file.filename
        content = await file.read()
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Ingesting: {file.filename}")
        
        # Ingest document
        chunks = ingest_document(file_path)

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail=f"No content could be extracted from {file.filename}",
            )

        embeddings = embed_texts([chunk.text for chunk in chunks])
        
        # Index chunks
        _store.add_chunks(chunks, embeddings)
        
        logger.info(f"Ingested {file.filename}: {len(chunks)} chunks")
        
        return IngestResponse(
            success=True,
            filename=file.filename,
            chunks_added=len(chunks),
            message=f"Successfully indexed {len(chunks)} chunks",
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ingest document: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@router.get("/status", response_model=StatusResponse)
async def status() -> StatusResponse:
    """
    Get system status and statistics.
    
    Returns:
        StatusResponse with index size and health info
        
    Raises:
        HTTPException: If store is unavailable
    """
    if _store is None:
        raise HTTPException(status_code=500, detail="Store not initialized")
    
    try:
        indexed_chunks = _store.get_collection_size()
        
        # TODO: Get unique book count from metadata
        books_indexed = 1  # Placeholder
        
        return StatusResponse(
            status="ok",
            indexed_chunks=indexed_chunks,
            books_indexed=books_indexed,
            api_version="1.0",
        )
        
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")


@router.get("/books", response_model=BooksResponse)
async def list_books() -> BooksResponse:
    """
    List all indexed books.
    
    Returns:
        BooksResponse with book filenames
        
    Raises:
        HTTPException: If store is unavailable
    """
    if _store is None:
        raise HTTPException(status_code=500, detail="Store not initialized")
    
    try:
        # TODO: Retrieve unique filenames from store metadata
        # For now, list files in BOOKS_DIR
        books = []
        for file in BOOKS_DIR.glob("*"):
            if file.is_file() and file.suffix in [".pdf", ".epub", ".txt"]:
                books.append(file.name)
        
        return BooksResponse(
            books=sorted(books),
            count=len(books),
        )
        
    except Exception as e:
        logger.error(f"Failed to list books: {e}")
        raise HTTPException(status_code=500, detail=f"List failed: {str(e)}")


@router.delete("/books/{filename}", response_model=DeleteResponse)
async def delete_book(filename: str) -> DeleteResponse:
    """
    Remove a book from the index.
    
    Args:
        filename: Name of book to delete
        
    Returns:
        DeleteResponse with deletion status
        
    Raises:
        HTTPException: If deletion fails
    """
    if _store is None:
        raise HTTPException(status_code=500, detail="Store not initialized")

    # filename is joined onto BOOKS_DIR and passed to unlink() below. Resolve the
    # join and require the result to sit directly inside BOOKS_DIR: that rejects
    # "..", ".", embedded separators, and symlinks pointing out of the directory.
    books_dir = BOOKS_DIR.resolve()
    file_path = (books_dir / filename).resolve()
    if file_path.parent != books_dir:
        raise HTTPException(status_code=400, detail=f"Invalid filename: {filename}")

    try:
        # Delete all chunks with this source
        chunks_deleted = _store.delete_by_source(filename)

        # Attempt the unlink rather than checking first. exists() + unlink() is
        # a check-then-act race: if the file goes away in between, unlink raises
        # FileNotFoundError and a successful delete is reported as a 500.
        try:
            file_path.unlink()
            file_existed = True
        except FileNotFoundError:
            file_existed = False

        # Nothing indexed and no file on disk: the book was never here
        if not chunks_deleted and not file_existed:
            raise HTTPException(status_code=404, detail=f"Book not found: {filename}")

        logger.info(f"Deleted book: {filename} ({chunks_deleted} chunks)")

        return DeleteResponse(
            success=True,
            filename=filename,
            message=f"Successfully deleted {filename}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete book: {e}")
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


__all__ = ["router", "initialize_store"]
