# `backend/generation/prompts.py` — Prompt templates

Design notes extracted from the module's docstrings. Ensures the LLM only uses
provided passages as sources.

## What the module does

Contains templates for building prompts that:

1. Provide retrieved context to the LLM
2. Instruct the LLM to answer based only on context
3. Request citations to specific passages
4. Prevent hallucination and false information

Key functions:

- `build_rag_prompt(question, chunks) -> prompt string`
- `build_citation_request(chunks) -> formatted context string`

## Why prompt design matters

The prompt design is critical to RAG quality. Poor prompts lead to:

- LLM ignoring provided context
- Hallucinated information not in passages
- No citations
- Off-topic answers

Good prompts:

- Clearly state to use ONLY provided context
- Format context clearly (separate passages)
- Ask for explicit citations
- Limit response length

## Structure of the assembled prompt

`build_rag_prompt` concatenates four parts: a system instruction, the numbered
passages with their source labels and relevance percentages, the question, and a
closing output instruction. With no chunks it degrades to
`"Question: ...\n\nNo context available."`.

The exact output is pinned byte for byte by `tests/test_characterization.py`, so
any change to the wording is a deliberate, visible one.

## Other builders

Four further builders exist — citation, question-answer, summarization and
extraction — along with a `PROMPTS` dictionary that maps names to *strings*
rather than to the functions themselves, and which nothing reads. Turning that
into a real registry of callables is what would make prompt style selectable.
