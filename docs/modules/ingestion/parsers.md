# `backend/ingestion/parsers.py` — Document parsers

Design notes extracted from the module's docstrings. The source keeps its summary
lines and every `Args`/`Returns`/`Raises` contract.

## What the module does

Provides functions to extract text from different file formats and preserve
important metadata (page numbers, chapter names, file info).

Supported formats:

- **PDF**: Extract text page-by-page and track page numbers
- **EPUB**: Extract text chapter-by-chapter and track chapter structure
- **TXT**: Plain text with filename metadata

## Architecture

1. Each parser function (`parse_pdf`, `parse_epub`, `parse_txt`) reads a specific format
2. Returns a list of `ParsedDocument` objects containing text and metadata
3. `parse_document()` dispatches to the correct parser based on file extension
4. All parsers handle errors gracefully and log warnings/errors

## Example usage

```python
docs = parse_document("book.pdf")  # Returns list[ParsedDocument]
for doc in docs:
    print(doc.text)        # The extracted text
    print(doc.metadata)    # Source file, page number, etc.
```

## `parse_pdf`

Process:

1. Opens the PDF file using pypdf
2. Iterates through each page
3. Extracts text from each page (skips empty pages)
4. Creates `ParsedDocument` for each page with metadata:
   - Source file path
   - Format (`"pdf"`)
   - Page number (1-indexed)
   - Total pages
   - Filename

Error handling:

- If PDF is corrupted or unreadable, logs an error and returns empty list
- If a page fails to extract text, it's silently skipped

## `parse_epub`

Process:

1. Opens EPUB file using ebooklib
2. Iterates through all items (chapters/sections) in the book
3. Extracts text from HTML content
4. Removes HTML tags and cleans whitespace
5. Creates `ParsedDocument` for each chapter with metadata:
   - Source file path
   - Format (`"epub"`)
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

> The HTML-stripping regex here duplicates `remove_html_tags` in
> `backend/ingestion/cleaner.py`, and `ingest_document` runs `clean_text` over
> every parsed segment, so EPUB content currently has its tags stripped twice.

## `parse_txt`

Process:

1. Opens text file with UTF-8 encoding
2. Reads entire content
3. Returns single `ParsedDocument` with filename metadata

Note: Unlike PDF/EPUB which return multiple documents (one per page/chapter), TXT
files are returned as a single document. This is fine because the chunking step
(Phase 1b) will split it into smaller pieces.

> This single-segment behaviour is also why the chunk-ID collision bug never
> showed up in testing: every fixture in the suite is a `.txt` file.

Error handling:

- Uses `"ignore"` error handling for encoding issues (skips bad characters)
- Skips empty files
- Returns empty list if file cannot be read
