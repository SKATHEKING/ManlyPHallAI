"""
Download and cache the sentence-transformers embedding model.
Run this once to avoid long delays on first ingestion.

Usage:
    python scripts/download_embeddings_model.py

To be implemented in Phase 1a.
"""

# Phase 1a: Download the embedding model for Discord bot ingestion and retrieval.

from __future__ import annotations

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import EMBEDDING_MODEL, MODELS_DIR

try:    # Ensure the models directory exists
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError as exc:  # pragma: no cover - environment guard
    raise SystemExit(
        "sentence-transformers is not installed. Run `pip install -r requirements.txt` first."
    ) from exc


os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODELS_DIR)

print(f"Downloading model: {EMBEDDING_MODEL}")
print(f"Cache directory: {MODELS_DIR}")

model = SentenceTransformer(EMBEDDING_MODEL)

print("✓ Model downloaded successfully!")
print(f"✓ Model dimension: {model.get_embedding_dimension()}")
