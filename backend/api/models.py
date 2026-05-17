"""
Pydantic request and response models for the FastAPI layer.

This module keeps the HTTP schema in one place so route handlers,
tests, and downstream clients can share the same validation contract.
The route module imports these models directly to avoid duplicating the
same definitions across multiple files.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """Request payload for the `/api/ask` endpoint."""

    question: str = Field(..., description="User's question", min_length=1, max_length=1000)
    source_filter: str | None = Field(
        None,
        description="Optional: restrict to a specific book filename",
    )
    k: int = Field(5, description="Number of sources to retrieve", ge=1, le=20)


class AskResponse(BaseModel):
    """Response payload returned by the `/api/ask` endpoint."""

    answer: str = Field(..., description="Generated answer")
    citations: list[str] = Field(..., description="Source citations")
    confidence: float = Field(..., description="Confidence score (0-1)")
    num_sources: int = Field(..., description="Number of retrieved sources")
    question: str = Field(..., description="Original question")


class IngestRequest(BaseModel):
    """Request payload for the optional JSON ingestion workflow."""

    filename: str = Field(..., description="Original filename", max_length=255)


class IngestResponse(BaseModel):
    """Response payload returned after an ingest operation."""

    success: bool = Field(..., description="Whether ingestion succeeded")
    filename: str = Field(..., description="Ingested filename")
    chunks_added: int = Field(..., description="Number of chunks indexed")
    message: str = Field(..., description="Status message")


class StatusResponse(BaseModel):
    """Response payload for `/api/status`."""

    status: str = Field("ok", description="System status")
    indexed_chunks: int = Field(..., description="Total chunks in index")
    books_indexed: int = Field(..., description="Number of books")
    api_version: str = Field("1.0", description="API version")


class BooksResponse(BaseModel):
    """Response payload for `/api/books`."""

    books: list[str] = Field(..., description="List of indexed book filenames")
    count: int = Field(..., description="Total number of books")


class DeleteResponse(BaseModel):
    """Response payload for `/api/books/{filename}` DELETE."""

    success: bool = Field(..., description="Whether deletion succeeded")
    filename: str = Field(..., description="Deleted filename")
    message: str = Field(..., description="Status message")


__all__ = [
    "AskRequest",
    "AskResponse",
    "IngestRequest",
    "IngestResponse",
    "StatusResponse",
    "BooksResponse",
    "DeleteResponse",
]
