"""
The data shapes that travel between pipeline stages.

Three separate NamedTuples used to exist for what is one concept -- a piece of
text plus the metadata describing where it came from. ParsedDocument (parsers),
TextChunk (chunker) and Chunk (ingestion) were field-for-field identical, and the
ingestion pipeline mechanically converted one into another for no reason. They
are unified here as TextSegment, with the original modules keeping their names as
aliases so existing imports continue to work.

Chunk metadata is a TypedDict rather than a dataclass on purpose. It is still a
plain dict at runtime, which matters twice over: the vector store writes it
straight into Chroma, which requires real dicts of primitives, and every existing
`metadata["filename"]` or `.get("page")` access keeps working untouched. What
changes is that a type checker now knows which keys exist.
"""

from __future__ import annotations

from typing import NamedTuple, TypedDict


class ChunkMetadata(TypedDict, total=False):
    """
    Provenance for a piece of text, accumulated as it moves through the pipeline.

    total=False because the keys are format-dependent and stage-dependent: a PDF
    segment carries page/total_pages, an EPUB segment carries chapter/chapter_title,
    and a plain text file carries neither. The chunk_* keys are added later, by the
    chunker, so they are absent on freshly parsed segments.

    Keys:
        source: Full file path (for citation)
        format: Document format (pdf/epub/txt)
        filename: Just the filename
        page: Page number, 1-indexed (PDF only)
        total_pages: Total pages in the document (PDF only)
        chapter: Chapter number, sequential (EPUB only)
        chapter_title: Chapter name (EPUB only)
        chunk_index: Position in the chunk sequence
        total_chunks: Total chunks produced from this segment
        chunk_tokens: Actual token count for this chunk
    """

    source: str
    format: str
    filename: str
    page: int
    total_pages: int
    chapter: int
    chapter_title: str
    chunk_index: int
    total_chunks: int
    chunk_tokens: int


class TextSegment(NamedTuple):
    """
    A piece of text with the metadata describing where it came from.

    One type now covers what three did. The docstrings of all three are preserved
    below, because each described the same shape at a different pipeline stage and
    together they explain the whole journey.

    ParsedDocument (was backend/ingestion/parsers.py) -- a parsed document:

        Attributes:
            text: The extracted text content from the document (or a page/chapter of it)
            metadata: Dictionary containing source info (filename, page/chapter number,
                      format, etc.) This metadata is preserved through the entire
                      ingestion pipeline and allows us to cite exact sources when
                      generating answers

    TextChunk (was backend/ingestion/chunker.py) -- a chunked piece:

        Attributes:
            text: The chunk of text (roughly CHUNK_SIZE tokens)
            metadata: Dictionary containing:
                      - Original metadata from parsed doc (source, page, chapter, etc.)
                      - chunk_index: Which chunk this is (0, 1, 2, ...)
                      - total_chunks: Total number of chunks from this document
                      - chunk_tokens: Actual token count for this chunk

    Chunk (was backend/ingestion/__init__.py) -- the ingestion pipeline's output:

        This is the final output of the ingestion pipeline - ready for indexing
        (embedding and storing in vector database).

        Attributes:
            text: The chunk of text (~256 tokens, ready for embedding)
            metadata: Rich metadata dictionary containing:
                      - source: Full file path (for citation)
                      - format: Document format (pdf/epub/txt)
                      - filename: Just the filename
                      - page/chapter: Location in original document
                      - chunk_index: Position in chunk sequence
                      - total_chunks: Total chunks from this document
                      - chunk_tokens: Actual token count for this chunk

        The metadata is crucial for the generation phase because it allows
        us to cite exact sources: "As stated on page 42 of The Secret Teaching..."
    """

    text: str
    metadata: ChunkMetadata


__all__ = ["ChunkMetadata", "TextSegment"]
