"""
API module for REST endpoints.
Handles request/response models and route definitions.

Exports and the endpoint list: docs/modules/packages.md
"""

from backend.api.routes import (
    router,
    initialize_store,
)
from backend.api.models import (
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
