"""
Generation module for LLM-based answer generation.
Handles prompt construction and LLM integration.

Main entry point: answer_question(question, store) -> Answer

Pipeline overview and examples: docs/modules/packages.md
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
