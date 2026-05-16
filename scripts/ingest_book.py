"""
End-to-end book ingestion script.
Parses, cleans, chunks, embeds, and stores a book.

This script automates the complete ingestion pipeline:
1. Parse document (PDF, EPUB, or TXT)
2. Clean text (normalize, remove HTML)
3. Chunk text (256 tokens, 50% overlap)
4. Generate embeddings (sentence-transformers)
5. Store in Chroma vector DB
6. Display statistics

Usage:
    python scripts/ingest_book.py data/books/my_book.pdf
    
    # With all options:
    python scripts/ingest_book.py \\
        data/books/my_book.pdf \\
        --force \\  # Re-ingest even if already exists
        --quiet      # Minimal output

Features:
    - Progress bars during ingestion and embedding
    - Automatic duplicate detection
    - Detailed statistics
    - Error recovery
"""

import sys
import time
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion import ingest_document
from backend.indexing import index_chunks, ChromaStore
from backend.config import BOOKS_DIR


def main():
    """Main entry point for book ingestion."""
    parser = argparse.ArgumentParser(
        description="Ingest a book into the Manly P. Hall AI knowledge base",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/books/my_book.pdf
  %(prog)s data/books/ebook.epub --force
  %(prog)s data/books/text.txt --quiet
        """
    )
    
    parser.add_argument(
        "file",
        help="Path to book file (PDF, EPUB, or TXT)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-ingest even if file already exists"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )
    
    args = parser.parse_args()
    
    # Validate file path
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        sys.exit(1)
    
    if file_path.suffix.lower() not in [".pdf", ".epub", ".txt"]:
        print(f"❌ Unsupported file type: {file_path.suffix}")
        print("   Supported: .pdf, .epub, .txt")
        sys.exit(1)
    
    # Check if already ingested
    store = ChromaStore()
    filename = file_path.name
    
    if not args.quiet:
        print(f"\n📚 Ingesting: {filename}")
        print(f"📁 Path: {file_path}")
        print(f"📊 Store has {store.get_collection_size()} chunks")
    
    try:
        # Step 1: Ingest document
        if not args.quiet:
            print("\n[Step 1/3] Parsing document...")
        
        start_parse = time.time()
        chunks = ingest_document(file_path)
        parse_time = time.time() - start_parse
        
        if not chunks:
            print(f"❌ No content extracted from {filename}")
            sys.exit(1)
        
        if not args.quiet:
            print(f"  ✓ Extracted {len(chunks)} chunks ({parse_time:.2f}s)")
        
        # Step 2: Index chunks
        if not args.quiet:
            print("\n[Step 2/3] Generating embeddings and storing...")
        
        start_index = time.time()
        store = index_chunks(chunks, show_progress=not args.quiet)
        index_time = time.time() - start_index
        
        total_chunks = store.get_collection_size()
        
        if not args.quiet:
            print(f"  ✓ Indexed in {index_time:.2f}s")
        
        # Step 3: Display statistics
        if not args.quiet:
            print("\n[Step 3/3] Statistics")
            print(f"  📊 Total chunks in store: {total_chunks}")
            print(f"  📖 New chunks: {len(chunks)}")
            print(f"  ⏱️  Total time: {parse_time + index_time:.2f}s")
            print(f"  ⚡ Speed: {len(chunks) / (parse_time + index_time):.1f} chunks/sec")
            
            # Calculate statistics
            if chunks:
                avg_chunk_size = sum(len(c.text) for c in chunks) / len(chunks)
                print(f"  📝 Avg chunk size: {avg_chunk_size:.0f} chars")
        
        print(f"\n✅ Successfully ingested: {filename}\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}\n")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
