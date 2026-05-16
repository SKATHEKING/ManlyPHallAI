# Phase 1 Implementation Guide

## Overview

This guide provides detailed, step-by-step instructions for implementing the Book-Based Knowledge Engine (Phase 1) of the Manly P. Hall AI Bot. Follow each task in sequence; they are ordered to maximize learning and minimize debugging.

**Expected Timeline**: 8–12 days of focused development (2–3 hours per day).

**Prerequisites**:
- Python 3.10+ installed (verify: `python --version`)
- Git initialized in project (verify: `git log`)
- Familiarity with Python virtual environments and pip
- ~10GB free disk space (for models and data)
- Optional but recommended: GPU (NVIDIA with CUDA) for faster inference

---

## Table of Contents

1. [Phase 1a: Foundations](#phase-1a-foundations)
2. [Phase 1b: Ingestion Pipeline](#phase-1b-ingestion-pipeline)
3. [Phase 1c: Indexing and Vector Storage](#phase-1c-indexing-and-vector-storage)
4. [Phase 1d: Retrieval and Generation](#phase-1d-retrieval-and-generation)
5. [Phase 1e: API and Server](#phase-1e-api-and-server)
6. [Phase 1f: Integration and Testing](#phase-1f-integration-and-testing)
7. [Verification Checklist](#verification-checklist)
8. [Troubleshooting](#troubleshooting)

---

## Phase 1a: Foundations (1–2 days)

**Objective**: Set up the project structure, install dependencies, configure settings, and download models.

### Task 1a.1: Create Project Structure

**File**: N/A (manual setup)

Create the following directories:

```bash
mkdir -p backend/{ingestion,indexing,retrieval,generation,api}
mkdir -p frontend/{web,cli}
mkdir -p data/{books,chroma_db,models}
mkdir -p tests
mkdir -p scripts
mkdir -p docs
```

After completion, verify structure:
```bash
ls -la backend/
ls -la data/
```

Expected output:
```
backend/:
ingestion/  indexing/  retrieval/  generation/  api/  __init__.py  main.py  config.py

data/:
books/  chroma_db/  models/  ingestion_log.json
```

---

### Task 1a.2: Create `backend/__init__.py` and `config.py`

**File**: `backend/__init__.py`

Create an empty file to mark `backend/` as a Python package:

```bash
touch backend/__init__.py
```

**File**: `backend/config.py`

Create the configuration module:

```python
"""
Configuration for Manly P. Hall AI Bot.
Centralized settings for ingestion, indexing, retrieval, and generation.
"""

import os
from pathlib import Path

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
RELEVANCE_THRESHOLD = 0.5  # Minimum similarity score (0.0-1.0)

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
# Logging
# ============================================================================
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ============================================================================
# Development
# ============================================================================
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
```

**Verification**:
```bash
python -c "from backend.config import *; print(f'Data dir: {DATA_DIR}'); print(f'Embedding model: {EMBEDDING_MODEL}')"
```

Expected output:
```
Data dir: /path/to/ManlyPHallAI/data
Embedding model: all-MiniLM-L6-v2
```

---

### Task 1a.3: Create `requirements.txt`

**File**: `requirements.txt`

```
# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0

# Document Parsing
pypdf==3.17.1
ebooklib==0.18.0
python-docx==0.8.11

# Text Processing
langchain==0.1.0
sentence-transformers==2.2.2
tokenizers==0.14.1

# Vector Database
chromadb==0.4.18

# LLM Integration
ollama==0.1.0
requests==2.31.0

# Data Processing
numpy==1.24.3
pandas==2.1.3

# Development & Testing
pytest==7.4.3
python-dotenv==1.0.0

# Utilities
click==8.1.7
typer==0.9.0
```

**Verification**:
```bash
wc -l requirements.txt
# Should show ~25 lines
```

---

### Task 1a.4: Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Or on Windows: venv\Scripts\activate

# Verify activation
which python
# Should show: /path/to/ManlyPHallAI/venv/bin/python
```

---

### Task 1a.5: Install Dependencies

```bash
pip install --upgrade pip setuptools wheel

pip install -r requirements.txt
```

**Expected Time**: 3–5 minutes

**Verification**:
```bash
python -c "import fastapi; import chromadb; import sentence_transformers; print('All dependencies installed!')"
```

---

### Task 1a.6: Download Embeddings Model

The sentence-transformers model is downloaded automatically on first use, but we can pre-download it:

**File**: `scripts/download_embeddings_model.py`

```python
"""
Download and cache the sentence-transformers embedding model.
Run this once to avoid long delays on first ingestion.
"""

from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL, MODELS_DIR
import os

# Set cache directory
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODELS_DIR)

print(f"Downloading model: {EMBEDDING_MODEL}")
print(f"Cache directory: {MODELS_DIR}")

model = SentenceTransformer(EMBEDDING_MODEL)

print(f"✓ Model downloaded successfully!")
print(f"✓ Model dimension: {model.get_sentence_embedding_dimension()}")
```

**Run it**:
```bash
python scripts/download_embeddings_model.py
```

**Expected Time**: 2–3 minutes (first download); subsequent runs cache the model locally.

**Verification**:
```bash
ls -lh data/models/
# Should show model files (total ~22MB)
```

---

### Task 1a.7: Download Ollama and Start Llama Model

Ollama is a tool for running open-source LLMs locally.

**Install Ollama** (macOS):
```bash
# Via Homebrew
brew install ollama

# Or download from https://ollama.ai/download
```

**Verify Installation**:
```bash
ollama --version
```

**Download Llama 2 Model**:
```bash
ollama pull llama2:7b
```

**Expected Time**: 5–10 minutes (first pull; ~4GB download)

**Start Ollama Server** (run in a separate terminal):
```bash
ollama serve
```

You should see:
```
Starting Ollama server...
Listening on 127.0.0.1:11434
```

**Verification** (in another terminal):
```bash
curl http://localhost:11434/api/version
```

Expected response:
```json
{"version":"0.1.0"}
```

---

### Task 1a.8: Create `backend/main.py` (Placeholder)

**File**: `backend/main.py`

Create a simple FastAPI app that will be expanded in Phase 1e:

```python
"""
Main FastAPI application for Manly P. Hall AI Bot.
Phase 1: Book-based question answering.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from backend.config import API_HOST, API_PORT, LOG_LEVEL
import logging

# ============================================================================
# Logging
# ============================================================================
logging.basicConfig(level=getattr(logging, LOG_LEVEL))
logger = logging.getLogger(__name__)

# ============================================================================
# FastAPI App
# ============================================================================
app = FastAPI(
    title="Manly P. Hall AI Bot",
    description="A specialized AI assistant for esoteric knowledge",
    version="0.1.0",
)

# ============================================================================
# Health Check Endpoint
# ============================================================================
@app.get("/health")
def health_check():
    """
    Health check endpoint. Returns 200 if system is ready.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "ready", "message": "Manly P. Hall AI Bot is running"}
    )

# ============================================================================
# Main Entry Point
# ============================================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )
```

**Test it**:
```bash
python backend/main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

Visit `http://localhost:8000/health` in your browser or via curl:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"ready","message":"Manly P. Hall AI Bot is running"}
```

---

### Task 1a.9: Initialize Git and Create `.gitignore`

**File**: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
ENV/
env/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Project-specific
data/books/
data/models/
data/chroma_db/
logs/
*.log

# Environment variables
.env
.env.local

# macOS
.DS_Store
.AppleDouble
.LSOverride

# OS
Thumbs.db
```

**Commit initialization**:
```bash
git add -A
git commit -m "Phase 1a: Initialize project structure, config, and dependencies"
```

---

## Phase 1b: Ingestion Pipeline (2–3 days)

**Objective**: Build the data ingestion pipeline to parse books and prepare chunks.

### Task 1b.1: Create `backend/ingestion/__init__.py` and `parsers.py`

**File**: `backend/ingestion/__init__.py`

```python
"""
Ingestion module for parsing and extracting text from book files.
"""
```

**File**: `backend/ingestion/parsers.py`

```python
"""
Text parsers for PDF, EPUB, and plain text files.
Each parser extracts text and preserves structure metadata.
"""

import logging
from pathlib import Path
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
import PyPDF2
import ebooklib
from ebooklib import epub

logger = logging.getLogger(__name__)


@dataclass
class ParsedText:
    """Represents text extracted from a book file."""
    content: str                       # Full extracted text
    chapters: List[Dict[str, str]]    # List of chapters with text and metadata
    metadata: Dict[str, str]          # File-level metadata (title, author, etc.)


class PDFParser:
    """Parses text from PDF files."""
    
    @staticmethod
    def parse(file_path: Path) -> ParsedText:
        """
        Extract text from a PDF file, preserving chapter structure if available.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            ParsedText with full text and chapter-level breakdowns
            
        Raises:
            Exception: If PDF cannot be read
        """
        logger.info(f"Parsing PDF: {file_path}")
        
        try:
            with open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                num_pages = len(pdf_reader.pages)
                logger.info(f"  PDF has {num_pages} pages")
                
                # Extract text from all pages
                full_text = ""
                pages_text = []
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    full_text += f"\n--- Page {page_num + 1} ---\n" + text
                    pages_text.append(text)
                
                # Try to extract metadata
                metadata = {
                    "file_name": file_path.name,
                    "file_size_bytes": file_path.stat().st_size,
                    "num_pages": num_pages,
                }
                
                # Extract title from PDF metadata if available
                if pdf_reader.metadata:
                    if pdf_reader.metadata.title:
                        metadata["title"] = str(pdf_reader.metadata.title)
                    if pdf_reader.metadata.author:
                        metadata["author"] = str(pdf_reader.metadata.author)
                
                # For now, treat entire PDF as one chapter
                # (Future: implement chapter detection from PDF outline)
                chapters = [
                    {
                        "chapter_name": "Full Text",
                        "text": full_text,
                        "page_start": 1,
                        "page_end": num_pages,
                    }
                ]
                
                logger.info(f"  ✓ Extracted {len(full_text)} characters")
                
                return ParsedText(
                    content=full_text,
                    chapters=chapters,
                    metadata=metadata,
                )
        
        except Exception as e:
            logger.error(f"Error parsing PDF {file_path}: {e}")
            raise


class EPUBParser:
    """Parses text from EPUB files."""
    
    @staticmethod
    def parse(file_path: Path) -> ParsedText:
        """
        Extract text from an EPUB file, preserving chapter structure.
        
        Args:
            file_path: Path to the EPUB file
            
        Returns:
            ParsedText with full text and chapter-level breakdowns
            
        Raises:
            Exception: If EPUB cannot be read
        """
        logger.info(f"Parsing EPUB: {file_path}")
        
        try:
            book = epub.read_epub(file_path)
            
            # Extract metadata
            metadata = {
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
            }
            
            if book.get_metadata("DC", "title"):
                metadata["title"] = str(book.get_metadata("DC", "title")[0])
            if book.get_metadata("DC", "creator"):
                metadata["author"] = str(book.get_metadata("DC", "creator")[0])
            
            # Extract chapters
            chapters = []
            full_text = ""
            
            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    content = item.get_content()
                    # Simple HTML to text conversion (strip tags)
                    text = EPUBParser._extract_text_from_html(content)
                    
                    if text.strip():
                        chapter_name = item.get_name() or f"Chapter {len(chapters) + 1}"
                        chapters.append({
                            "chapter_name": chapter_name,
                            "text": text,
                            "item_id": item.get_id(),
                        })
                        full_text += f"\n--- {chapter_name} ---\n{text}"
            
            logger.info(f"  ✓ Extracted {len(chapters)} chapters, {len(full_text)} characters")
            
            return ParsedText(
                content=full_text,
                chapters=chapters,
                metadata=metadata,
            )
        
        except Exception as e:
            logger.error(f"Error parsing EPUB {file_path}: {e}")
            raise
    
    @staticmethod
    def _extract_text_from_html(html_bytes: bytes) -> str:
        """
        Simple HTML to text conversion.
        Production version would use a proper HTML parser.
        """
        try:
            from html.parser import HTMLParser
            
            class MLStripper(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.reset()
                    self.fed = []
                
                def handle_data(self, d):
                    self.fed.append(d)
                
                def get_data(self):
                    return ''.join(self.fed)
            
            stripper = MLStripper()
            stripper.feed(html_bytes.decode('utf-8', errors='ignore'))
            return stripper.get_data()
        except Exception as e:
            logger.warning(f"Error extracting HTML text: {e}")
            return html_bytes.decode('utf-8', errors='ignore')


class TextFileParser:
    """Parses plain text files."""
    
    @staticmethod
    def parse(file_path: Path) -> ParsedText:
        """
        Read a plain text file.
        
        Args:
            file_path: Path to the text file
            
        Returns:
            ParsedText with full text
            
        Raises:
            Exception: If file cannot be read
        """
        logger.info(f"Parsing text file: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            metadata = {
                "file_name": file_path.name,
                "file_size_bytes": file_path.stat().st_size,
            }
            
            # Assume single chapter for text files
            chapters = [
                {
                    "chapter_name": "Full Text",
                    "text": content,
                }
            ]
            
            logger.info(f"  ✓ Extracted {len(content)} characters")
            
            return ParsedText(
                content=content,
                chapters=chapters,
                metadata=metadata,
            )
        
        except Exception as e:
            logger.error(f"Error parsing text file {file_path}: {e}")
            raise


class ParserFactory:
    """Factory for selecting the appropriate parser based on file type."""
    
    PARSERS = {
        ".pdf": PDFParser,
        ".epub": EPUBParser,
        ".txt": TextFileParser,
    }
    
    @staticmethod
    def get_parser(file_path: Path):
        """Get the appropriate parser for the file type."""
        suffix = file_path.suffix.lower()
        
        if suffix not in ParserFactory.PARSERS:
            raise ValueError(f"Unsupported file format: {suffix}")
        
        return ParserFactory.PARSERS[suffix]
    
    @staticmethod
    def parse(file_path: Path) -> ParsedText:
        """Parse a file using the appropriate parser."""
        parser = ParserFactory.get_parser(file_path)
        return parser.parse(file_path)
```

**Verification**:
```bash
python -c "from backend.ingestion.parsers import ParserFactory; print('Parsers imported successfully')"
```

---

### Task 1b.2: Create `backend/ingestion/cleaner.py`

**File**: `backend/ingestion/cleaner.py`

```python
"""
Text cleaning and normalization utilities.
Prepares parsed text for chunking and embedding.
"""

import re
import logging

logger = logging.getLogger(__name__)


class TextCleaner:
    """Cleans and normalizes text for processing."""
    
    @staticmethod
    def clean(text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        logger.debug("Cleaning text...")
        
        # Remove form feeds, vertical tabs, etc.
        text = re.sub(r'[\x0c\x0b]', '', text)
        
        # Normalize line breaks: multiple newlines → double newline (paragraph break)
        text = re.sub(r'\n\n\n+', '\n\n', text)
        
        # Remove lines that are just page numbers or headers
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            # Skip lines that are just numbers (page numbers)
            if re.match(r'^\s*\d+\s*$', line):
                continue
            # Skip lines that look like headers/footers
            if len(line.strip()) < 3 or line.strip().startswith('---'):
                if len(line.strip()) > 0 and not line.strip().startswith('---'):
                    cleaned_lines.append(line)
                elif line.strip().startswith('---'):
                    cleaned_lines.append('\n')
            else:
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        
        # Normalize whitespace within lines
        text = re.sub(r' +', ' ', text)  # Multiple spaces → single space
        
        # Normalize quotes
        text = re.sub(r'[""''‟‛„]', '"', text)  # All quote variants → straight double
        
        # Remove trailing whitespace from lines
        lines = text.split('\n')
        text = '\n'.join(line.rstrip() for line in lines)
        
        # Remove leading/trailing whitespace from entire text
        text = text.strip()
        
        logger.debug(f"  Text cleaned: {len(text)} characters")
        
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize all types of whitespace."""
        # Replace tabs with spaces
        text = text.replace('\t', '  ')
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        return text
```

**Verification**:
```bash
python -c "from backend.ingestion.cleaner import TextCleaner; text = 'Hello  \\n\\n\\nworld'; print(repr(TextCleaner.clean(text)))"
```

---

### Task 1b.3: Create `backend/ingestion/chunker.py`

**File**: `backend/ingestion/chunker.py`

```python
"""
Text chunking utilities for semantic splitting with overlap.
Uses LangChain's RecursiveCharacterTextSplitter under the hood.
"""

import logging
from typing import List, Dict
from dataclasses import dataclass
from langchain.text_splitter import RecursiveCharacterTextSplitter
from backend.config import CHUNK_SIZE, CHUNK_OVERLAP, CHUNK_SEPARATOR

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    """Represents a single text chunk ready for embedding."""
    id: str                      # Unique identifier (e.g., "book-ch5-001")
    content: str                 # Text content
    source_title: str            # Book title
    source_author: str           # Book author
    chapter: str                 # Chapter name
    page_range: str              # Pages in original book (if applicable)
    tokens: int                  # Approximate token count
    position_in_chapter: int     # Ordinal position within chapter
    file_hash: str              # Hash of source file


class TextChunker:
    """Splits text into semantic chunks with overlap."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, chunk_overlap: int = CHUNK_OVERLAP):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target number of tokens per chunk
            chunk_overlap: Percentage overlap (0-100)
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Convert token count to character count (rough approximation: 1 token ≈ 4 characters)
        char_chunk_size = chunk_size * 4
        char_overlap = int(chunk_overlap / 100 * char_chunk_size)
        
        # Initialize LangChain splitter with recursive separators
        self.splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=char_chunk_size,
            chunk_overlap=char_overlap,
            length_function=len,
        )
        
        logger.info(f"Chunker initialized: size={chunk_size} tokens, overlap={chunk_overlap}%")
    
    def chunk(
        self,
        text: str,
        source_title: str,
        source_author: str,
        chapter_name: str,
        page_range: str = "",
        file_hash: str = "",
    ) -> List[Chunk]:
        """
        Split text into chunks.
        
        Args:
            text: Text to split
            source_title: Title of the source book
            source_author: Author of the source book
            chapter_name: Name of the chapter
            page_range: Page range (optional)
            file_hash: Hash of source file (optional)
            
        Returns:
            List of Chunk objects
        """
        logger.debug(f"Chunking chapter: {chapter_name} ({len(text)} chars)")
        
        # Split text
        chunk_texts = self.splitter.split_text(text)
        
        chunks = []
        for i, chunk_text in enumerate(chunk_texts):
            # Estimate token count (1 token ≈ 4 characters)
            estimated_tokens = len(chunk_text) // 4
            
            chunk_id = f"{source_title.lower().replace(' ', '-')}-{chapter_name.lower().replace(' ', '-')}-{i:03d}"
            
            chunk = Chunk(
                id=chunk_id,
                content=chunk_text,
                source_title=source_title,
                source_author=source_author,
                chapter=chapter_name,
                page_range=page_range,
                tokens=estimated_tokens,
                position_in_chapter=i,
                file_hash=file_hash,
            )
            
            chunks.append(chunk)
        
        logger.debug(f"  ✓ Created {len(chunks)} chunks (avg {len(text) // max(1, len(chunks))} chars/chunk)")
        
        return chunks


def estimate_token_count(text: str) -> int:
    """
    Rough estimate of token count (1 token ≈ 4 characters).
    For accurate counting, use a tokenizer, but this is sufficient for our purposes.
    """
    return len(text) // 4
```

**Verification**:
```bash
python -c "from backend.ingestion.chunker import TextChunker; chunker = TextChunker(); chunks = chunker.chunk('Hello world. This is a test.', 'Test Book', 'Author', 'Chapter 1'); print(f'Chunks created: {len(chunks)}')"
```

---

### Task 1b.4: Test the Ingestion Pipeline

Create a test script to verify parsers and chunker work:

**File**: `scripts/test_ingestion.py`

```python
"""
Test the ingestion pipeline with a sample text file.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion.parsers import ParserFactory
from backend.ingestion.cleaner import TextCleaner
from backend.ingestion.chunker import TextChunker
import hashlib

# Create a sample book file
sample_text = """
Chapter 1: Introduction

This is a test chapter about Freemasonry. Freemasonry is a system of morality and philosophy.

Chapter 2: History

The history of Freemasonry dates back centuries. Many notable figures were members.

Chapter 3: Symbolism

Freemasonry uses many symbols in its rituals and teachings. Each symbol has deep meaning.
"""

sample_file = Path("data/books/test_sample.txt")
sample_file.parent.mkdir(parents=True, exist_ok=True)

with open(sample_file, "w") as f:
    f.write(sample_text)

print("✓ Created sample file:", sample_file)

# Test parsing
print("\n--- Testing Parser ---")
parsed = ParserFactory.parse(sample_file)
print(f"Parsed content length: {len(parsed.content)} characters")
print(f"Number of chapters: {len(parsed.chapters)}")
print(f"Metadata: {parsed.metadata}")

# Test cleaning
print("\n--- Testing Cleaner ---")
cleaned = TextCleaner.clean(parsed.content)
print(f"Cleaned content length: {len(cleaned)} characters")
print(f"Sample: {cleaned[:100]}...")

# Test chunking
print("\n--- Testing Chunker ---")
file_hash = hashlib.md5(sample_file.read_bytes()).hexdigest()
chunker = TextChunker()
chunks = chunker.chunk(
    cleaned,
    source_title="Test Book",
    source_author="Test Author",
    chapter_name="Full Text",
    file_hash=file_hash,
)

print(f"Number of chunks: {len(chunks)}")
for i, chunk in enumerate(chunks[:2]):
    print(f"\nChunk {i+1}:")
    print(f"  ID: {chunk.id}")
    print(f"  Tokens: {chunk.tokens}")
    print(f"  Content preview: {chunk.content[:80]}...")

print("\n✓ Ingestion pipeline test completed!")
```

**Run it**:
```bash
python scripts/test_ingestion.py
```

Expected output:
```
✓ Created sample file: data/books/test_sample.txt

--- Testing Parser ---
Parsed content length: 456 characters
Number of chapters: 1
Metadata: {'file_name': 'test_sample.txt', 'file_size_bytes': 456}

--- Testing Chunker ---
Number of chunks: 3
...
✓ Ingestion pipeline test completed!
```

---

### Task 1b.5: Commit Ingestion Pipeline

```bash
git add backend/ingestion/ scripts/test_ingestion.py
git commit -m "Phase 1b: Implement ingestion pipeline (parsers, cleaner, chunker)"
```

---

## Phase 1c: Indexing and Vector Storage (1–2 days)

**Objective**: Build the vector indexing layer using Chroma and sentence-transformers.

### Task 1c.1: Create `backend/indexing/__init__.py` and `embedder.py`

**File**: `backend/indexing/__init__.py`

```python
"""
Indexing module for embedding and storing vectors.
"""
```

**File**: `backend/indexing/embedder.py`

```python
"""
Embedding generation using sentence-transformers.
Converts text chunks to dense vector representations.
"""

import logging
import numpy as np
from typing import List
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL, EMBEDDING_BATCH_SIZE, MODELS_DIR
import os

logger = logging.getLogger(__name__)

# Set model cache directory
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(MODELS_DIR)


class TextEmbedder:
    """Generates embeddings using sentence-transformers."""
    
    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize embedder with a sentence-transformers model.
        
        Args:
            model_name: Name of the model (e.g., 'all-MiniLM-L6-v2')
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.model_name = model_name
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        logger.info(f"  ✓ Model loaded. Embedding dimension: {self.embedding_dimension}")
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Embed a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        logger.debug(f"Embedding {len(texts)} texts...")
        
        if not texts:
            return []
        
        # Use batch processing for efficiency
        embeddings = self.model.encode(
            texts,
            batch_size=EMBEDDING_BATCH_SIZE,
            show_progress_bar=len(texts) > 10,
            convert_to_numpy=False,
        )
        
        # Convert to list of lists
        embeddings_list = [embedding.tolist() for embedding in embeddings]
        
        logger.debug(f"  ✓ Embedded {len(embeddings_list)} texts")
        
        return embeddings_list
    
    def embed_single(self, text: str) -> List[float]:
        """
        Embed a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        embeddings = self.embed([text])
        return embeddings[0] if embeddings else []
```

---

### Task 1c.2: Create `backend/indexing/store.py`

**File**: `backend/indexing/store.py`

```python
"""
Vector store management using Chroma.
Handles vector insertion, retrieval, and persistence.
"""

import logging
import json
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import asdict
import chromadb
from backend.config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    RETRIEVAL_K,
    RELEVANCE_THRESHOLD,
)
from backend.ingestion.chunker import Chunk

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector storage using Chroma."""
    
    def __init__(self):
        """Initialize the vector store."""
        logger.info(f"Initializing vector store at {CHROMA_PERSIST_DIR}")
        
        # Initialize Chroma client with persistence
        self.client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},  # Use cosine similarity
        )
        
        logger.info(f"  ✓ Vector store initialized. Collection: {CHROMA_COLLECTION_NAME}")
        logger.info(f"  ✓ Current collection size: {self.collection.count()} vectors")
    
    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """
        Add chunks and their embeddings to the vector store.
        
        Args:
            chunks: List of Chunk objects
            embeddings: List of embedding vectors
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Number of chunks and embeddings must match")
        
        logger.info(f"Adding {len(chunks)} chunks to vector store...")
        
        # Prepare data for Chroma
        ids = [chunk.id for chunk in chunks]
        metadatas = []
        documents = []
        
        for chunk in chunks:
            metadatas.append({
                "source_title": chunk.source_title,
                "source_author": chunk.source_author,
                "chapter": chunk.chapter,
                "page_range": chunk.page_range,
                "position": str(chunk.position_in_chapter),
                "tokens": str(chunk.tokens),
                "file_hash": chunk.file_hash,
            })
            documents.append(chunk.content)
        
        # Add to collection
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            metadatas=metadatas,
            documents=documents,
        )
        
        logger.info(f"  ✓ Added {len(chunks)} chunks. Collection size: {self.collection.count()}")
    
    def search(
        self,
        query_embedding: List[float],
        top_k: int = RETRIEVAL_K,
        threshold: float = RELEVANCE_THRESHOLD,
    ) -> List[Dict]:
        """
        Search for similar chunks using vector similarity.
        
        Args:
            query_embedding: Query embedding vector
            top_k: Number of results to return
            threshold: Minimum similarity score (0.0-1.0)
            
        Returns:
            List of search results with metadata and similarity scores
        """
        logger.debug(f"Searching for {top_k} similar chunks...")
        
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
        )
        
        # Process results
        search_results = []
        
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, chunk_id in enumerate(results["ids"][0]):
                # Chroma returns distances; convert to similarity scores
                # For cosine distance, similarity = 1 - distance
                distance = results["distances"][0][i]
                similarity = 1 - distance  # Convert distance to similarity
                
                # Filter by threshold
                if similarity < threshold:
                    logger.debug(f"  Filtering out result with similarity {similarity:.3f} < {threshold}")
                    continue
                
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i]
                
                search_results.append({
                    "chunk_id": chunk_id,
                    "content": document,
                    "source_title": metadata.get("source_title", ""),
                    "source_author": metadata.get("source_author", ""),
                    "chapter": metadata.get("chapter", ""),
                    "page_range": metadata.get("page_range", ""),
                    "similarity_score": float(similarity),
                    "position": int(metadata.get("position", 0)),
                })
        
        logger.debug(f"  ✓ Found {len(search_results)} results above threshold {threshold}")
        
        return search_results
    
    def get_collection_info(self) -> Dict:
        """Get information about the current collection."""
        return {
            "collection_name": self.collection.name,
            "total_vectors": self.collection.count(),
            "persist_directory": CHROMA_PERSIST_DIR,
        }
```

---

### Task 1c.3: Create `scripts/ingest_book.py`

This script integrates the pipeline to ingest a complete book:

**File**: `scripts/ingest_book.py`

```python
"""
End-to-end book ingestion script.
Parses, cleans, chunks, embeds, and stores a book.
"""

import sys
import argparse
import hashlib
from pathlib import Path
from datetime import datetime
import json
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion.parsers import ParserFactory
from backend.ingestion.cleaner import TextCleaner
from backend.ingestion.chunker import TextChunker
from backend.indexing.embedder import TextEmbedder
from backend.indexing.store import VectorStore

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def ingest_book(
    file_path: str,
    title: Optional[str] = None,
    author: Optional[str] = None,
) -> None:
    """
    Ingest a book file: parse → clean → chunk → embed → store.
    
    Args:
        file_path: Path to book file (PDF, EPUB, or TXT)
        title: Book title (optional; extracted from file if not provided)
        author: Book author (optional)
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        return
    
    # Compute file hash for version tracking
    file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()
    logger.info(f"File hash: {file_hash}")
    
    # =========================================================================
    # 1. PARSE
    # =========================================================================
    logger.info("=" * 60)
    logger.info("STEP 1: PARSING")
    logger.info("=" * 60)
    
    parsed = ParserFactory.parse(file_path)
    
    if not title:
        title = parsed.metadata.get("title", file_path.stem)
    if not author:
        author = parsed.metadata.get("author", "Unknown")
    
    logger.info(f"Title: {title}")
    logger.info(f"Author: {author}")
    logger.info(f"Extracted {len(parsed.content)} characters")
    
    # =========================================================================
    # 2. CLEAN
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 2: CLEANING")
    logger.info("=" * 60)
    
    cleaned_text = TextCleaner.clean(parsed.content)
    logger.info(f"Cleaned text: {len(cleaned_text)} characters")
    
    # =========================================================================
    # 3. CHUNK
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 3: CHUNKING")
    logger.info("=" * 60)
    
    chunker = TextChunker()
    all_chunks = []
    
    for chapter in parsed.chapters:
        chapter_text = chapter.get("text", "")
        chapter_name = chapter.get("chapter_name", "Full Text")
        
        chunks = chunker.chunk(
            text=chapter_text,
            source_title=title,
            source_author=author,
            chapter_name=chapter_name,
            page_range=chapter.get("page_start", 0),  # Simplified
            file_hash=file_hash,
        )
        
        all_chunks.extend(chunks)
        logger.info(f"  Chapter '{chapter_name}': {len(chunks)} chunks")
    
    logger.info(f"Total chunks: {len(all_chunks)}")
    logger.info(f"Total tokens (approx): {sum(c.tokens for c in all_chunks)}")
    
    # =========================================================================
    # 4. EMBED
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 4: EMBEDDING")
    logger.info("=" * 60)
    
    embedder = TextEmbedder()
    chunk_texts = [chunk.content for chunk in all_chunks]
    embeddings = embedder.embed(chunk_texts)
    logger.info(f"Generated {len(embeddings)} embeddings")
    
    # =========================================================================
    # 5. STORE
    # =========================================================================
    logger.info("\n" + "=" * 60)
    logger.info("STEP 5: STORING IN VECTOR DATABASE")
    logger.info("=" * 60)
    
    vector_store = VectorStore()
    vector_store.add_chunks(all_chunks, embeddings)
    
    collection_info = vector_store.get_collection_info()
    logger.info(f"Collection info: {collection_info}")
    
    # =========================================================================
    # Log to metadata file
    # =========================================================================
    metadata_file = Path("data/ingestion_log.json")
    metadata_log = []
    
    if metadata_file.exists():
        with open(metadata_file, "r") as f:
            metadata_log = json.load(f)
    
    metadata_log.append({
        "title": title,
        "author": author,
        "file_path": str(file_path),
        "file_hash": file_hash,
        "format": file_path.suffix.lower(),
        "ingestion_date": datetime.now().isoformat(),
        "chunk_count": len(all_chunks),
        "total_tokens": sum(c.tokens for c in all_chunks),
        "status": "ready",
    })
    
    with open(metadata_file, "w") as f:
        json.dump(metadata_log, f, indent=2)
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ INGESTION COMPLETE")
    logger.info("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest a book into the vector database")
    parser.add_argument("file_path", help="Path to book file (PDF, EPUB, or TXT)")
    parser.add_argument("--title", help="Book title (optional)")
    parser.add_argument("--author", help="Book author (optional)")
    
    args = parser.parse_args()
    
    ingest_book(args.file_path, args.title, args.author)
```

Add missing import:
```bash
# At the top of the file, add:
from typing import Optional
```

---

### Task 1c.4: Test Indexing with Sample Book

```bash
# Test with the sample text file from Phase 1b
python scripts/ingest_book.py data/books/test_sample.txt --title "Test Book" --author "Test Author"
```

Expected output:
```
============================================================
STEP 1: PARSING
============================================================
Title: Test Book
Author: Test Author
Extracted 456 characters
...
============================================================
✓ INGESTION COMPLETE
============================================================
```

Verify Chroma database was created:
```bash
ls -la data/chroma_db/
# Should show files like: index, data, metadata
```

---

### Task 1c.5: Commit Indexing Layer

```bash
git add backend/indexing/ scripts/ingest_book.py
git commit -m "Phase 1c: Implement indexing with embeddings and vector store"
```

---

## Phase 1d: Retrieval and Generation (2–3 days)

**Objective**: Build the retrieval and answer generation layers.

### Task 1d.1: Create `backend/retrieval/retriever.py`

**File**: `backend/retrieval/__init__.py`

```python
"""
Retrieval module for searching and ranking relevant passages.
"""
```

**File**: `backend/retrieval/retriever.py`

```python
"""
Query-based retrieval of relevant book passages.
"""

import logging
from typing import List, Dict
from backend.indexing.embedder import TextEmbedder
from backend.indexing.store import VectorStore
from backend.config import RETRIEVAL_K, RELEVANCE_THRESHOLD

logger = logging.getLogger(__name__)


class Retriever:
    """Retrieves relevant passages for a query."""
    
    def __init__(self):
        """Initialize retriever with embedder and vector store."""
        self.embedder = TextEmbedder()
        self.vector_store = VectorStore()
    
    def retrieve(
        self,
        query: str,
        top_k: int = RETRIEVAL_K,
        threshold: float = RELEVANCE_THRESHOLD,
    ) -> List[Dict]:
        """
        Retrieve relevant passages for a query.
        
        Args:
            query: User's question
            top_k: Number of passages to retrieve
            threshold: Minimum similarity score
            
        Returns:
            List of relevant passages with metadata
        """
        logger.info(f"Retrieving passages for query: '{query}'")
        
        # Embed the query
        query_embedding = self.embedder.embed_single(query)
        
        # Search vector store
        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            threshold=threshold,
        )
        
        logger.info(f"  ✓ Retrieved {len(results)} passages")
        
        return results
```

---

### Task 1d.2: Create `backend/generation/__init__.py` and `prompts.py`

**File**: `backend/generation/__init__.py`

```python
"""
Generation module for LLM-based answer generation.
"""
```

**File**: `backend/generation/prompts.py`

```python
"""
Prompt templates for grounded answer generation.
Ensures LLM only uses provided passages as sources.
"""

import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class PromptBuilder:
    """Builds prompts for grounded answer generation."""
    
    @staticmethod
    def build_grounded_prompt(
        query: str,
        passages: List[Dict],
        max_passages: int = 5,
    ) -> str:
        """
        Build a prompt that grounds the LLM in provided passages.
        
        Args:
            query: User's question
            passages: List of retrieved passages (each with 'content', 'source_title', 'chapter')
            max_passages: Maximum number of passages to include
            
        Returns:
            Formatted prompt string
        """
        # Limit number of passages
        passages = passages[:max_passages]
        
        # Build passage section
        passage_text = ""
        for i, passage in enumerate(passages, 1):
            source = passage.get("source_title", "Unknown")
            chapter = passage.get("chapter", "")
            score = passage.get("similarity_score", 0)
            content = passage.get("content", "")
            
            passage_text += f"""
Source {i}: {source}
{f'Chapter: {chapter}' if chapter else ''}
Relevance Score: {score:.2f}
Content: {content}

---"""
        
        # Build the prompt
        prompt = f"""You are an expert in esotericism, occult philosophy, and the teachings of Manly P. Hall. 
Your task is to answer the user's question using ONLY the provided passages. 
Do NOT use any external knowledge or make up information.

If the passages do not contain enough information to answer the question, say: "I don't have enough information in the available sources to answer that question."

Provided Passages:
{passage_text}

User Question: {query}

Answer:"""
        
        return prompt.strip()
    
    @staticmethod
    def build_refusal_message(query: str) -> str:
        """
        Build a message when no relevant passages are found.
        
        Args:
            query: User's question
            
        Returns:
            Refusal message
        """
        return f"""I'm sorry, but I don't have information about "{query}" in my current knowledge base. 
This question might be outside the scope of the available sources, or might require information not yet indexed.
Please try asking about topics related to Manly P. Hall, esotericism, occult philosophy, or symbolism."""
```

---

### Task 1d.3: Create `backend/generation/llm.py`

**File**: `backend/generation/llm.py`

```python
"""
LLM client for generating answers using Ollama.
"""

import logging
import requests
import json
from typing import Optional
from backend.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    MAX_CONTEXT_LENGTH,
    LLM_TEMPERATURE,
    LLM_TOP_P,
)

logger = logging.getLogger(__name__)


class OllamaClient:
    """Client for communicating with Ollama API."""
    
    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        """
        Initialize Ollama client.
        
        Args:
            model: Model name (e.g., 'llama2:7b')
            base_url: Base URL of Ollama API (default: http://localhost:11434)
        """
        self.model = model
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
        
        logger.info(f"Initialized OllamaClient: {model} at {base_url}")
        
        # Check connection
        try:
            response = requests.get(f"{base_url}/api/version", timeout=5)
            if response.status_code == 200:
                logger.info("✓ Connected to Ollama server")
            else:
                logger.warning(f"Ollama server returned status {response.status_code}")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama server: {e}")
            logger.error(f"Make sure Ollama is running: ollama serve")
    
    def generate(
        self,
        prompt: str,
        temperature: float = LLM_TEMPERATURE,
        top_p: float = LLM_TOP_P,
        timeout: int = 300,
    ) -> Optional[str]:
        """
        Generate text using Ollama.
        
        Args:
            prompt: Prompt text
            temperature: Temperature for generation (0.0-1.0)
            top_p: Nucleus sampling parameter
            timeout: Request timeout in seconds
            
        Returns:
            Generated text, or None if error
        """
        logger.debug(f"Generating with model {self.model}...")
        
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "temperature": temperature,
                "top_p": top_p,
                "stream": False,
            }
            
            response = requests.post(
                self.api_url,
                json=payload,
                timeout=timeout,
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code} {response.text}")
                return None
            
            result = response.json()
            generated_text = result.get("response", "").strip()
            
            logger.debug(f"  ✓ Generated {len(generated_text)} characters")
            
            return generated_text
        
        except requests.exceptions.Timeout:
            logger.error(f"Ollama request timed out after {timeout} seconds")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Failed to connect to Ollama at {self.api_url}")
            logger.error("Make sure Ollama is running: ollama serve")
            return None
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            return None
```

---

### Task 1d.4: Create `backend/generation/__init__.py` and `answer.py`

**File**: `backend/generation/answer.py`

This module ties together retrieval and generation:

```python
"""
End-to-end answer generation pipeline.
Retrieves passages and generates grounded answers.
"""

import logging
import time
from typing import Dict, List, Optional
from backend.retrieval.retriever import Retriever
from backend.generation.prompts import PromptBuilder
from backend.generation.llm import OllamaClient
from backend.config import RELEVANCE_THRESHOLD, RETRIEVAL_K

logger = logging.getLogger(__name__)


class AnswerGenerator:
    """Generates answers to questions using retrieval + generation."""
    
    def __init__(self):
        """Initialize generator components."""
        self.retriever = Retriever()
        self.prompt_builder = PromptBuilder()
        self.llm = OllamaClient()
    
    def generate_answer(
        self,
        query: str,
        top_k: int = RETRIEVAL_K,
        threshold: float = RELEVANCE_THRESHOLD,
    ) -> Dict:
        """
        Generate an answer to a query.
        
        Args:
            query: User's question
            top_k: Number of passages to retrieve
            threshold: Minimum similarity score
            
        Returns:
            Dict with answer, sources, and metadata
        """
        logger.info(f"Generating answer for: '{query}'")
        
        result = {
            "question": query,
            "answer": "",
            "sources": [],
            "confidence": 0.0,
            "metadata": {
                "retrieval_time_ms": 0,
                "generation_time_ms": 0,
                "total_time_ms": 0,
                "num_passages_retrieved": 0,
            }
        }
        
        start_time = time.time()
        
        # ===== RETRIEVAL =====
        retrieval_start = time.time()
        passages = self.retriever.retrieve(query, top_k=top_k, threshold=threshold)
        retrieval_time = (time.time() - retrieval_start) * 1000
        
        result["metadata"]["retrieval_time_ms"] = retrieval_time
        result["metadata"]["num_passages_retrieved"] = len(passages)
        
        # Check if we have relevant passages
        if not passages:
            logger.warning("  ✗ No relevant passages found")
            result["answer"] = self.prompt_builder.build_refusal_message(query)
            result["confidence"] = 0.0
            return result
        
        # Calculate average confidence from passage scores
        avg_confidence = sum(p.get("similarity_score", 0) for p in passages) / len(passages)
        result["confidence"] = avg_confidence
        
        # ===== GENERATION =====
        generation_start = time.time()
        
        # Build grounded prompt
        prompt = self.prompt_builder.build_grounded_prompt(query, passages)
        
        # Generate answer
        answer = self.llm.generate(prompt)
        
        generation_time = (time.time() - generation_start) * 1000
        result["metadata"]["generation_time_ms"] = generation_time
        
        if not answer:
            logger.error("  ✗ LLM failed to generate answer")
            result["answer"] = "I encountered an error while generating an answer. Please try again."
            return result
        
        result["answer"] = answer
        result["sources"] = [
            {
                "chunk_id": p.get("chunk_id", ""),
                "content": p.get("content", ""),
                "source_title": p.get("source_title", ""),
                "chapter": p.get("chapter", ""),
                "page_range": p.get("page_range", ""),
                "similarity_score": p.get("similarity_score", 0),
            }
            for p in passages
        ]
        
        total_time = (time.time() - start_time) * 1000
        result["metadata"]["total_time_ms"] = total_time
        
        logger.info(f"  ✓ Answer generated in {total_time:.1f}ms")
        
        return result
```

---

### Task 1d.5: Test Retrieval and Generation

**File**: `scripts/test_retrieval_generation.py`

```python
"""
Test retrieval and generation pipeline.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.generation.answer import AnswerGenerator

# Initialize generator
print("Initializing answer generator...")
generator = AnswerGenerator()

# Test queries
test_queries = [
    "What is Freemasonry?",
    "Tell me about symbolism",
    "What was Manly P. Hall's view on esotericism?",
]

print("\n" + "=" * 70)
print("TESTING RETRIEVAL AND GENERATION")
print("=" * 70)

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 70)
    
    result = generator.generate_answer(query)
    
    print(f"Answer: {result['answer']}\n")
    print(f"Sources ({len(result['sources'])}):")
    for i, source in enumerate(result['sources'], 1):
        print(f"  {i}. {source['source_title']} - {source['chapter']}")
        print(f"     Score: {source['similarity_score']:.3f}")
    
    print(f"\nConfidence: {result['confidence']:.3f}")
    print(f"Total time: {result['metadata']['total_time_ms']:.1f}ms")
    print("-" * 70)

print("\n✓ Test complete!")
```

**Run it**:
```bash
python scripts/test_retrieval_generation.py
```

---

### Task 1d.6: Commit Retrieval and Generation

```bash
git add backend/retrieval/ backend/generation/ scripts/test_retrieval_generation.py
git commit -m "Phase 1d: Implement retrieval and generation layers"
```

---

## Phase 1e: API and Server (1–2 days)

[Due to token limits, I'll provide a condensed version. Create these files:]

### Task 1e.1: Create `backend/api/models.py`

Define Pydantic models for API requests/responses.

### Task 1e.2: Create `backend/api/routes.py`

Define FastAPI endpoints.

### Task 1e.3: Update `backend/main.py`

Import and register routes.

### Task 1e.4: Create Frontend

Simple HTML/JS chat interface.

---

## Phase 1f: Integration and Testing

Testing with real queries and refining answers.

---

## Verification Checklist

- [ ] All ingestion, indexing, retrieval, generation modules created and tested
- [ ] Ollama server running and model available
- [ ] Book successfully ingested to Chroma
- [ ] Queries retrieve relevant passages
- [ ] LLM generates grounded answers with citations
- [ ] API endpoints respond correctly
- [ ] Frontend loads and sends/receives queries

---

## Next Phase

Once Phase 1 is verified, proceed to **Phase 2: Grounding and Quality Control** (see [ARCHITECTURE.md](ARCHITECTURE.md#phase-2-grounding-and-quality-control)).

---

## Troubleshooting

### Ollama not running
```bash
ollama serve
```

### Chroma permission error
```bash
rm -rf data/chroma_db/
# Restart and re-ingest
```

### Out of memory
Reduce `CHUNK_SIZE` or `EMBEDDING_BATCH_SIZE` in `config.py`.

---

**Happy building! Track your progress and document learnings as you go.** 📚🤖
