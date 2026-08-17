"""
Document parsers for ingesting books in multiple formats.

Extracts text from PDF, EPUB and TXT while preserving the metadata needed for
citation (page numbers, chapter names, file info).

Architecture, per-format process notes and error handling:
docs/modules/ingestion/parsers.md
"""

from __future__ import annotations

import logging
from pathlib import Path

from backend.core.types import TextSegment

import pypdf
import ebooklib
from ebooklib import epub


logger = logging.getLogger(__name__)


# Alias onto the shared type; the original docstring now lives on TextSegment.
ParsedDocument = TextSegment


def parse_pdf(file_path: Path | str) -> list[ParsedDocument]:
    """
    Parse a PDF file and extract text with page metadata.

    Process and error handling: docs/modules/ingestion/parsers.md

    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of ParsedDocument tuples with text and metadata
        Empty list if file cannot be read
    """
    file_path = Path(file_path)
    documents = []
    
    try:
        # Open PDF file in binary mode (required for PDF reading)
        with open(file_path, "rb") as f:
            # Create a PDF reader object
            pdf_reader = pypdf.PdfReader(f)
            # Iterate through each page in the PDF
            for page_num, page in enumerate(pdf_reader.pages):
                # Extract text from the page
                text = page.extract_text()
                # Only include non-empty pages
                if text.strip():
                    # Create a ParsedDocument for this page with all metadata
                    documents.append(
                        ParsedDocument(
                            text=text,
                            metadata={
                                "source": str(file_path),      # Full path to file
                                "format": "pdf",               # Document format
                                "page": page_num + 1,          # Page number (1-indexed)
                                "total_pages": len(pdf_reader.pages),  # Total pages in PDF
                                "filename": file_path.name,    # Just the filename
                            },
                        )
                    )
        logger.info(f"✓ Parsed PDF: {file_path} ({len(documents)} pages)")
    except Exception as e:
        logger.error(f"✗ Error parsing PDF {file_path}: {e}")
    
    return documents


def parse_epub(file_path: Path | str) -> list[ParsedDocument]:
    """
    Parse an EPUB file and extract text with chapter metadata.

    Process, the HTML-to-text notes and error handling:
    docs/modules/ingestion/parsers.md

    Args:
        file_path: Path to the EPUB file
        
    Returns:
        List of ParsedDocument tuples with text and metadata
        Empty list if file cannot be read
    """
    file_path = Path(file_path)
    documents = []
    
    try:
        # Read the EPUB file
        book = epub.read_epub(str(file_path))
        chapter_num = 0
        
        # Iterate through all items in the book (chapters, sections, etc.)
        for item in book.get_items():
            # Only process document items (skip images, metadata, etc.)
            if item.get_type() == ebooklib.ITEM_DOCUMENT:
                try:
                    # Get the raw HTML content of this chapter
                    text = item.get_content().decode("utf-8", errors="ignore")
                    
                    # Remove HTML tags using regex
                    # This replaces all <tag> patterns with a space
                    import re
                    text = re.sub(r"<[^>]+>", " ", text)
                    
                    # Clean up extra whitespace - collapse multiple spaces into one
                    text = " ".join(text.split())
                    
                    # Only include non-empty chapters
                    if text.strip():
                        chapter_num += 1
                        documents.append(
                            ParsedDocument(
                                text=text,
                                metadata={
                                    "source": str(file_path),     # Full path to file
                                    "format": "epub",             # Document format
                                    "chapter": chapter_num,       # Chapter number (sequential)
                                    "chapter_title": item.get_name() or f"Chapter {chapter_num}",  # Chapter name
                                    "filename": file_path.name,   # Just the filename
                                },
                            )
                        )
                except Exception as e:
                    # Log and skip individual items that fail
                    logger.warning(f"Skipped EPUB item: {e}")
        
        logger.info(f"✓ Parsed EPUB: {file_path} ({chapter_num} chapters)")
    except Exception as e:
        logger.error(f"✗ Error parsing EPUB {file_path}: {e}")
    
    return documents


def parse_txt(file_path: Path | str) -> list[ParsedDocument]:
    """
    Parse a plain text file.

    Returns one document rather than many, unlike PDF and EPUB.
    Process and error handling: docs/modules/ingestion/parsers.md

    Args:
        file_path: Path to the text file
        
    Returns:
        List with single ParsedDocument (or empty list if file is empty/unreadable)
    """
    file_path = Path(file_path)
    
    try:
        # Open and read the entire text file
        # errors="ignore" means skip any characters that aren't valid UTF-8
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        
        # Only process if file has content
        if text.strip():
            document = ParsedDocument(
                text=text,
                metadata={
                    "source": str(file_path),   # Full path to file
                    "format": "txt",            # Document format
                    "filename": file_path.name, # Just the filename
                },
            )
            logger.info(f"✓ Parsed TXT: {file_path}")
            return [document]
        else:
            logger.warning(f"✗ Empty text file: {file_path}")
            return []
    except Exception as e:
        logger.error(f"✗ Error parsing TXT {file_path}: {e}")
        return []


def parse_document(file_path: Path | str) -> list[ParsedDocument]:
    """
    Parse a document of unknown type based on file extension.
    
    This is the main entry point for parsing. It:
    1. Checks the file extension
    2. Dispatches to the appropriate parser (PDF/EPUB/TXT)
    3. Returns the parsed documents
    
    This function provides a unified interface so callers don't need to
    know which parser to use - just call parse_document() and it figures it out.
    
    Supported formats:
    - .pdf → parse_pdf()
    - .epub → parse_epub()
    - .txt → parse_txt()
    
    Args:
        file_path: Path to the document file
        
    Returns:
        List of ParsedDocument tuples with text and metadata
        Empty list if format is unsupported or file cannot be read
    """
    file_path = Path(file_path)
    suffix = file_path.suffix.lower()
    
    # Check file extension and call appropriate parser
    if suffix == ".pdf":
        return parse_pdf(file_path)
    elif suffix == ".epub":
        return parse_epub(file_path)
    elif suffix == ".txt":
        return parse_txt(file_path)
    else:
        # Unknown format
        logger.error(f"✗ Unsupported file format: {suffix}")
        return []
