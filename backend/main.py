"""
Main FastAPI support application for Manly P. Hall AI Bot.

This is the HTTP API server for Phase 1e:
- REST endpoints for Q&A, ingestion, status
- Initialization of indexing and retrieval components
- Error handling and logging

The API can be accessed via HTTP or used as backend for Discord bot,
web frontend, or other integrations.

To run:
    PYTHONPATH=. python -m uvicorn backend.main:app --reload

Then visit:
    http://localhost:8000/docs (interactive API documentation)
    http://localhost:8000/redoc (ReDoc documentation)
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import API_HOST, API_PORT
from backend.api.routes import router, initialize_store


# ============================================================================
# Logging
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Lifespan Events (Startup/Shutdown)
# ============================================================================


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handle startup and shutdown events.
    
    Startup:
    - Initialize the ChromaStore (load indexed data)
    - Verify Ollama availability (warning if not)
    
    Shutdown:
    - Clean up resources
    """
    # Startup
    logger.info("🚀 Starting Manly P. Hall AI Bot API...")
    try:
        initialize_store()
        logger.info("✓ Store initialized")
    except Exception as e:
        logger.error(f"✗ Failed to initialize store: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")


# ============================================================================
# FastAPI App Configuration
# ============================================================================

app = FastAPI(
    title="Manly P. Hall AI Bot",
    description="A specialized AI assistant for esoteric knowledge",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware (allow requests from any origin for simplicity)
# In production, restrict to specific domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Include Routers
# ============================================================================

app.include_router(router)


# ============================================================================
# Health Check Endpoint
# ============================================================================

@app.get("/health")
def health_check():
    """
    Health check endpoint. Returns 200 if system is ready.
    
    Used by load balancers and monitoring systems to verify the API is alive.
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ready",
            "message": "Manly P. Hall AI Bot is running",
            "version": "1.0.0"
        }
    )


@app.get("/")
def root():
    """
    Root endpoint - provides API documentation links.
    """
    return {
        "title": "Manly P. Hall AI Bot API",
        "version": "1.0.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
        "status": "ready"
    }


# ============================================================================
# Error Handlers
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting API on {API_HOST}:{API_PORT}")
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )
