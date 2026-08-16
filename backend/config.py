"""
Configuration for Manly P. Hall AI Bot.
Centralized settings for ingestion, indexing, retrieval, and generation.

Values live on the Settings model below and are read from the environment or a
.env file, so everything .env.example and docker-compose.yml advertise now
actually takes effect. Previously these were plain module constants and only the
DISCORD_* ones consulted the environment at all.

Use get_settings() to obtain the process-wide instance. It is cached, so repeated
calls are free, and the cache can be cleared in tests to load a different
configuration:

    from backend.config import get_settings
    settings = get_settings()
    print(settings.chunk_size)

The module-level constants further down are a backwards-compatible shim over the
same values, kept so existing importers continue to work unchanged.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """
    Every tunable value in the system, in one validated place.

    Each field can be overridden by an environment variable of the same name in
    upper case (chunk_size -> CHUNK_SIZE), or by an entry in .env.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ========================================================================
    # Paths
    # ========================================================================
    # Only the root is configurable; the rest derive from it, so pointing
    # DATA_DIR at a temporary directory relocates the whole data layout at once.
    data_dir: Path = PROJECT_ROOT / "data"
    logs_dir: Path = PROJECT_ROOT / "logs"

    # ========================================================================
    # Ingestion & Chunking
    # ========================================================================
    chunk_size: int = 256  # Tokens per chunk
    chunk_overlap: int = 50  # Percentage overlap (0-100)
    chunk_separator: str = "\n\n"  # Primary separator (paragraph breaks)
    tokenizer_model: str = "bert-base-uncased"  # Used only to count tokens

    # ========================================================================
    # Embeddings
    # ========================================================================
    embedding_model: str = "all-MiniLM-L6-v2"  # sentence-transformers model
    embedding_dimension: int = 384  # Output dimension of all-MiniLM-L6-v2
    embedding_batch_size: int = 32  # Batch size for embedding generation

    # ========================================================================
    # Vector Store (Chroma)
    # ========================================================================
    chroma_collection_name: str = "books"

    # ========================================================================
    # Retrieval
    # ========================================================================
    retrieval_k: int = 5  # Number of passages to retrieve
    relevance_threshold: float = 0.3  # Minimum similarity score (0.0-1.0)
    #                                   With cosine distance on normalized embeddings:
    #                                   0.3 = reasonably similar (typical for semantic search)
    #                                   0.5 = very similar (too strict for short queries)

    # ========================================================================
    # LLM (Ollama)
    # ========================================================================
    ollama_model: str = "llama2:7b"  # Model to use for generation
    # OLLAMA_URL is accepted too, because docker-compose.yml sets that name.
    ollama_base_url: str = Field(
        "http://localhost:11434",  # Ollama API URL
        validation_alias=AliasChoices("OLLAMA_BASE_URL", "OLLAMA_URL"),
    )
    max_context_length: int = 2048  # Max tokens in prompt to LLM
    llm_temperature: float = 0.3  # Lower = more deterministic
    llm_top_p: float = 0.9  # Nucleus sampling
    llm_top_k: int = 40  # Sample from the k most likely tokens

    # ========================================================================
    # API Server
    # ========================================================================
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True  # Auto-reload on code changes during development

    # ========================================================================
    # Discord Bot
    # ========================================================================
    discord_token: str = ""
    discord_guild_id: int | None = None
    discord_command_prefix: str = "!"
    discord_status_channel_id: int | None = None

    # ========================================================================
    # Logging
    # ========================================================================
    log_level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # ========================================================================
    # Development
    # ========================================================================
    debug: bool = False

    @property
    def books_dir(self) -> Path:
        """Where uploaded and ingested source books are kept."""
        return self.data_dir / "books"

    @property
    def chroma_dir(self) -> Path:
        """On-disk location of the Chroma vector index."""
        return self.data_dir / "chroma_db"

    @property
    def models_dir(self) -> Path:
        """Cache directory for the downloaded embeddings model."""
        return self.data_dir / "models"


@lru_cache
def get_settings() -> Settings:
    """
    Return the process-wide Settings, constructing it on first use.

    lru_cache is the Pythonic singleton: one instance per process, and
    get_settings.cache_clear() lets a test load a different configuration --
    which a __new__-based singleton would make impossible.
    """
    return Settings()


# ============================================================================
# Backwards-compatible constants
# ============================================================================
# The names below are the original module-level constants. They are now derived
# from Settings so there is a single source of truth. Directories are no longer
# created on import: a configuration module should not touch the filesystem as a
# side effect of being imported. Each writer creates what it needs.
_settings = get_settings()

DATA_DIR = _settings.data_dir
BOOKS_DIR = _settings.books_dir
CHROMA_DB_DIR = _settings.chroma_dir
MODELS_DIR = _settings.models_dir
LOGS_DIR = _settings.logs_dir

CHUNK_SIZE = _settings.chunk_size
CHUNK_OVERLAP = _settings.chunk_overlap
CHUNK_SEPARATOR = _settings.chunk_separator

EMBEDDING_MODEL = _settings.embedding_model
EMBEDDING_DIMENSION = _settings.embedding_dimension
EMBEDDING_BATCH_SIZE = _settings.embedding_batch_size

CHROMA_COLLECTION_NAME = _settings.chroma_collection_name
CHROMA_PERSIST_DIR = str(_settings.chroma_dir)

RETRIEVAL_K = _settings.retrieval_k
RELEVANCE_THRESHOLD = _settings.relevance_threshold

OLLAMA_MODEL = _settings.ollama_model
OLLAMA_BASE_URL = _settings.ollama_base_url
MAX_CONTEXT_LENGTH = _settings.max_context_length
LLM_TEMPERATURE = _settings.llm_temperature
LLM_TOP_P = _settings.llm_top_p

API_HOST = _settings.api_host
API_PORT = _settings.api_port
API_RELOAD = _settings.api_reload

DISCORD_TOKEN = _settings.discord_token
DISCORD_GUILD_ID = _settings.discord_guild_id
DISCORD_COMMAND_PREFIX = _settings.discord_command_prefix
DISCORD_STATUS_CHANNEL_ID = _settings.discord_status_channel_id

LOG_LEVEL = _settings.log_level
LOG_FORMAT = _settings.log_format

DEBUG = _settings.debug
