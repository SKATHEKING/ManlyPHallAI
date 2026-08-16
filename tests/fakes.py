"""
Test doubles for the pipeline's collaborators.

Before these existed there was no way to exercise the RAG pipeline without a real
Chroma database on disk, a real sentence-transformers model in memory, and a real
Ollama server on localhost. Every test therefore hit production data and silently
depended on infrastructure being up.

Each fake stands in for one collaborator and records what it was asked to do, so
tests can assert on the interaction rather than only on the final output.
"""

from __future__ import annotations

from typing import Iterator, Sequence

import numpy as np


class FakeStore:
    """
    In-memory stand-in for ChromaStore.

    `search` returns Chroma's native result envelope: every field is a list with
    one entry per query, and we only ever issue one query, hence the [[...]]
    nesting. Retrieval unpacks that shape directly, so the fake has to reproduce
    it faithfully or the test proves nothing.

    Distances follow Chroma's cosine convention, where 0 means identical. The
    retriever converts them with `1 - distance`, so a distance of 0.1 becomes a
    similarity of 0.9.
    """

    def __init__(self, hits: Sequence[dict] | None = None) -> None:
        """
        Args:
            hits: Ordered results to return from search(). Each dict takes the
                  keys `id`, `document`, `metadata` and `distance`.
        """
        self.hits = list(hits or [])
        self.searches: list[tuple] = []
        self.added: list[tuple] = []
        self.deleted: list[str] = []

    def search(self, query_embedding, k: int = 5) -> dict:
        self.searches.append((query_embedding, k))
        window = self.hits[:k]
        return {
            "ids": [[h["id"] for h in window]],
            "documents": [[h["document"] for h in window]],
            "metadatas": [[h["metadata"] for h in window]],
            "distances": [[h["distance"] for h in window]],
        }

    def get_collection_size(self) -> int:
        return len(self.hits)

    def add_chunks(self, chunks, embeddings_matrix) -> int:
        self.added.append((list(chunks), embeddings_matrix))
        return len(chunks)

    def delete_by_source(self, source_filename: str) -> int:
        self.deleted.append(source_filename)
        remaining = [h for h in self.hits
                     if h["metadata"].get("filename") != source_filename]
        removed = len(self.hits) - len(remaining)
        self.hits = remaining
        return removed


class FakeLLM:
    """
    Stand-in for OllamaLLM that answers instantly and records its prompts.

    Recording the prompt is the point: it lets a test assert that retrieved
    passages actually reached the model, which is the one thing the real
    end-to-end tests cannot check.
    """

    def __init__(self, response: str = "As above, so below.") -> None:
        self.response = response
        self.prompts: list[str] = []

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float | None = None) -> str:
        self.prompts.append(prompt)
        return self.response

    def generate_stream(self, prompt: str,
                        temperature: float | None = None) -> Iterator[str]:
        self.prompts.append(prompt)
        yield from self.response.split(" ")

    def is_running(self) -> bool:
        return True


class ExplodingLLM:
    """LLM double that always fails, for testing the error path."""

    def __init__(self, exc: Exception | None = None) -> None:
        self.exc = exc or ConnectionError("Ollama is not running")

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float | None = None) -> str:
        raise self.exc

    def generate_stream(self, prompt: str,
                        temperature: float | None = None) -> Iterator[str]:
        raise self.exc

    def is_running(self) -> bool:
        return False


def fake_embed(texts, batch_size=None) -> np.ndarray:
    """
    Deterministic stand-in for embed_texts.

    Produces a stable vector per input without loading a 90MB model. The values
    are meaningless for similarity; anything asserting on ranking should drive
    FakeStore's distances instead.
    """
    if isinstance(texts, str):
        texts = [texts]
    else:
        texts = list(texts)
    return np.array([[float(len(t) % 7), 0.0, 1.0] for t in texts], dtype=float)


__all__ = ["FakeStore", "FakeLLM", "ExplodingLLM", "fake_embed"]
