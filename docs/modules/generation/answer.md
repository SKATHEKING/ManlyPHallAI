# `backend/generation/answer.py` — End-to-end answer pipeline

Design notes extracted from the module's docstrings. Retrieves passages and
generates grounded answers with citations.

## What the module does

Orchestrates Phase 1d:

1. Take user question
2. Retrieve relevant chunks from indexed books
3. Build context-aware prompt
4. Call LLM to generate answer
5. Format answer with citations

Main function: `answer_question(question, store) -> Answer`

The answer generation pipeline is the core of the RAG system.

- **Input**: user question
- **Process**: retrieve context → build prompt → generate answer → add citations
- **Output**: `Answer` with source citations

## Example usage

```python
from backend.generation.answer import answer_question
from backend.indexing import ChromaStore

store = ChromaStore()
result = answer_question("What is enlightenment?", store)

print(result.text)
print(result.citations)  # Sources
```

## Confidence

Confidence is the mean retrieval score across the chunks that survived the
relevance threshold. It measures how well the question matched the corpus, not
how correct the answer is — a confidently retrieved passage can still be
summarised badly.

## Citation formatting

`_format_citations` de-duplicates on the full `source` path but renders the
`filename` basename, producing strings like `"kybalion.pdf, Page 12"`. The prompt
builder formats the same chunk differently (`"kybalion.pdf, page 12"`, lowercase,
falling back to `section N` where there is no page), so the citation the user sees
and the label the model sees are produced by two separate code paths.

## Error handling

The LLM is currently constructed inside the `try` block, so a connection failure
is caught and turned into an answer whose text begins `"Error: Could not generate
answer"` — returned with a normal 200 response. An outage therefore looks like a
successful answer to callers.
