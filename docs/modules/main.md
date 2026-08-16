# `backend/main.py` — FastAPI application

Design notes extracted from the module's docstrings. The HTTP API server for
Phase 1e.

## Responsibilities

- REST endpoints for Q&A, ingestion, status
- Initialization of indexing and retrieval components
- Error handling and logging

The API can be accessed over HTTP or used as the backend for the Discord bot, a
web frontend, or other integrations.

## Running it

```bash
PYTHONPATH=. python -m uvicorn backend.main:app --reload
```

Then visit:

- <http://localhost:8000/docs> — interactive API documentation
- <http://localhost:8000/redoc> — ReDoc documentation

## Startup

The vector store is created during the application lifespan, before the first
request is served. A failure there re-raises and the application does not start,
which is why the handlers can assume a working store rather than each checking
for one.

A global exception handler converts any uncaught error into a 500, so individual
endpoints do not need their own catch-all wrappers.
