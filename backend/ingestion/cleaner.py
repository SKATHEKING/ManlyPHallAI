"""
Text cleaning and normalization utilities.
Prepares parsed text for chunking and embedding.

This module is responsible for cleaning extracted text so it's suitable for:
1. Semantic chunking (removes noise that would affect splitting)
2. Embedding (removes control characters that could confuse the model)
3. Display (removes extraneous whitespace and formatting artifacts)

Handles:
- Whitespace normalization (collapse multiple spaces/newlines/tabs)
- Control character removal (invisible Unicode characters)
- HTML/XML remnants (from EPUB parsing)
- Encoding issues (bad Unicode)

The clean_text() function applies all cleaning steps in sequence:
  Input text → remove control chars → remove HTML → normalize whitespace → output

Example usage:
    raw_text = "Hello  \\n\\n  <b>world</b>  \\t  !"  # Messy text
    clean = clean_text(raw_text)
    # Result: "Hello\n\n world !"  (clean and ready for processing)
"""

from __future__ import annotations

import logging
import re
import unicodedata


logger = logging.getLogger(__name__)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace: collapse multiple spaces/newlines/tabs.
    
    Why this matters:
    - Multiple newlines can create artificial "chunk boundaries"
    - Multiple spaces waste tokens in the embedding model
    - Tabs should be converted to spaces for consistency
    
    Examples:
    - "hello    world" → "hello world"      (4 spaces → 1 space)
    - "line1\\n\\n\\nline2" → "line1\\n\\nline2"  (3 newlines → 2)
    - "a\\tb" → "a b"                           (tab → space)
    
    Args:
        text: Raw text from parser
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple newlines (2 or more) with exactly 2 newlines (paragraph break)
    # This preserves paragraph structure while removing excessive breaks
    text = re.sub(r"\n\n+", "\n\n", text)
    
    # Replace multiple spaces (2 or more) with exactly 1 space
    text = re.sub(r" +", " ", text)
    
    # Replace multiple tabs (1 or more) with 1 space
    # Tabs don't typically appear in natural text, but better safe than sorry
    text = re.sub(r"\t+", " ", text)
    
    return text


def remove_control_characters(text: str) -> str:
    """
    Remove control characters and invisible Unicode characters.
    
    Why this matters:
    - Control characters (ASCII 0-31) can cause issues in downstream processing
    - Invisible Unicode characters (zero-width spaces, etc.) confuse embeddings
    - Encoding errors can introduce these characters
    
    Unicode categories we remove:
    - Cc: Control characters (null byte, tab, etc.)
    - Cf: Format characters (zero-width space, soft hyphen, etc.)
    
    Args:
        text: Text possibly containing control chars
        
    Returns:
        Text with control chars removed
    """
    # Keep only characters that are NOT control (Cc) or format (Cf)
    text = "".join(
        char for char in text
        if unicodedata.category(char) not in ("Cc", "Cf")
    )
    return text


def remove_html_tags(text: str) -> str:
    """
    Remove HTML/XML tags from text.
    
    Why this matters:
    - EPUB files contain HTML markup that we don't want in the final text
    - HTML entities (like &nbsp;) need to be decoded
    - Unclosed or malformed tags can create confusing text
    
    Examples:
    - "<p>Hello</p> world" → " Hello  world"  (tags removed)
    - "Hello&nbsp;world" → "Hello world"      (entity decoded)
    - "Hello&lt;world&gt;" → "Hello<world>"   (entities decoded)
    
    Args:
        text: Text possibly containing HTML tags
        
    Returns:
        Text with tags removed
    """
    # Remove HTML/XML tags using regex
    # Pattern: < (opening) followed by anything (non-greedy) followed by > (closing)
    # Replace with space to avoid word concatenation (e.g., "<b>hello</b>world" → "hello world")
    text = re.sub(r"<[^>]+>", " ", text)
    
    # Decode common HTML entities to their text equivalents
    text = text.replace("&nbsp;", " ")   # Non-breaking space → regular space
    text = text.replace("&lt;", "<")     # Less-than symbol
    text = text.replace("&gt;", ">")     # Greater-than symbol
    text = text.replace("&amp;", "&")    # Ampersand (must be last to avoid double-decoding)
    text = text.replace("&quot;", '"')   # Quotation mark
    
    return text


def clean_text(text: str) -> str:
    """
    Comprehensive text cleaning pipeline.
    
    This function applies all cleaning steps in order:
    1. remove_control_characters() - Get rid of invisible junk
    2. remove_html_tags() - Strip formatting markup
    3. normalize_whitespace() - Fix spacing issues
    4. strip() - Remove leading/trailing whitespace
    
    The order matters! For example:
    - If we normalized whitespace first, HTML entities might get mangled
    - If we didn't remove control chars first, some might survive to cause issues
    
    Args:
        text: Raw or semi-processed text
        
    Returns:
        Cleaned text ready for chunking
    """
    # Step 1: Remove invisible/control characters that can cause issues downstream
    text = remove_control_characters(text)
    
    # Step 2: Remove HTML tags and decode entities
    text = remove_html_tags(text)
    
    # Step 3: Normalize whitespace to make text compact and consistent
    text = normalize_whitespace(text)
    
    # Step 4: Remove leading and trailing whitespace
    text = text.strip()
    
    return text
