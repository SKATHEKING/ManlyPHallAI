"""
Generation module for LLM-based answer generation.
Handles prompt construction and LLM integration.

Main entry point: answer_question(question, store) -> Answer

This module orchestrates the generation phase (Phase 1d):
- Retrieve relevant chunks for a question
- Build prompt with context
- Call Ollama LLM for generation
- Format answer with citations

Example usage:
    from backend.generation import answer_question
    from backend.indexing import ChromaStore
    
    store = ChromaStore()
    answer = answer_question("What is enlightenment?", store)
    
    print(answer.text)
    print(answer.to_markdown())
"""

from backend.generation.answer import Answer, answer_question, answer_question_with_source_filter
from backend.generation.llm import OllamaLLM, generate_answer
from backend.generation.prompts import build_rag_prompt


__all__ = [
    "Answer",
    "answer_question",
    "answer_question_with_source_filter",
    "OllamaLLM",
    "generate_answer",
    "build_rag_prompt",
]
