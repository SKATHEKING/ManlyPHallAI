# `backend/generation/llm.py` — Ollama client

Design notes extracted from the module's docstrings. Provides Phase 1d, the
generation step.

## What the module does

1. Integrate with local Ollama LLM
2. Send prompts with retrieved context
3. Generate grounded answers citing sources

Main class: `OllamaLLM` (wrapper around Ollama)
Main function: `generate_answer(prompt, retrieved_chunks) -> str`

Responsibilities:

- Connecting to Ollama service
- Managing model loading/switching
- Generating answers grounded in retrieved chunks
- Handling streaming or batch responses

## Example usage

```python
from backend.generation.llm import OllamaLLM

llm = OllamaLLM()
answer = llm.generate(prompt, temperature=0.3)

# Or use the high-level function:
from backend.generation import generate_answer
answer = generate_answer(prompt, retrieved_chunks)
```

## Running Ollama

Requires the Ollama service running locally:

- Download from [ollama.ai](https://ollama.ai)
- Run: `ollama pull llama2:7b` (or another model)
- The service listens on `http://localhost:11434/`

The base URL is configurable via `OLLAMA_BASE_URL` (or `OLLAMA_URL`, the name
docker-compose uses), and the client appends `/api` to it.

## Sampling parameters

`temperature`, `top_p` and `top_k` all come from settings rather than being
hardcoded. Lower temperature means more deterministic output; the default of 0.3
favours faithfulness to the retrieved passages over fluency.
