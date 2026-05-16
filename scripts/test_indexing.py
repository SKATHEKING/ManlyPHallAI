"""
Test the indexing pipeline (Phase 1c).

This test validates the complete indexing workflow:
1. Ingest a sample book (Phase 1b)
2. Generate embeddings for all chunks (Phase 1c)
3. Store in Chroma vector database (Phase 1c)
4. Verify retrieval capability (Phase 1d preview)

This is the first end-to-end test combining Phase 1b + 1c:
- Input: Book file
- Process: Ingest → Chunk → Embed → Index
- Output: Searchable vector database

Usage:
    PYTHONPATH=. python scripts/test_indexing.py

Expected output:
    🚀 Testing Indexing Pipeline (Phase 1c)
    
    [Phase 1b: Ingestion]
    ✓ Created sample book
    ✓ Ingested and chunked
    
    [Phase 1c: Indexing]
    📝 Generating embeddings
    ✓ Indexed N chunks
    
    [Verification: Retrieval]
    🔍 Testing similarity search
    ✓ Retrieved K similar chunks
    
    📊 Results:
    • Store size: N chunks
    • Sample query: "enlightenment"
    • Top 3 results with scores...

This demonstrates the core RAG pipeline:
1. Ingest (parse + chunk) ✓
2. Index (embed + store) ✓ THIS TEST
3. Retrieve (vector search) ✓ THIS TEST
4. Generate (LLM answers) - Phase 1d
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion import ingest_document
from backend.indexing import index_chunks
from backend.indexing.embedder import embed_texts


def create_sample_book() -> Path:
    """
    Create a sample book for testing indexing.
    
    Same as test_ingestion.py - creates a small Manly P. Hall sample.
    
    Returns:
        Path to sample book file
    """
    sample_dir = Path("data/books")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    sample_file = sample_dir / "test_index_sample.txt"
    
    # Sample text from public domain
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
    and that by understanding the nature of these fears, he could transcend them.
    
    The knowledge imparted in the mysteries was always practical. It was designed to improve 
    the condition of humanity and to elevate the consciousness of those who received it. 
    This remains the true purpose of spiritual knowledge.
    """
    
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"✓ Created sample book: {sample_file}")
    return sample_file


def test_indexing_pipeline():
    """
    Complete end-to-end test of ingestion + indexing pipeline.
    
    Tests:
    1. Ingestion: Parse and chunk book
    2. Embedding: Generate vectors for chunks
    3. Storage: Store in Chroma
    4. Retrieval: Verify semantic search works
    """
    print("🚀 Testing Indexing Pipeline (Phase 1c)\n")
    
    # ========== PHASE 1B: INGESTION ==========
    print("[Phase 1b: Ingestion]")
    sample_file = create_sample_book()
    
    print("\n📖 Ingesting document...")
    start_ingest = time.time()
    chunks = ingest_document(sample_file)
    ingest_time = time.time() - start_ingest
    
    print(f"✓ Ingested in {ingest_time:.2f}s: {len(chunks)} chunks")
    
    # ========== PHASE 1C: INDEXING ==========
    print("\n[Phase 1c: Indexing]")
    print(f"\n📝 Generating embeddings for {len(chunks)} chunks...")
    start_embed = time.time()
    store = index_chunks(chunks, show_progress=True)
    embed_time = time.time() - start_embed
    
    print(f"✓ Indexed in {embed_time:.2f}s")
    
    # ========== VERIFICATION: RETRIEVAL ==========
    print("\n[Verification: Semantic Search]")
    
    # Test 1: Search for "enlightenment"
    test_queries = [
        ("What is enlightenment?", "Searching for enlightenment..."),
        ("Tell me about initiation", "Searching for initiation..."),
        ("cosmic principles", "Searching for cosmic principles..."),
    ]
    
    for query_text, description in test_queries:
        print(f"\n🔍 {description}")
        print(f"   Query: '{query_text}'")
        
        # Generate embedding for query
        query_embedding = embed_texts(query_text)[0]
        
        # Search the store
        results = store.search(query_embedding, k=3)
        
        # Display results
        print(f"   ✓ Found {len(results['ids'][0])} relevant chunks:")
        
        for i, (chunk_id, distance, metadata, document) in enumerate(
            zip(
                results["ids"][0],
                results["distances"][0],
                results["metadatas"][0],
                results["documents"][0],
            )
        ):
            # Convert distance to similarity score (0-1, where 1 is identical)
            similarity = 1 - distance
            print(f"\n     [{i+1}] Similarity: {similarity:.2%}")
            print(f"         Source: {metadata.get('filename')} (chunk {metadata.get('chunk_index')})")
            print(f"         Preview: {document[:150]}...")
    
    # ========== STATISTICS ==========
    print("\n\n📊 Indexing Statistics:")
    print(f"  • Total chunks indexed: {store.get_collection_size()}")
    print(f"  • Ingestion time: {ingest_time:.2f}s")
    print(f"  • Embedding + indexing time: {embed_time:.2f}s")
    print(f"  • Total time: {ingest_time + embed_time:.2f}s")
    print(f"  • Average per chunk: {(ingest_time + embed_time) / len(chunks):.3f}s")
    
    print("\n✓ Indexing test complete!")
    print("\n💡 Next: Phase 1d (Retrieval + Generation with LLM)")


if __name__ == "__main__":
    test_indexing_pipeline()
