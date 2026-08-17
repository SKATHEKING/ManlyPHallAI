"""
Demo script: exercise the full RAG loop. Requires a running Ollama.

Not a test -- it asserts nothing. See docs/modules/scripts.md
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.ingestion import ingest_document
from backend.indexing import index_chunks
from backend.retrieval import retrieve_chunks
from backend.generation.prompts import build_rag_prompt
from backend.generation.llm import OllamaLLM
from backend.generation import answer_question


def create_sample_book() -> Path:
    """Create sample book for testing."""
    sample_dir = Path("data/books")
    sample_dir.mkdir(parents=True, exist_ok=True)
    
    sample_file = sample_dir / "test_rag_sample.txt"
    
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
    
    Chapter III: The Law of Correspondence
    
    As the Hermetic philosophers taught, "As above, so below; as below, so above." 
    This law of correspondence means that patterns repeat at different scales of reality. 
    The laws governing the macrocosm also govern the microcosm. The structure of the atom 
    mirrors the structure of the solar system. The human body reflects the body of the universe.
    
    Understanding this principle allows us to perceive unity in apparent diversity. 
    By studying the small, we learn about the large. By understanding ourselves, 
    we understand the cosmos.
    """
    
    with open(sample_file, "w", encoding="utf-8") as f:
        f.write(sample_content)
    
    print(f"✓ Created sample book: {sample_file}")
    return sample_file


def test_phase_1b_1c():
    """Test ingestion and indexing (Phase 1b + 1c)."""
    print("\n[Phase 1b+1c: Ingestion & Indexing]")
    
    # Create and ingest sample
    sample_file = create_sample_book()
    
    print("  Ingesting document...")
    chunks = ingest_document(sample_file)
    print(f"  ✓ Created {len(chunks)} chunks")
    
    # Index chunks
    print("  Indexing chunks...")
    store = index_chunks(chunks, show_progress=False)
    print(f"  ✓ Indexed {store.get_collection_size()} chunks")
    
    return store, chunks


def test_phase_1d_retrieval(store):
    """Test retrieval (Phase 1d)."""
    print("\n[Phase 1d: Retrieval]")
    
    # Test queries
    test_queries = [
        "What is enlightenment?",
        "Tell me about the law of correspondence",
        "What is the Hermetic principle?",
    ]
    
    for query in test_queries:
        print(f"\n  Query: '{query}'")
        
        start = time.time()
        retrieved = retrieve_chunks(query, store, k=3)
        elapsed = time.time() - start
        
        print(f"  ✓ Retrieved {len(retrieved)} chunks in {elapsed:.2f}s")
        
        if retrieved:
            top_result = retrieved[0]
            print(f"    Top result: {top_result['text'][:100]}... (score: {top_result['score']:.2%})")


def test_phase_1d_prompts(store):
    """Test prompt building (Phase 1d)."""
    print("\n[Phase 1d: Prompt Building]")
    
    query = "What is enlightenment?"
    print(f"  Building prompt for: '{query}'")
    
    retrieved = retrieve_chunks(query, store, k=3)
    if not retrieved:
        print("  ✗ No retrieval results")
        return None
    
    prompt = build_rag_prompt(query, retrieved)
    print(f"  ✓ Built prompt ({len(prompt)} chars)")
    print(f"\n  Prompt preview:\n  ---\n  {prompt[:300]}...\n  ---")
    
    return prompt


def test_phase_1d_generation(store):
    """Test generation (Phase 1d) - requires Ollama."""
    print("\n[Phase 1d: Generation with LLM]")
    
    # Check if Ollama is running
    try:
        llm = OllamaLLM()
        if not llm.is_running():
            print("  ⚠ Ollama is not running. Skipping LLM test.")
            print("    To enable: ollama serve (in another terminal)")
            return None
    except Exception as e:
        print(f"  ⚠ Ollama not available: {e}")
        print("    To enable: ollama serve (in another terminal)")
        return None
    
    # Test query
    query = "What is the law of correspondence?"
    print(f"\n  Question: '{query}'")
    
    try:
        start = time.time()
        answer = answer_question(query, store)
        elapsed = time.time() - start
        
        print(f"\n  ✓ Generated answer in {elapsed:.2f}s")
        print(f"\n  Answer:\n  {answer.text}")
        print(f"\n  Sources:")
        for citation in answer.citations:
            print(f"    - {citation}")
        print(f"\n  Confidence: {answer.confidence:.2%}")
        
        return answer
        
    except Exception as e:
        print(f"  ✗ Generation failed: {e}")
        return None


def main():
    """Run complete Phase 1d test."""
    print("🚀 Testing Retrieval & Generation Pipeline (Phase 1d)\n")
    
    # Phase 1b+1c: Prepare indexed store
    print("=" * 60)
    store, chunks = test_phase_1b_1c()
    
    # Phase 1d tests
    print("\n" + "=" * 60)
    test_phase_1d_retrieval(store)
    
    print("\n" + "=" * 60)
    prompt = test_phase_1d_prompts(store)
    
    print("\n" + "=" * 60)
    answer = test_phase_1d_generation(store)
    
    # Summary
    print("\n" + "=" * 60)
    print("\n✓ Phase 1d tests complete!")
    print("\n💡 Next steps:")
    print("   - Phase 1e: API routes (FastAPI endpoints)")
    print("   - Phase 1e: Discord bot integration")
    print("   - Phase 2: Quality control and evaluation")


if __name__ == "__main__":
    main()
