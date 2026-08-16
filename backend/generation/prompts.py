"""
Prompt templates for grounded answer generation.
Ensures LLM only uses provided passages as sources.

Key function: build_rag_prompt(question, chunks) -> prompt string

Why prompt design drives RAG quality, the assembled prompt's structure and the
other builders: docs/modules/generation/prompts.md
"""

from __future__ import annotations


def build_rag_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    """
    Build a RAG prompt that instructs LLM to answer using only provided context.
    
    The prompt structure:
    1. System instruction: Use only provided context
    2. Context: Formatted retrieved chunks
    3. Question: User's query
    4. Output instruction: Answer with citations
    
    This design prevents hallucination by making it explicit that
    the LLM should use only the provided passages.
    
    Args:
        question: User's question
        retrieved_chunks: List of dicts from retrieve_chunks()
                         Each chunk should have: text, source, page, chunk_index
        
    Returns:
        Formatted prompt string for LLM
        
    Example output:
        ```
        Use ONLY the following passages to answer the question.
        If the answer is not in the passages, say "I don't know."
        
        CONTEXT:
        [Passage 1]
        Source: book.pdf, page 42
        
        [Passage 2]
        Source: book.pdf, page 43
        
        QUESTION:
        What is enlightenment?
        
        ANSWER (cite sources):
        ```
    """
    if not retrieved_chunks:
        return f"Question: {question}\n\nNo context available."
    
    # Part 1: System instruction
    system_instruction = (
        "You are a helpful assistant answering questions based on provided passages.\n"
        "IMPORTANT: Answer ONLY using the provided passages.\n"
        "If the answer is not in the passages, say 'I don't know' or 'This information is not in the provided passages.'\n"
        "Be accurate and cite your sources.\n"
        "Avoid speculation or information not in the passages.\n"
    )
    
    # Part 2: Format context passages
    context_sections = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        passage = chunk.get("text", "")
        source = chunk.get("source", "unknown")
        filename = chunk.get("filename", "")
        page = chunk.get("page")
        chunk_index = chunk.get("chunk_index", 0)
        score = chunk.get("score", 0)
        
        # Format source info
        source_parts = []
        if filename:
            source_parts.append(filename)
        if page is not None:
            source_parts.append(f"page {page}")
        elif chunk_index is not None:
            source_parts.append(f"section {chunk_index}")
        
        source_str = ", ".join(source_parts) if source_parts else source
        
        # Format passage with metadata
        context_sections.append(
            f"[Passage {i}]\n"
            f"{passage}\n"
            f"(Source: {source_str}, Relevance: {score:.0%})\n"
        )
    
    context = "\n".join(context_sections)
    
    # Part 3: Question
    question_section = f"Question: {question}"
    
    # Part 4: Output instruction
    output_instruction = (
        "\nAnswer: Answer the question using only the passages above. "
        "Cite which passage(s) you used. "
        "If the answer is not in the passages, say you don't know."
    )
    
    # Combine all parts
    prompt = (
        f"{system_instruction}\n"
        f"PASSAGES:\n"
        f"{context}\n"
        f"{question_section}"
        f"{output_instruction}"
    )
    
    return prompt


def build_citation_prompt(question: str, retrieved_chunks: list[dict]) -> tuple[str, list[dict]]:
    """
    Build prompt and extract citation metadata for post-processing.
    
    This variant returns both the prompt and structured citation info
    so the caller can extract exact citations from the response.
    
    Args:
        question: User's question
        retrieved_chunks: List of retrieved chunks
        
    Returns:
        Tuple of (prompt_string, citation_metadata_list)
    """
    prompt = build_rag_prompt(question, retrieved_chunks)
    
    # Extract citation metadata
    citations = []
    for chunk in retrieved_chunks:
        citations.append({
            "source": chunk.get("source", "unknown"),
            "filename": chunk.get("filename", ""),
            "page": chunk.get("page"),
            "chunk_index": chunk.get("chunk_index"),
            "score": chunk.get("score", 0),
        })
    
    return prompt, citations


def build_question_answer_prompt(question: str, retrieved_chunks: list[dict]) -> str:
    """
    Alternative prompt format using Q&A structure.
    
    This format may work better with some models.
    Uses explicit Q&A structure similar to SQuAD/reading comprehension tasks.
    
    Args:
        question: User's question
        retrieved_chunks: List of retrieved chunks
        
    Returns:
        Formatted prompt string
    """
    if not retrieved_chunks:
        return f"Q: {question}\nA: No context available."
    
    # Combine passages into a single context
    context = "\n\n".join([chunk.get("text", "") for chunk in retrieved_chunks])
    
    # Build QA prompt
    prompt = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Based only on the context above, provide an accurate answer to the question. "
        f"If the answer is not in the context, respond with 'I don't know.' "
        f"Answer:"
    )
    
    return prompt


def build_summarization_prompt(chunks: list[dict]) -> str:
    """
    Build prompt to summarize retrieved passages.
    
    Useful for providing high-level overview before detailed answer.
    
    Args:
        chunks: List of retrieved chunks
        
    Returns:
        Prompt for summarizing passages
    """
    if not chunks:
        return "No passages to summarize."
    
    passages = "\n\n".join([chunk.get("text", "") for chunk in chunks])
    
    prompt = (
        f"Summarize the following passages in 2-3 sentences, capturing the main ideas:\n\n"
        f"{passages}\n\n"
        f"Summary:"
    )
    
    return prompt


def build_extraction_prompt(question: str, chunks: list[dict], entity_type: str = "facts") -> str:
    """
    Build prompt to extract specific information from passages.
    
    Useful for extracting structured data (names, dates, concepts) from unstructured text.
    
    Args:
        question: What to extract (e.g., "Extract all names of philosophers")
        chunks: Retrieved passages
        entity_type: Type of entity to extract (for clarity)
        
    Returns:
        Formatted extraction prompt
    """
    if not chunks:
        return f"No passages to extract from."
    
    passages = "\n\n".join([chunk.get("text", "") for chunk in chunks])
    
    prompt = (
        f"Extract all {entity_type} from the following passages that relate to: {question}\n\n"
        f"Passages:\n{passages}\n\n"
        f"Extraction (list or comma-separated):"
    )
    
    return prompt


# Prompt templates by use case
PROMPTS = {
    "default": "build_rag_prompt",  # Main RAG prompt
    "qa": "build_question_answer_prompt",  # Q&A format
    "summarization": "build_summarization_prompt",  # Summary generation
    "extraction": "build_extraction_prompt",  # Entity/fact extraction
    "citation": "build_citation_prompt",  # With citation metadata
}


__all__ = [
    "build_rag_prompt",
    "build_citation_prompt",
    "build_question_answer_prompt",
    "build_summarization_prompt",
    "build_extraction_prompt",
]
