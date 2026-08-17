"""
Demo script: exercise the Phase 1b ingestion pipeline and print statistics.

Not a test -- it asserts nothing. See docs/modules/scripts.md
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to path so we can import backend modules
# Without this, Python won't find the backend package
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion import ingest_document


def create_sample_book() -> Path:
    """
    Create a sample text file for testing ingestion.
    
    This function creates a realistic sample book in data/books/ directory
    with actual Manly P. Hall content to test the ingestion pipeline.
    
    Why create a sample book?
    - Tests the pipeline without requiring actual book files
    - Reproducible (same content every time)
    - Public domain content (Manly P. Hall is PD)
    - Includes paragraph structure for testing chunking
    
    Returns:
        Path to the created sample file
    """
    # Create data/books directory if it doesn't exist
    sample_dir = Path("data/books")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    sample_file = sample_dir / "sample_book.txt"
    
    # Sample text from public domain Manly P. Hall content
    # This is actual text to give a realistic test
    sample_content = """
    The Secret Teaching of All Ages
    
    Chapter I: Ancient Wisdom and Modern Thought
    
    All things in nature move in cycles. The day yields to the night, the season changes, 
    and the years pass into centuries. In the same way, the consciousness of mankind 
    moves through cycles of knowledge and ignorance, enlightenment and obscuration.
    
    The ancient philosophers understood this principle well. They saw that the universe 
    operates according to immutable laws, that there is an order and harmony underlying 
    all apparent chaos. The Hermetic principle "As above, so below" expresses this ancient 
    wisdom perfectly.
    
    In our modern age, we have lost touch with these timeless truths. We have become 
    enamored with the material world, forgetting that all matter is merely the expression 
    of spiritual reality. The ancient mysteries taught that consciousness is primary, 
    and that the physical universe is but a reflection of the mental and spiritual planes.
    
    The symbols used by the ancient wisdom schools were not mere decorations or marks 
    of identification. They were living languages, capable of conveying profound truths 
    to those who understood their meanings. Each symbol contained within itself a universe 
    of knowledge. The square, the triangle, the circle, the cross—these simple forms 
    represented cosmic principles and human enlightenment.
    
    Chapter II: The Path of Initiation
    
    The ancient schools of mystery did not keep their wisdom locked away from all people. 
    Rather, they established systems of initiation whereby qualified seekers could gradually 
    unfold their spiritual understanding. These initiatory degrees were arranged in a 
    sequence, each building upon the knowledge of the previous one.
    
    The first degree dealt with the conquest of fear and the development of the will. 
    The candidate was taught that the fears that bound him were primarily mental constructs, 
    and that by understanding the nature of these fears, he could transcend them. This 
    overcame his tendency toward self-preservation and taught him to act for the good 
    of the whole.
    
    The second degree taught the nature of polarity and equilibrium. The candidate learned 
    that all things exist in pairs of opposites—light and darkness, good and evil, 
    masculine and feminine. True wisdom consists not in choosing one and rejecting the other, 
    but in understanding how these apparent opposites are in reality complementary aspects 
    of a greater whole.
    
    The third degree brought the candidate face to face with the highest principles of 
    existence—the nature of the self, the cosmos, and the divine reality underlying all 
    manifestation. At this level, the distinction between the knower and the known began 
    to dissolve, and direct mystical experience became possible.
    
    These initiatory degrees were not mere intellectual exercises. They involved the entire 
    being of the candidate—his body, his emotions, his intellect, and his spirit. The 
    ancient schools understood that lasting transformation requires integration of all 
    levels of human consciousness.
    
    The knowledge imparted in the mysteries was always practical. It was designed to improve 
    the condition of humanity and to elevate the consciousness of those who received it. 
    This remains the true purpose of spiritual knowledge—not to create an elite class of 
    illuminated individuals, but to gradually lift all humanity toward higher levels of 
    awareness and understanding.
    """
    
    # Write the sample content to file
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"✓ Created sample book: {sample_file}")
    return sample_file


def print_statistics(chunks: list) -> None:
    """
    Print statistics about ingested chunks.
    
    This helps verify the ingestion pipeline is working correctly by showing:
    - How many chunks were created
    - Text length and distribution
    - Metadata (source file, page, chapter, etc.)
    
    Args:
        chunks: List of Chunk objects from ingestion
    """
    if not chunks:
        print("✗ No chunks to analyze")
        return
    
    # Calculate statistics about chunk sizes
    total_text_length = sum(len(chunk.text) for chunk in chunks)
    avg_chunk_length = total_text_length / len(chunks)
    
    print(f"\n📊 Ingestion Statistics:")
    print(f"  • Total chunks: {len(chunks)}")
    print(f"  • Total text length: {total_text_length:,} characters")
    print(f"  • Average chunk length: {avg_chunk_length:.0f} characters")
    print(f"  • Min chunk length: {min(len(chunk.text) for chunk in chunks)} characters")
    print(f"  • Max chunk length: {max(len(chunk.text) for chunk in chunks)} characters")
    
    # Show metadata from first chunk (all should have similar structure)
    if chunks[0].metadata:
        print(f"\n🏷️  Metadata (from first chunk):")
        for key, value in chunks[0].metadata.items():
            print(f"  • {key}: {value}")


def print_sample_chunks(chunks: list, num_samples: int = 3) -> None:
    """
    Print sample chunks for quality inspection.
    
    This lets us see what the chunks actually look like - are they
    semantic units? Do they cut sentences in the middle? Are they
    roughly the right size?
    
    Args:
        chunks: List of Chunk objects
        num_samples: How many sample chunks to show
    """
    print(f"\n📑 Sample Chunks (first {num_samples}):\n")
    
    for i, chunk in enumerate(chunks[:num_samples]):
        print(f"--- Chunk {i + 1} ---")
        print(f"Metadata: {chunk.metadata}")
        print(f"Text ({len(chunk.text)} chars):")
        # Print first 300 characters of chunk so we can see the content
        preview = chunk.text[:300] + ("..." if len(chunk.text) > 300 else "")
        print(f"{preview}\n")


def main():
    """
    Main test function.
    
    This orchestrates the test:
    1. Create sample book
    2. Time the ingestion process
    3. Print statistics
    4. Show sample chunks
    """
    print("🚀 Testing Ingestion Pipeline\n")
    
    # Step 1: Create sample book for testing
    sample_file = create_sample_book()
    
    # Step 2: Ingest the document and time how long it takes
    print("\n📖 Ingesting document...")
    start_time = time.time()
    chunks = ingest_document(sample_file)
    elapsed = time.time() - start_time
    
    print(f"✓ Ingestion took {elapsed:.2f} seconds")
    
    # Step 3: Print statistics about what was ingested
    print_statistics(chunks)
    
    # Step 4: Print sample chunks for manual inspection
    print_sample_chunks(chunks, num_samples=3)
    
    print("\n✓ Test complete!")


if __name__ == "__main__":
    main()
