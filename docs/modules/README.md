# Module design notes

The conceptual documentation that used to live inside the source files. Each
module keeps its summary line and every `Args`/`Returns`/`Raises` contract, so
`help()`, IDE tooltips and pydoc still work; the "why" material moved here.

Nothing was deleted — this is a relocation. Each source file points at its page.

## The pipeline

```
ingestion → indexing → retrieval → generation → api / bot
```

[Package overviews](packages.md) — what each package is for, with usage examples.

## By module

| Module | Notes |
|---|---|
| `backend/ingestion/parsers.py` | [parsers.md](ingestion/parsers.md) — per-format process, error handling |
| `backend/ingestion/cleaner.py` | [cleaner.md](ingestion/cleaner.md) — cleaning pipeline |
| `backend/ingestion/chunker.py` | [chunker.md](ingestion/chunker.md) — why chunking, why overlap |
| `backend/indexing/embedder.py` | [embedder.md](indexing/embedder.md) — why sentence-transformers |
| `backend/indexing/store.py` | [store.md](indexing/store.md) — why Chroma, id scheme, scoring |
| `backend/retrieval/retriever.py` | [retriever.md](retrieval/retriever.md) — result shape, threshold |
| `backend/generation/prompts.py` | [prompts.md](generation/prompts.md) — why prompt design matters |
| `backend/generation/llm.py` | [llm.md](generation/llm.md) — running Ollama, sampling |
| `backend/generation/answer.py` | [answer.md](generation/answer.md) — confidence, citations |
| `backend/api/routes.py` | [routes.md](api/routes.md) — endpoints, validation |
| `backend/main.py` | [main.md](main.md) — running it, startup, errors |
| `bot/discord_bot.py` | [discord_bot.md](bot/discord_bot.md) — commands, setup |
| `scripts/*.py` | [scripts.md](scripts.md) — demo scripts and expected output |

## Known issues recorded here

Several pages carry a note about behaviour that is wrong or surprising, kept
next to the design it contradicts:

- **Chunk IDs collide across pages** — [chunker.md](ingestion/chunker.md),
  [store.md](indexing/store.md). Multi-page books are largely not indexed.
- **EPUB HTML is stripped twice** — [parsers.md](ingestion/parsers.md),
  [cleaner.md](ingestion/cleaner.md).
- **LLM failures return 200** — [answer.md](generation/answer.md).
- **`source` vs `filename` divergence** — [retriever.md](retrieval/retriever.md).
- **The bot duplicates the API's ask path** — [discord_bot.md](bot/discord_bot.md).
- **Four prompt builders are unreachable** — [prompts.md](generation/prompts.md).
