"""
Tests for ChromaStore against a real Chroma database in a temporary directory.

These are only possible because ChromaStore now takes its persist directory as an
argument. Previously it read a module constant, so every test touched the real
index in data/chroma_db.
"""

from __future__ import annotations

import numpy as np
import pytest

from backend.core.types import SearchHit, TextSegment
from backend.indexing.store import ChromaStore


@pytest.fixture
def store(tmp_path):
    """A real Chroma store, isolated in a temporary directory."""
    return ChromaStore(persist_dir=tmp_path / "chroma", collection_name="test_books")


def _segment(name: str, index: int, text: str) -> TextSegment:
    return TextSegment(
        text=text,
        metadata={"filename": name, "chunk_index": index,
                  "source": f"/books/{name}", "format": "txt"},
    )


class TestSearchHitConversion:
    """The distance-to-similarity conversion moved from retrieval into the store."""

    def test_score_is_the_complement_of_chroma_distance(self, store):
        """
        Query Chroma directly and through the store, and require the scores to
        agree. This pins the arithmetic to Chroma's actual output rather than to
        an assumption about it.
        """
        vectors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        store.add_chunks(
            [_segment("a.txt", 0, "first"),
             _segment("b.txt", 0, "second"),
             _segment("c.txt", 0, "third")],
            vectors,
        )

        query = np.array([1.0, 0.0, 0.0])

        raw = store.collection.query(
            query_embeddings=[query.tolist()], n_results=3,
            include=["distances"],
        )
        expected = [1 - d for d in raw["distances"][0]]

        hits = store.search(query, k=3)

        assert [h.score for h in hits] == pytest.approx(expected)

    def test_returns_search_hits_not_raw_chroma(self, store):
        store.add_chunks([_segment("a.txt", 0, "first")], np.array([[1.0, 0.0, 0.0]]))

        hits = store.search(np.array([1.0, 0.0, 0.0]), k=1)

        assert isinstance(hits, list)
        assert isinstance(hits[0], SearchHit)
        assert hits[0].text == "first"
        assert hits[0].metadata["filename"] == "a.txt"

    def test_identical_vector_scores_near_one(self, store):
        store.add_chunks([_segment("a.txt", 0, "first")], np.array([[1.0, 0.0, 0.0]]))

        hit = store.search(np.array([1.0, 0.0, 0.0]), k=1)[0]

        assert hit.score == pytest.approx(1.0, abs=1e-6)

    def test_empty_collection_returns_no_hits(self, store):
        assert store.search(np.array([1.0, 0.0, 0.0]), k=5) == []


class TestIsolation:
    """The constructor arguments are what make these tests independent."""

    def test_two_stores_do_not_share_data(self, tmp_path):
        first = ChromaStore(persist_dir=tmp_path / "one", collection_name="books")
        second = ChromaStore(persist_dir=tmp_path / "two", collection_name="books")

        first.add_chunks([_segment("a.txt", 0, "only in first")],
                         np.array([[1.0, 0.0, 0.0]]))

        assert first.get_collection_size() == 1
        assert second.get_collection_size() == 0

    def test_delete_by_source_removes_only_that_file(self, store):
        store.add_chunks(
            [_segment("a.txt", 0, "keep"), _segment("b.txt", 0, "remove")],
            np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]),
        )

        removed = store.delete_by_source("b.txt")

        assert removed == 1
        assert store.get_collection_size() == 1

    def test_delete_by_unknown_source_removes_nothing(self, store):
        store.add_chunks([_segment("a.txt", 0, "keep")], np.array([[1.0, 0.0, 0.0]]))

        assert store.delete_by_source("nope.txt") == 0
        assert store.get_collection_size() == 1
