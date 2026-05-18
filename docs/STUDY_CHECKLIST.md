# Study Checklist

Use this checklist to turn the study plan into measurable progress. Check items off only after you can explain them clearly and point to the code or docs where they appear.

## Week 1: Architecture and Python Basics

- [ ] I can explain the project phases from Phase 1 to Phase 5.
- [ ] I can describe the role of each top-level folder in the repo.
- [ ] I can explain how environment variables feed into backend/config.py.
- [ ] I can describe what backend/main.py does at startup.
- [ ] I can explain Python modules, packages, and virtual environments.
- [ ] I can explain why the project uses pathlib, logging, and dataclasses.

Resources:
- Python tutorial: https://docs.python.org/3/tutorial/
- venv: https://docs.python.org/3/tutorial/venv.html
- logging: https://docs.python.org/3/library/logging.html

## Week 2: Ingestion and Chunking

- [ ] I can explain the difference between PDF, EPUB, and TXT ingestion.
- [ ] I can describe what the cleaner does before chunking.
- [ ] I can explain why overlap is used in chunking.
- [ ] I can trace a sample book from parsing to chunk objects.
- [ ] I can explain what metadata is preserved and why it matters later.

Resources:
- PyPDF2: https://pypdf2.readthedocs.io/
- ebooklib: https://docs.sourcefabric.org/projects/ebooklib/
- LangChain text splitters: https://python.langchain.com/docs/concepts/text_splitters/

## Week 3: Embeddings and Retrieval

- [ ] I can explain what embeddings represent.
- [ ] I can explain why cosine similarity is used.
- [ ] I can describe what Chroma stores and why persistence matters.
- [ ] I can explain how retrieve_chunks() filters results.
- [ ] I can describe the role of k and the relevance threshold.

Resources:
- sentence-transformers: https://www.sbert.net/
- Chroma: https://docs.trychroma.com/
- cosine similarity: https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity

## Week 4: Generation and Prompting

- [ ] I can explain how retrieved chunks become prompt context.
- [ ] I can explain how citations are formatted.
- [ ] I can describe what makes a prompt grounded.
- [ ] I can explain the difference between streaming and batch generation.
- [ ] I can explain how confidence is computed.

Resources:
- Ollama: https://ollama.com/docs
- prompt engineering: https://platform.openai.com/docs/guides/prompt-engineering
- RAGAS: https://docs.ragas.io/

## Week 5: API and Discord

- [ ] I can explain the purpose of each Pydantic model in backend/api/models.py.
- [ ] I can map each route in backend/api/routes.py to its pipeline step.
- [ ] I can explain why the API exists alongside the Discord bot.
- [ ] I can explain why the bot defers responses for long tasks.
- [ ] I can explain the Discord 2000-character limit workaround.

Resources:
- FastAPI: https://fastapi.tiangolo.com/tutorial/
- Pydantic: https://docs.pydantic.dev/
- discord.py: https://discordpy.readthedocs.io/

## Week 6: Testing and Deployment

- [ ] I can explain what the Phase 1f tests are trying to prove.
- [ ] I can separate unit, integration, E2E, and performance tests.
- [ ] I can explain why Docker and Compose are useful here.
- [ ] I can explain the purpose of the GitHub Actions workflows.
- [ ] I can describe how to verify the API and bot in a reproducible setup.

Resources:
- pytest: https://docs.pytest.org/
- Docker: https://docs.docker.com/
- GitHub Actions: https://docs.github.com/en/actions

## Week 7: Evaluation and Phase 2 Concepts

- [ ] I can define relevance, correctness, citation quality, and hallucination rate.
- [ ] I can explain why a benchmark dataset is needed.
- [ ] I can describe what an evaluation harness does.
- [ ] I can explain how prompt and retrieval A/B tests would work.
- [ ] I can describe how Phase 2 improves Phase 1.

Resources:
- PHASE_2_PLAN.md
- RAGAS: https://docs.ragas.io/
- Hugging Face Evaluate: https://huggingface.co/docs/evaluate/
- scikit-learn evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html

## Completion Rule

Do not count a topic as done until you can do all three:

- explain it in plain language
- point to the repo file that uses it
- summarize the trade-off the project made
