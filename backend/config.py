"""
Configuration for Manly P. Hall AI Bot.
Centralized settings for ingestion, indexing, retrieval, and generation.
"""

import os
from pathlib import Path


def _optional_int_env(name: str) -> int | None:
    value = os.getenv(name)
    return int(value) if value else None

# ============================================================================
# Paths
# ============================================================================
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
BOOKS_DIR = DATA_DIR / "books"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
MODELS_DIR = DATA_DIR / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Ensure directories exist
for dir_path in [DATA_DIR, BOOKS_DIR, CHROMA_DB_DIR, MODELS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Ingestion & Chunking
# ============================================================================
CHUNK_SIZE = 256  # Tokens per chunk
CHUNK_OVERLAP = 50  # Percentage overlap (0-100)
CHUNK_SEPARATOR = "\n\n"  # Primary separator (paragraph breaks)

# ============================================================================
# Embeddings
# ============================================================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # sentence-transformers model
EMBEDDING_DIMENSION = 384  # Output dimension of all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE = 32  # Batch size for embedding generation

# ============================================================================
# Vector Store (Chroma)
# ============================================================================
CHROMA_COLLECTION_NAME = "books"
CHROMA_PERSIST_DIR = str(CHROMA_DB_DIR)

# ============================================================================
# Retrieval
# ============================================================================
RETRIEVAL_K = 5  # Number of passages to retrieve
RELEVANCE_THRESHOLD = 0.3  # Minimum similarity score (0.0-1.0)
                           # With cosine distance on normalized embeddings:
                           # 0.3 = reasonably similar (typical for semantic search)
                           # 0.5 = very similar (too strict for short queries)

# ============================================================================
# LLM (Ollama)
# ============================================================================
OLLAMA_MODEL = "llama2:7b"  # Model to use for generation
OLLAMA_BASE_URL = "http://localhost:11434"  # Ollama API URL
MAX_CONTEXT_LENGTH = 2048  # Max tokens in prompt to LLM
LLM_TEMPERATURE = 0.3  # Lower = more deterministic
LLM_TOP_P = 0.9  # Nucleus sampling

# ============================================================================
# API Server
# ============================================================================
API_HOST = "0.0.0.0"
API_PORT = 8000
API_RELOAD = True  # Auto-reload on code changes during development

# ============================================================================
# Discord Bot
# ============================================================================
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "")
DISCORD_GUILD_ID = _optional_int_env("DISCORD_GUILD_ID")
DISCORD_COMMAND_PREFIX = os.getenv("DISCORD_COMMAND_PREFIX", "!")
DISCORD_STATUS_CHANNEL_ID = _optional_int_env("DISCORD_STATUS_CHANNEL_ID")

# ============================================================================
# Logging
# ============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# Development
# ============================================================================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
