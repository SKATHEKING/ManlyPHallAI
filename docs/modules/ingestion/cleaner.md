# `backend/ingestion/cleaner.py` — Text cleaning and normalization

Design notes extracted from the module's docstrings. Prepares parsed text for
chunking and embedding.

## Why clean at all

Cleaning makes extracted text suitable for:

1. Semantic chunking (removes noise that would affect splitting)
2. Embedding (removes control characters that could confuse the model)
3. Display (removes extraneous whitespace and formatting artifacts)

## What it handles

- Whitespace normalization (collapse multiple spaces/newlines/tabs)
- Control character removal (invisible Unicode characters)
- HTML/XML remnants (from EPUB parsing)
- Encoding issues (bad Unicode)

## Pipeline

`clean_text()` applies all cleaning steps in sequence:

```
Input text → remove control chars → remove HTML → normalize whitespace → output
```

## Example usage

```python
raw_text = "Hello  \n\n  <b>world</b>  \t  !"  # Messy text
clean = clean_text(raw_text)
# Result: "Hello\n\n world !"  (clean and ready for processing)
```

> `remove_html_tags` here uses the same regex that `parse_epub` already applies
> while parsing, so EPUB content passes through HTML stripping twice.
