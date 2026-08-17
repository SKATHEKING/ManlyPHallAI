"""
Characterization tests: pin the CURRENT behaviour of the pure pipeline functions.

These are not tests of what the code *should* do. They record what it *does*, so a
refactor that changes observable behaviour fails loudly instead of silently. Every
literal here was captured from the pre-refactor code, not written by hand.

The existing end-to-end tests cannot serve this purpose: they assert things like
`"sources" in data or "citations" in data`, which passes for almost any change.

Where a value below looks wrong, it probably is — the drift between the two
citation renderers is real and deliberately recorded. Fixing it is a behaviour
change and belongs in its own commit, which will update these expectations.
"""

from __future__ import annotations

import pytest

from backend.generation.answer import _format_citations
from backend.generation.prompts import build_rag_prompt
from backend.ingestion.chunker import count_tokens, create_chunks
from backend.retrieval.retriever import retrieve_chunks
from tests.fakes import FakeStore, fake_embed


# A fixed retrieval result covering the three metadata shapes that exist:
# a PDF chunk with a page, a second chunk from the same source (exercises
# citation de-duplication), and an EPUB chunk with a chapter and no page.
RETRIEVED = [
    {"text": "All is Mind. The universe is mental.", "source": "/books/kybalion.pdf",
     "filename": "kybalion.pdf", "page": 12, "chapter": None, "chunk_index": 0,
     "score": 0.87, "metadata": {}, "rank": 1},
    {"text": "As above, so below.", "source": "/books/kybalion.pdf",
     "filename": "kybalion.pdf", "page": 13, "chapter": None, "chunk_index": 1,
     "score": 0.71, "metadata": {}, "rank": 2},
    {"text": "Chapter text about vibration.", "source": "/books/hall.epub",
     "filename": "hall.epub", "page": None, "chapter": 3, "chunk_index": 0,
     "score": 0.55, "metadata": {}, "rank": 3},
]


class TestPromptBuilding:
    """Pins build_rag_prompt byte for byte."""

    def test_prompt_is_unchanged(self):
        expected = (
            "You are a helpful assistant answering questions based on provided passages.\n"
            "IMPORTANT: Answer ONLY using the provided passages.\n"
            "If the answer is not in the passages, say 'I don't know' or "
            "'This information is not in the provided passages.'\n"
            "Be accurate and cite your sources.\n"
            "Avoid speculation or information not in the passages.\n"
            "\n"
            "PASSAGES:\n"
            "[Passage 1]\n"
            "All is Mind. The universe is mental.\n"
            "(Source: kybalion.pdf, page 12, Relevance: 87%)\n"
            "\n"
            "[Passage 2]\n"
            "As above, so below.\n"
            "(Source: kybalion.pdf, page 13, Relevance: 71%)\n"
            "\n"
            "[Passage 3]\n"
            "Chapter text about vibration.\n"
            "(Source: hall.epub, section 0, Relevance: 55%)\n"
            "\n"
            "Question: What is mentalism?\n"
            "Answer: Answer the question using only the passages above. "
            "Cite which passage(s) you used. "
            "If the answer is not in the passages, say you don't know."
        )
        assert build_rag_prompt("What is mentalism?", RETRIEVED) == expected

    def test_prompt_with_no_context(self):
        assert build_rag_prompt("What is mentalism?", []) == (
            "Question: What is mentalism?\n\nNo context available."
        )

    def test_prompt_labels_a_chapter_chunk_by_section_not_chapter(self):
        """
        Recorded drift, not an endorsement.

        The EPUB chunk carries chapter=3, but the prompt renders 'section 0' from
        chunk_index because build_rag_prompt only branches on page. The user-facing
        citation for the same chunk says 'Chapter: 3' — see TestCitations.
        """
        prompt = build_rag_prompt("q", [RETRIEVED[2]])
        assert "(Source: hall.epub, section 0, Relevance: 55%)" in prompt
        assert "Chapter: 3" not in prompt


class TestCitations:
    """Pins _format_citations, including its de-duplication rule."""

    def test_citations_are_unchanged(self):
        assert _format_citations(RETRIEVED) == [
            "kybalion.pdf, Page 12",
            "hall.epub, Chapter: 3",
        ]

    def test_dedupes_on_source_path_keeping_the_first(self):
        """
        Two chunks share /books/kybalion.pdf, so only the first is cited and
        page 13 never appears. De-duplication keys on the full `source` path
        while the rendered string uses the `filename` basename.
        """
        citations = _format_citations(RETRIEVED)
        assert len(citations) == 2
        assert "Page 13" not in " ".join(citations)

    def test_chapter_takes_precedence_over_page(self):
        chunk = dict(RETRIEVED[2], page=99, chapter=3)
        assert _format_citations([chunk]) == ["hall.epub, Chapter: 3"]

    def test_empty_input(self):
        assert _format_citations([]) == []


