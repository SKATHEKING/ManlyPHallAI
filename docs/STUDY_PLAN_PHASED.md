# Phased Study Plan for ManlyPHallAI

This study plan is organized by phase so you can prepare before implementation rather than trying to learn everything at once. The goal is to build the right knowledge at the right time.

## How to use this plan

- Study one phase at a time.
- Spend time understanding the code and docs for that phase before moving on.
- Use the project files as your primary reference.
- Keep notes in the project docs or in your own learning log.

## Phase 0: Project Orientation and Python Foundations

### Goal
Understand the repository, its architecture, and the core Python tools used throughout the project.

### Subjects to study
- Python fundamentals: functions, classes, modules, packages, virtual environments
- File handling and paths with pathlib
- Logging and configuration via environment variables
- Basic dependency management and virtual environments
- How the repository is divided into backend, bot, scripts, data, and docs

### Project files to read
- README.md
- ARCHITECTURE.md
- GETTING_STARTED.md
- backend/config.py
- backend/main.py

### What you should be able to do before moving on
- Explain the project goal in your own words
- Describe each major folder and its role
- Trace how configuration flows into the app

## Phase 1: Ingestion and Document Processing

### Goal
Learn how raw text documents become usable chunks for downstream retrieval.

### Subjects to study
- Text parsing for PDF, EPUB, and TXT files
- Text cleaning and normalization
- Chunking strategies and overlap
- Metadata preservation and source traceability
- Why ingestion should be separate from indexing

### Project files to read
- backend/ingestion/parsers.py
- backend/ingestion/cleaner.py
- backend/ingestion/chunker.py
- scripts/ingest_book.py
- tests/test_ingestion.py

### What you should be able to do before moving on
- Explain the ingestion pipeline from file to chunk
- Describe why chunk size and overlap matter
- Compare the behavior of different document types

## Phase 2: Embeddings, Vector Search, and Retrieval

### Goal
Understand how meaning-based search works in the system.

### Subjects to study
- Embeddings and semantic similarity
- Cosine similarity
- Vector databases and persistence
- Query embedding and retrieval ranking
- Similarity thresholds and top-k search

### Project files to read
- backend/indexing/embedder.py
- backend/indexing/store.py
- backend/retrieval/retriever.py
- scripts/test_indexing.py
- scripts/test_retrieval_generation.py

### What you should be able to do before moving on
- Explain how a query becomes a vector and how it is matched
- Describe how retrieval quality depends on chunking and embeddings
- Explain why this approach is better than simple keyword matching for this project

## Phase 3: Prompting and Generation

### Goal
Learn how retrieved passages are turned into grounded answers.

### Subjects to study
- Prompt construction
- Context injection from retrieved chunks
- Grounded generation and hallucination avoidance
- Citation formatting
- Confidence scoring and answer quality trade-offs

### Project files to read
- backend/generation/prompts.py
- backend/generation/llm.py
- backend/generation/answer.py

### What you should be able to do before moving on
- Explain how the prompting layer uses retrieved context
- Identify where hallucinations can enter the pipeline
- Describe why citations matter for this project

## Phase 4: API and Service Layer

### Goal
Understand how the system becomes usable by other applications.

### Subjects to study
- FastAPI basics
- Pydantic request and response models
- Routing and validation
- Startup and shutdown lifecycle
- Error handling and health checks

### Project files to read
- backend/api/models.py
- backend/api/routes.py
- backend/main.py

### What you should be able to do before moving on
- Map each API endpoint to the underlying pipeline step
- Explain the difference between request validation and application logic
- Describe how the API supports the bot and future interfaces

## Phase 5: Discord Integration and User Experience

### Goal
Learn how the system becomes a real assistant inside a chat platform.

### Subjects to study
- Discord bot setup
- Slash commands and async event handling
- Message formatting and response limits
- Bot lifecycle and startup configuration

### Project files to read
- bot/discord_bot.py
- scripts/run_discord_bot.py

### What you should be able to do before moving on
- Explain how a Discord command triggers the RAG workflow
- Describe what makes chat UIs different from REST APIs
- Recognize common issues with bot responsiveness and message size

## Phase 6: Testing, Reliability, and Deployment Readiness

### Goal
Learn how to verify the system rather than assume it works.

### Subjects to study
- Unit testing
- Integration and end-to-end testing
- Performance testing
- Docker and containerization basics
- CI/CD concepts

### Project files to read
- tests/
- Dockerfile
- docker-compose.yml
- PHASE_1F_PLAN.md
- PHASE_1F_TESTING_GUIDE.md

### What you should be able to do before moving on
- Differentiate between unit, integration, and end-to-end test goals
- Explain why deployment readiness matters even for a learning project
- Describe how reproducibility improves debugging

## Phase 7: Evaluation and Quality Improvement

### Goal
Learn how to measure whether the system is actually good, not just functional.

### Subjects to study
- Relevance and correctness metrics
- Citation quality and hallucination detection
- Benchmark datasets
- Prompt and retrieval evaluation
- Quality loops for improvement

### Project files to read
- PHASE_2_PLAN.md
- COMPLETE_ROADMAP.md
- PROJECT_EVOLUTION.md

### What you should be able to do before moving on
- Define what quality means in this project
- Explain how you would evaluate the system over time
- Identify the difference between functional success and quality success

## Suggested study order

1. Phase 0: Orientation
2. Phase 1: Ingestion
3. Phase 2: Retrieval
4. Phase 3: Generation
5. Phase 4: API layer
6. Phase 5: Discord interface
7. Phase 6: Testing and deployment
8. Phase 7: Evaluation and quality

## Study habit to keep

Each study session should answer three questions:
- What part of the system am I learning?
- What project file explains it?
- What trade-off or design decision is behind it?
