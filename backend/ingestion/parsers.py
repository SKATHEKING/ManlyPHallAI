"""
Document parsers for ingesting books in multiple formats.

This module provides functions to extract text from different file formats
and preserve important metadata (page numbers, chapter names, file info).

Supported formats:
- PDF: Extract text page-by-page and track page numbers
- EPUB: Extract text chapter-by-chapter and track chapter structure
- TXT: Plain text with filename metadata

Architecture:
1. Each parser function (parse_pdf, parse_epub, parse_txt) reads a specific format
2. Returns a list of ParsedDocument objects containing text and metadata
3. The parse_document() function dispatches to the correct parser based on file extension
4. All parsers handle errors gracefully and log warnings/errors

Example usage:
    docs = parse_document("book.pdf")  # Returns list[ParsedDocument]
    for doc in docs:
        print(doc.text)        # The extracted text
        print(doc.metadata)    # Source file, page number, etc.
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
    
    Process:
    1. Opens the PDF file using pypdf
    2. Iterates through each page
    3. Extracts text from each page (skips empty pages)
    4. Creates ParsedDocument for each page with metadata:
       - Source file path
       - Format ("pdf")
       - Page number (1-indexed)
       - Total pages
       - Filename
    
    Error handling:
    - If PDF is corrupted or unreadable, logs an error and returns empty list
    - If a page fails to extract text, it's silently skipped
    
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
    
    Process:
    1. Opens EPUB file using ebooklib
    2. Iterates through all items (chapters/sections) in the book
    3. Extracts text from HTML content
    4. Removes HTML tags and cleans whitespace
    5. Creates ParsedDocument for each chapter with metadata:
       - Source file path
       - Format ("epub")
       - Chapter number
       - Chapter title
       - Filename
    
    Note: EPUB files store content as HTML, so we need to:
    - Decode UTF-8 bytes to string
    - Remove HTML tags to get plain text
    - Clean up extra whitespace
    
    Error handling:
    - Skips items that fail to parse (logs warning)
    - Returns what could be parsed even if some items fail
    
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
    
    Process:
    1. Opens text file with UTF-8 encoding
    2. Reads entire content
    3. Returns single ParsedDocument with filename metadata
    
    Note: Unlike PDF/EPUB which return multiple documents (one per page/chapter),
    TXT files are returned as a single document. This is fine because the chunking
    step (Phase 1b) will split it into smaller pieces.
    
    Error handling:
    - Uses "ignore" error handling for encoding issues (skips bad characters)
    - Skips empty files
    - Returns empty list if file cannot be read
    
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
