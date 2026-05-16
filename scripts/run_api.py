"""
Convenience script for starting the FastAPI server.

Usage:
    python scripts/run_api.py

Then visit:
    http://localhost:8000/docs (interactive API docs)
    http://localhost:8000/redoc (ReDoc docs)
"""

if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # Add project root to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    import uvicorn
    from backend.config import API_HOST, API_PORT
    from backend.main import app
    
    print(f"\n🚀 Starting Manly P. Hall AI API Server")
    print(f"📍 http://{API_HOST}:{API_PORT}")
    print(f"📚 API Docs: http://{API_HOST}:{API_PORT}/docs\n")
    
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )
