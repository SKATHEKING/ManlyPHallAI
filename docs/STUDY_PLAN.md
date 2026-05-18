# ManlyPHallAI Study Plan

This project is meant to be a learning experience, so this study plan follows the codebase in the same order the system itself works: foundation first, then ingestion, indexing, retrieval, generation, APIs, testing, deployment, and finally quality evaluation.

Use this as a week-by-week roadmap. The estimated time assumes about 6 to 10 hours per week. If you have more time, spend it on the practice tasks and source reading; if you have less time, keep the project reading and the hands-on exercises, then stretch the schedule.

## How To Use This Plan

- Read the listed project files first.
- Read the external resources second.
- Do the practice tasks last.
- Keep a short learning log in `PROJECT_EVOLUTION.md` or a personal note file.

## Week 1: Project Architecture and Python Foundations

Estimated time: 6 to 8 hours

### Topics

- Repository structure and phase roadmap.
- Python modules, packages, virtual environments, and type hints.
- Logging, pathlib, dataclasses, exceptions, and configuration via environment variables.
- How the project is organized by backend, bot, scripts, data, and docs.

### Read in the project

- `README.md`
- `ARCHITECTURE.md`
- `PROJECT_EVOLUTION.md`
- `technologies.md`
- `resources.md`
- `backend/config.py`
- `backend/main.py`

### External resources

- Python tutorial: https://docs.python.org/3/tutorial/
- Virtual environments: https://docs.python.org/3/tutorial/venv.html
- Logging: https://docs.python.org/3/library/logging.html
- pathlib: https://docs.python.org/3/library/pathlib.html
- dataclasses: https://docs.python.org/3/library/dataclasses.html

### Activities

- Draw the project architecture from memory.
- List every top-level folder and explain its purpose.
- Explain how environment variables flow into `backend/config.py`.
- Write a one-page summary of the system in your own words.

### Outcome

By the end of the week, you should be able to explain the project at a high level and describe how Python is being used as the base layer.

## Week 2: Document Ingestion and Cleaning

Estimated time: 6 to 10 hours

### Topics

- Parsing PDF, EPUB, and TXT sources.
- Text normalization and cleanup.
- File metadata and source traceability.
- Why ingestion is separated from indexing.

### Read in the project

- `backend/ingestion/parsers.py`
- `backend/ingestion/cleaner.py`
- `backend/ingestion/chunker.py`
- `backend/ingestion/__init__.py`
- `scripts/ingest_book.py`
- `tests/test_ingestion.py`

### External resources

- PyPDF2 / pypdf docs: https://pypdf2.readthedocs.io/
- ebooklib docs: https://docs.sourcefabric.org/projects/ebooklib/
- regex docs: https://docs.python.org/3/library/re.html
- LangChain text splitters: https://python.langchain.com/docs/concepts/text_splitters/

### Activities

- Trace one sample document through parse → clean → chunk.
- Compare what metadata is kept for PDF versus EPUB versus TXT.
- Experiment on paper with different chunk sizes and overlap values.
- Write down the trade-off between larger chunks and retrieval precision.

### Outcome

You should understand how raw source material becomes structured chunks that can be indexed and cited later.

## Week 3: Embeddings, Vector Databases, and Retrieval

Estimated time: 7 to 10 hours

### Topics

- Sentence embeddings and cosine similarity.
- Vector store basics and persistence.
- Query embedding and semantic search.
- Similarity thresholds and ranking.

### Read in the project

- `backend/indexing/embedder.py`
- `backend/indexing/store.py`
- `backend/indexing/__init__.py`
- `backend/retrieval/retriever.py`
- `tests/test_indexing.py`
- `tests/test_retrieval_generation.py`

### External resources

- sentence-transformers: https://www.sbert.net/
- Chroma docs: https://docs.trychroma.com/
- Cosine similarity reference: https://scikit-learn.org/stable/modules/metrics.html#cosine-similarity
- Vector search overview: https://www.pinecone.io/learn/vector-search/

### Activities

- Explain why embeddings are used instead of keyword search.
- Trace what happens when a query enters `retrieve_chunks()`.
- Compare the meaning of `k`, `threshold`, and `score`.
- Write a short note on why persistence matters for the vector store.

### Outcome

You should be able to describe how the system finds semantically similar passages and why retrieval quality depends on the embedding model and chunking strategy.

## Week 4: Prompting, Answer Generation, and Grounding

Estimated time: 7 to 10 hours

### Topics

- Prompt construction.
- Context injection from retrieved chunks.
- Grounded generation and citation formatting.
- Confidence scores and refusal behavior.
- Streaming versus batch generation.

### Read in the project

- `backend/generation/prompts.py`
- `backend/generation/llm.py`
- `backend/generation/answer.py`
- `backend/generation/__init__.py`
- `PROJECT_EVOLUTION.md` sections on prompt engineering and threshold tuning

### External resources

- Ollama docs: https://ollama.com/docs
- Prompt engineering guide: https://platform.openai.com/docs/guides/prompt-engineering
- LangChain prompt templates: https://python.langchain.com/docs/concepts/prompt_templates/
- RAGAS docs: https://docs.ragas.io/

### Activities

- Rewrite the answer pipeline as a numbered sequence in your own words.
- Identify where hallucination could enter the pipeline.
- Compare grounded prompts with generic prompts.
- Create a short checklist for source citation quality.

### Outcome

You should understand how retrieved context becomes an answer, and why good prompting is just as important as good retrieval.

## Week 5: FastAPI, Pydantic, and API Design

Estimated time: 6 to 9 hours

### Topics

- Request/response validation.
- API routing and response models.
- Startup/shutdown lifecycle behavior.
- Health checks and error handling.
- How the API supports other interfaces.

### Read in the project

- `backend/api/models.py`
- `backend/api/routes.py`
- `backend/api/__init__.py`
- `backend/main.py`
- `GETTING_STARTED.md`

### External resources

- FastAPI tutorial: https://fastapi.tiangolo.com/tutorial/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- Pydantic docs: https://docs.pydantic.dev/
- HTTP status codes reference: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

### Activities

- Map each API endpoint to the code that implements it.
- Explain why the models were moved into a dedicated module.
- Compare FastAPI validation to handwritten input checking.
- Use the OpenAPI docs mentally: what should a client see at `/docs`?

### Outcome

You should understand how the project exposes its core RAG logic through a typed HTTP interface.

## Week 6: Discord Bot and User Interaction

Estimated time: 6 to 9 hours

### Topics

- Discord bot setup and slash commands.
- Async command handling.
- Response formatting and Discord message limits.
- Feedback, errors, and command sync.

### Read in the project

- `bot/discord_bot.py`
- `bot/__init__.py`
- `scripts/run_discord_bot.py`
- `PHASE_1_SUMMARY.md` section on the Discord bot

### External resources

- discord.py docs: https://discordpy.readthedocs.io/
- asyncio docs: https://docs.python.org/3/library/asyncio.html
- Discord developer portal: https://discord.com/developers/docs/intro

### Activities

- Explain why Discord is the primary interface in this project.
- Trace what happens when `/ask` is used.
- Write down why the bot defers responses for long operations.
- Think through how the project handles messages that exceed Discord limits.

### Outcome

You should understand how the retrieval system becomes a user-facing assistant inside Discord.

## Week 7: Testing, Reliability, and Performance

Estimated time: 7 to 10 hours

### Topics

- Unit tests, integration tests, and end-to-end tests.
- Performance baselines and latency measurement.
- CI/CD workflows and reproducible environments.
- Docker and Compose for local runtime consistency.

### Read in the project

- `PHASE_1F_TESTING_GUIDE.md`
- `PHASE_1F_PLAN.md`
- `PHASE_1F_PROGRESS.md`
- `tests/`
- `.github/workflows/`
- `Dockerfile`
- `docker-compose.yml`

### External resources

- pytest docs: https://docs.pytest.org/
- Docker docs: https://docs.docker.com/
- Docker Compose docs: https://docs.docker.com/compose/
- GitHub Actions docs: https://docs.github.com/en/actions

### Activities

- Read the test file names and infer what behavior each test protects.
- Explain the difference between validation, smoke testing, and benchmarking.
- Learn what the Docker image is trying to make reproducible.
- Identify which tests depend on Ollama and which do not.

### Outcome

You should be able to reason about how the project proves correctness and how it stays runnable across machines.

## Week 8: Evaluation, Quality Control, and Phase 2 Concepts

Estimated time: 7 to 10 hours

### Topics

- Evaluation metrics for relevance, correctness, and citation quality.
- Hallucination detection.
- Benchmark datasets and result tracking.
- Prompt and retrieval A/B testing.
- How Phase 2 improves the Phase 1 system.

### Read in the project

- `PHASE_2_PLAN.md`
- `PROJECT_EVOLUTION.md`
- `DECISIONS.md`
- `COMPLETE_ROADMAP.md`

### External resources

- RAGAS docs: https://docs.ragas.io/
- Hugging Face Evaluate: https://huggingface.co/docs/evaluate/
- scikit-learn model evaluation: https://scikit-learn.org/stable/modules/model_evaluation.html
- Basic information retrieval metrics: https://en.wikipedia.org/wiki/Information_retrieval

### Activities

- Define what “good” means for this project in measurable terms.
- Draft a small benchmark of 10 questions and expected sources.
- Explain the difference between retrieval quality and answer quality.
- Write a short evaluation rubric for citations and hallucination.

### Outcome

You should be ready to design the evaluation layer that turns the project into a measurable learning system.

## Optional Weeks 9 to 10: Broader ML and Product Depth

Estimated time: 4 to 8 hours per week

These weeks are optional but useful if you want deeper context beyond the immediate stack.

### Topics

- Information retrieval theory.
- Prompt versioning and experiment tracking.
- Basic observability and logging strategy.
- Product thinking for a domain-specific assistant.

### Resources

- Introduction to information retrieval: https://nlp.stanford.edu/IR-book/
- MLflow docs for experiment tracking: https://mlflow.org/docs/latest/index.html
- OpenTelemetry docs: https://opentelemetry.io/docs/
- 12-Factor App principles: https://12factor.net/

### Activities

- Compare the project’s current design to a production-grade RAG system.
- Write a short proposal for Phase 3 or Phase 4 based on what you learned.
- Identify the top three technical risks still remaining.

## Suggested Study Workflow Each Week

- Day 1: Read the project files for the topic.
- Day 2: Read the official external docs.
- Day 3: Trace the code flow on paper.
- Day 4: Run or inspect the relevant command or test.
- Day 5: Write a short summary of what you learned and what confused you.

## Recommended Learning Rule

For every concept, answer these three questions:

- What problem does this solve in the project?
- Where does it appear in the code?
- What trade-off did the project make by choosing it?
