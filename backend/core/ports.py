"""
The interfaces the pipeline depends on, as structural types.

These are Protocols, not base classes. Nothing has to inherit from them or
declare that it implements them: a class conforms simply by having the right
methods. ChromaStore and OllamaLLM already satisfy these as written, so the
interfaces could be introduced without editing either one.

That is what makes substitution possible. Retrieval and generation ask for a
Searchable or an LLM, and a test can hand them an in-memory fake -- which is why
the pipeline can now be exercised without a Chroma database on disk, a 90MB model
in memory, or an Ollama server on localhost.

The protocols are split rather than merged so that each consumer asks for the
narrowest thing it needs: retrieval only ever searches, so it depends on
Searchable, and a fake for it needs two methods rather than five.

Deliberately not @runtime_checkable: isinstance() against a Protocol only checks
that method *names* exist, not their signatures, which gives false confidence.
Conformance is enforced by the type checker instead.
"""

from __future__ import annotations

from typing import Callable, Iterable, Iterator, Protocol, Sequence

import numpy as np

from backend.core.types import SearchHit, TextSegment


class Searchable(Protocol):
    """The read-only surface of a vector store, which is all retrieval needs."""

    def search(self, query_embedding, k: int = 5) -> list[SearchHit]:
        """Return up to k chunks most similar to the query embedding."""
        ...

    def get_collection_size(self) -> int:
        """Return the number of chunks currently indexed."""
        ...


class VectorStore(Searchable, Protocol):
    """A store that can also be written to, as ingestion and deletion require."""

    def add_chunks(self, chunks: Sequence[TextSegment], embeddings_matrix) -> int:
        """Index the given chunks with their pre-computed embeddings."""
        ...

    def delete_by_source(self, source_filename: str) -> int:
        """Remove every chunk originating from one file; return how many went."""
        ...


class LLM(Protocol):
    """
    A text generator.

    The signatures match OllamaLLM's existing methods exactly, so it conforms
    without modification, and any replacement -- an OpenAI client, a canned fake,
    a null implementation for offline use -- only has to provide these three.
    """

    def generate(self, prompt: str, max_tokens: int = 512,
                 temperature: float | None = None) -> str:
        """Generate a complete response for the prompt."""
        ...

    def generate_stream(self, prompt: str,
                        temperature: float | None = None) -> Iterator[str]:
        """Yield the response in fragments as they are produced."""
        ...

    def is_running(self) -> bool:
        """Report whether the backing service is reachable."""
        ...


# Single-function interfaces are Callable aliases rather than one-method Protocol
# classes; the class would be pure ceremony around a function signature.
EmbedFn = Callable[[str | Iterable[str]], np.ndarray]
ProgressFn = Callable[[str], None]


__all__ = ["Searchable", "VectorStore", "LLM", "EmbedFn", "ProgressFn"]
