"""
Main FastAPI application for Manly P. Hall AI Bot.
Phase 1: Book-based question answering.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.config import API_HOST, API_PORT, LOG_LEVEL
import logging

# ============================================================================
# Logging
# ============================================================================
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App
# ============================================================================
app = FastAPI(
    title="Manly P. Hall AI Bot",
    description="A specialized AI assistant for esoteric knowledge",
    version="0.1.0",
)

# ============================================================================
# Health Check Endpoint
# ============================================================================
@app.get("/health")
def health_check():
    """
    Health check endpoint. Returns 200 if system is ready.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "message": "Manly P. Hall AI Bot is running"}
    )

# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )
