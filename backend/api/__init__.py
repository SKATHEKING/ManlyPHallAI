"""
API module for REST endpoints.
Handles request/response models and route definitions.

Main exports:
- router: FastAPI router with all endpoints
- initialize_store: Initialize the ChromaStore
- Request/Response models for validation

Endpoints:
- POST /api/ask: Answer a question
- POST /api/ingest: Add a book to the index
- GET /api/status: System status
- GET /api/books: List indexed books
- DELETE /api/books/{filename}: Remove a book
"""

from backend.api.routes import (
    router,
    initialize_store,
    AskRequest,
    AskResponse,
    IngestRequest,
    IngestResponse,
    StatusResponse,
    BooksResponse,
    DeleteResponse,
)


__all__ = [
    "router",
    "initialize_store",
    "AskRequest",
    "AskResponse",
    "IngestRequest",
    "IngestResponse",
    "StatusResponse",
    "BooksResponse",
    "DeleteResponse",
]