class TestChunking:
    """Pins chunk boundaries, indices and the token counter."""

    TEXT = ("The Principle of Mentalism. All is Mind. " * 40).strip()
    META = {"source": "/books/kybalion.pdf", "format": "pdf",
            "filename": "kybalion.pdf", "page": 12}

    def test_real_tokenizer_is_loaded(self):
        """
        Canary for the silent fallback.

        chunker falls back to len(text)//4 if the tokenizer fails to load, which
        changes every chunk boundary. The real BERT tokenizer counts 4 for this
        input; the fallback would return 2.
        """
        assert count_tokens("hello world") == 4

    def test_chunk_count_and_indices(self):
        chunks = create_chunks(self.TEXT, self.META)
        assert len(chunks) == 5
        assert [c.metadata["chunk_index"] for c in chunks] == [0, 1, 2, 3, 4]
        assert all(c.metadata["total_chunks"] == 5 for c in chunks)

    def test_chunk_token_counts(self):
        chunks = create_chunks(self.TEXT, self.META)
        assert [c.metadata["chunk_tokens"] for c in chunks] == [141, 142, 142, 142, 123]

    def test_chunk_boundaries(self):
        """The overlap means every chunk after the first starts mid-sentence."""
        chunks = create_chunks(self.TEXT, self.META)
        assert chunks[0].text[:40] == "The Principle of Mentalism. All is Mind."
        for chunk in chunks[1:]:
            assert chunk.text[:40] == ". The Principle of Mentalism. All is Min"

    def test_source_metadata_is_carried_through(self):
        chunks = create_chunks(self.TEXT, self.META)
        assert sorted(chunks[0].metadata) == [
            "chunk_index", "chunk_tokens", "filename", "format",
            "page", "source", "total_chunks",
        ]
        assert chunks[0].metadata["page"] == 12
        assert chunks[0].metadata["filename"] == "kybalion.pdf"

    def test_chunk_index_restarts_per_call(self):
        """
        Recorded bug, pinned so the fix is visibly a change.

        create_chunks numbers from 0 on every call, and ingest_document calls it
        once per page. Combined with the chunk id f"{filename}_{chunk_index}",
        every page produces an id ending _0, so pages collide in the store.
        """
        first = create_chunks(self.TEXT, self.META)
        second = create_chunks(self.TEXT, dict(self.META, page=13))
        assert first[0].metadata["chunk_index"] == 0
        assert second[0].metadata["chunk_index"] == 0


class TestRetrieval:
    """Pins the retrieval result shape and the distance-to-score conversion."""

    HITS = [
        {"id": "kybalion.pdf_0", "document": "All is Mind.", "distance": 0.13,
         "metadata": {"source": "/books/kybalion.pdf", "filename": "kybalion.pdf",
                      "page": 12, "chunk_index": 0, "format": "pdf"}},
        {"id": "hall.epub_0", "document": "Vibration.", "distance": 0.45,
         "metadata": {"source": "/books/hall.epub", "filename": "hall.epub",
                      "chapter": 3, "chunk_index": 0, "format": "epub"}},
        {"id": "far.txt_0", "document": "Unrelated.", "distance": 0.95,
         "metadata": {"source": "/books/far.txt", "filename": "far.txt",
                      "chunk_index": 0, "format": "txt"}},
    ]

    @pytest.fixture
    def results(self, monkeypatch):
        monkeypatch.setattr("backend.retrieval.retriever.embed_texts", fake_embed)
        return retrieve_chunks("what is mind", FakeStore(self.HITS), k=3)

    def test_result_keys(self, results):
        assert sorted(results[0]) == [
            "chapter", "chunk_index", "filename", "metadata",
            "page", "rank", "score", "source", "text",
        ]

    def test_score_is_one_minus_distance(self, results):
        assert results[0]["score"] == pytest.approx(0.87)
        assert results[1]["score"] == pytest.approx(0.55)

    def test_below_threshold_is_filtered_out(self, results):
        """distance 0.95 -> score 0.05, under RELEVANCE_THRESHOLD of 0.3."""
        assert len(results) == 2
        assert all(r["filename"] != "far.txt" for r in results)

    def test_rank_is_one_based_and_ordered(self, results):
        assert [r["rank"] for r in results] == [1, 2]

    def test_source_is_a_path_and_filename_is_a_basename(self, results):
        """The divergence two consumers disagree about."""
        assert results[0]["source"] == "/books/kybalion.pdf"
        assert results[0]["filename"] == "kybalion.pdf"

    def test_missing_metadata_keys_become_none(self, results):
        assert results[0]["chapter"] is None
        assert results[1]["page"] is None
