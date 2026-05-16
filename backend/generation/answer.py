"""
End-to-end answer generation pipeline.
Retrieves passages and generates grounded answers with citations.

This module orchestrates Phase 1d:
1. Take user question
2. Retrieve relevant chunks from indexed books
3. Build context-aware prompt
4. Call LLM to generate answer
5. Format answer with citations

Main function: answer_question(question, store) -> Answer

The answer generation pipeline is the core of the RAG system:
Input: User question
Process: Retrieve context → Build prompt → Generate answer → Add citations
Output: Answer with source citations

Example usage:
    from backend.generation.answer import answer_question
    from backend.indexing import ChromaStore
    
    store = ChromaStore()
    result = answer_question("What is enlightenment?", store)
    
    print(result["answer"])
    print(result["citations"])  # Sources
"""

from __future__ import annotations

import logging
from typing import Any

from backend.retrieval.retriever import retrieve_chunks
from backend.generation.llm import OllamaLLM
from backend.generation.prompts import build_rag_prompt
from backend.config import RETRIEVAL_K, RELEVANCE_THRESHOLD, OLLAMA_MODEL


logger = logging.getLogger(__name__)


class Answer:
    """
    Structured answer with citations and metadata.
    
    Represents a complete answer with:
    - Generated text (answer)
    - Source citations (where info came from)
    - Retrieved context (chunks used)
    - Confidence (based on retrieval scores)
    
    This is returned by answer_question() and can be serialized for API/Discord.
    """
    
    def __init__(
        self,
        text: str,
        citations: list[str],
        retrieved_chunks: list[dict],
        confidence: float = 0.0,
    ):
        """
        Initialize an Answer object.
        
        Args:
            text: The generated answer text
            citations: List of formatted citations (e.g., "page 10 of book.pdf")
            retrieved_chunks: Raw chunks used for generation
            confidence: Average similarity score of retrieved chunks (0-1)
        """
        self.text = text
        self.citations = citations
        self.retrieved_chunks = retrieved_chunks
        self.confidence = confidence
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for API/JSON serialization.
        
        Returns:
            Dict with answer, citations, confidence, etc.
        """
        return {
            "answer": self.text,
            "citations": self.citations,
            "confidence": self.confidence,
            "num_sources": len(self.retrieved_chunks),
            "retrieved_chunks": [
                {
                    "text": chunk.get("text", ""),
                    "source": chunk.get("source", ""),
                    "page": chunk.get("page"),
                    "score": chunk.get("score", 0),
                }
                for chunk in self.retrieved_chunks
            ],
        }
    
    def to_markdown(self) -> str:
        """
        Format answer as Markdown for Discord or web display.
        
        Returns:
            Formatted string with answer and citations
        """
        lines = []
        lines.append(f"**Answer:**\n\n{self.text}")
        
        if self.citations:
            lines.append("\n\n**Sources:**")
            for citation in self.citations:
                lines.append(f"- {citation}")
        
        if self.confidence > 0:
            confidence_pct = self.confidence * 100
            lines.append(f"\n**Confidence:** {confidence_pct:.0f}%")
        
        return "\n".join(lines)


def answer_question(
    question: str,
    store: Any,
    k: int = RETRIEVAL_K,
    threshold: float = RELEVANCE_THRESHOLD,
    model: str = OLLAMA_MODEL,
    use_streaming: bool = False,
) -> Answer:
    """
    End-to-end pipeline: question → retrieve → generate → answer with citations.
    
    This is the core RAG pipeline that combines all components:
    1. Validate question
    2. Retrieve relevant chunks
    3. Build prompt with context
    4. Call LLM to generate answer
    5. Extract and format citations
    6. Return structured Answer
    
    Args:
        question: User's question (string)
        store: ChromaStore instance (from Phase 1c)
        k: Number of chunks to retrieve (default 5)
        threshold: Minimum relevance threshold (default 0.5)
        model: Which model to use (default from config)
        use_streaming: Whether to stream response (for interactive display)
        
    Returns:
        Answer object with text, citations, and metadata
        
    Raises:
        ValueError: If question is empty
        ConnectionError: If Ollama is not running
    """
    # Validate input
    if not question or not question.strip():
        logger.error("Empty question provided")
        raise ValueError("Question cannot be empty")
    
    question = question.strip()
    logger.info(f"Answering: {question[:100]}...")
    
    # Step 1: Retrieve relevant chunks
    logger.debug("Step 1: Retrieving relevant chunks...")
    retrieved = retrieve_chunks(
        question,
        store,
        k=k,
        threshold=threshold,
    )
    
    if not retrieved:
        logger.warning("No relevant chunks found for question")
        return Answer(
            text="I couldn't find relevant information to answer your question.",
            citations=[],
            retrieved_chunks=[],
            confidence=0.0,
        )
    
    # Step 2: Build prompt with context
    logger.debug("Step 2: Building prompt...")
    prompt = build_rag_prompt(question, retrieved)
    
    # Step 3: Generate answer
    logger.debug("Step 3: Generating answer...")
    try:
        llm = OllamaLLM(model=model)
        
        if use_streaming:
            # Stream response (collect into single string)
            answer_text = ""
            for chunk in llm.generate_stream(prompt):
                answer_text += chunk
        else:
            # Batch mode
            answer_text = llm.generate(prompt)
        
    except Exception as e:
        logger.error(f"Failed to generate answer: {e}")
        answer_text = f"Error: Could not generate answer ({str(e)})"
    
    # Step 4: Format citations
    logger.debug("Step 4: Formatting citations...")
    citations = _format_citations(retrieved)
    
    # Step 5: Calculate average confidence
    confidence = sum(chunk.get("score", 0) for chunk in retrieved) / len(retrieved) if retrieved else 0
    
    # Step 6: Return structured answer
    logger.info(f"Generated answer with {len(citations)} citations (confidence: {confidence:.2%})")
    
    return Answer(
        text=answer_text,
        citations=citations,
        retrieved_chunks=retrieved,
        confidence=confidence,
    )


def _format_citations(retrieved_chunks: list[dict]) -> list[str]:
    """
    Extract and format citations from retrieved chunks.
    
    Converts raw metadata into human-readable citations.
    Example output:
    - "The Secret Teachings of All Ages, page 42"
    - "book.pdf, Chapter 3"
    
    Args:
        retrieved_chunks: List of dicts from retrieve_chunks()
        
    Returns:
        List of formatted citation strings
    """
    citations = []
    seen_sources = set()  # Avoid duplicate citations
    
    for chunk in retrieved_chunks:
        # Build citation from metadata
        source = chunk.get("source", "unknown")
        
        # Skip if we've already cited this source
        if source in seen_sources:
            continue
        seen_sources.add(source)
        
        # Extract metadata
        page = chunk.get("page")
        chapter = chunk.get("chapter")
        filename = chunk.get("filename", "")
        score = chunk.get("score", 0)
        
        # Build citation string
        parts = []
        if filename:
            parts.append(filename)
        
        if chapter:
            parts.append(f"Chapter: {chapter}")
        elif page is not None:
            parts.append(f"Page {page}")
        
        citation = ", ".join(parts)
        
        if citation and citation not in citations:
            citations.append(citation)
    
    return citations


def answer_question_with_source_filter(
    question: str,
    store: Any,
    source_file: str,
    k: int = RETRIEVAL_K,
) -> Answer:
    """
    Answer question restricted to a specific source file.
    
    Useful for single-book Q&A (e.g., "Ask me anything about X book").
    
    Args:
        question: User's question
        store: ChromaStore instance
        source_file: Filename to restrict results to
        k: Number of chunks to retrieve
        
    Returns:
        Answer object
    """
    logger.info(f"Answering from {source_file}: {question[:100]}...")
    
    # Retrieve and filter by source
    retrieved = retrieve_chunks(question, store, k=k*2)  # Get more to filter
    filtered = [r for r in retrieved if r["filename"] == source_file][:k]
    
    if not filtered:
        return Answer(
            text=f"No relevant information found in {source_file}.",
            citations=[],
            retrieved_chunks=[],
            confidence=0.0,
        )
    
    # Build prompt and generate
    prompt = build_rag_prompt(question, filtered)
    llm = OllamaLLM()
    answer_text = llm.generate(prompt)
    citations = _format_citations(filtered)
    confidence = sum(c.get("score", 0) for c in filtered) / len(filtered)
    
    return Answer(answer_text, citations, filtered, confidence)


__all__ = ["Answer", "answer_question", "answer_question_with_source_filter"]
