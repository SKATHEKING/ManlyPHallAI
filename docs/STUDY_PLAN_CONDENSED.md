# Condensed Study Plan

This is the shorter version of the full study plan. It keeps the same learning order but compresses it into 4 focused weeks.

## Week 1: Project Map and Python Foundations

Estimated time: 6 to 8 hours

### Study

- README, architecture, evolution log, technologies, and resources docs
- Python modules, packages, virtual environments, logging, pathlib, dataclasses, and environment variables
- backend/config.py and backend/main.py

### Resources

- Python tutorial: https://docs.python.org/3/tutorial/
- venv: https://docs.python.org/3/tutorial/venv.html
- logging: https://docs.python.org/3/library/logging.html
- pathlib: https://docs.python.org/3/library/pathlib.html

### Outcome

Understand the project structure and the Python conventions used throughout the repo.

## Week 2: Ingestion, Chunking, Embeddings, and Retrieval

Estimated time: 8 to 10 hours

### Study

- backend/ingestion/parsers.py
- backend/ingestion/cleaner.py
- backend/ingestion/chunker.py
- backend/indexing/embedder.py
- backend/indexing/store.py
- backend/retrieval/retriever.py

### Resources

- PyPDF2: https://pypdf2.readthedocs.io/
- ebooklib: https://docs.sourcefabric.org/projects/ebooklib/
- LangChain text splitters: https://python.langchain.com/docs/concepts/text_splitters/
- sentence-transformers: https://www.sbert.net/
- Chroma: https://docs.trychroma.com/

### Outcome

Understand how raw books become searchable chunks and how semantic retrieval works.

## Week 3: Prompting, Generation, API, and Discord

Estimated time: 8 to 10 hours

### Study

- backend/generation/prompts.py
- backend/generation/llm.py
- backend/generation/answer.py
- backend/api/models.py
- backend/api/routes.py
- backend/main.py
- bot/discord_bot.py

### Resources

- Ollama: https://ollama.com/docs
- FastAPI: https://fastapi.tiangolo.com/tutorial/
- Pydantic: https://docs.pydantic.dev/
- discord.py: https://discordpy.readthedocs.io/
- asyncio: https://docs.python.org/3/library/asyncio.html

### Outcome

Understand how the project turns retrieved passages into grounded answers and exposes them through HTTP and Discord.

## Week 4: Testing, Deployment, and Quality Evaluation

Estimated time: 8 to 12 hours

### Study

- PHASE_1F_TESTING_GUIDE.md
- PHASE_1F_PLAN.md
- PHASE_1F_PROGRESS.md
- PHASE_2_PLAN.md
- tests/
- .github/workflows/
- Dockerfile and docker-compose.yml

### Resources

- pytest: https://docs.pytest.org/
- Docker: https://docs.docker.com/
- Docker Compose: https://docs.docker.com/compose/
- GitHub Actions: https://docs.github.com/en/actions
- RAGAS: https://docs.ragas.io/

### Outcome

Understand how the project is validated, containerized, and prepared for the next quality-control phase.

## Weekly Practice Rule

Each week, finish with three things:

- A one-page summary in your own words
- A small code trace or diagram
- A note about one trade-off the project made
