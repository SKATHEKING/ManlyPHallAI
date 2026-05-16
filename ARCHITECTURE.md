# Manly P. Hall AI Bot — System Architecture

## Overview

This document describes the system architecture for the Manly P. Hall AI Bot across all five phases of development. It outlines design decisions, component interactions, technology choices, and how the system evolves from a Discord-based retrieval system to a full audiovisual AI assistant.

**Document Status**: Phase 1 focus (completed). Phases 2–5 are planned and will be updated as implementation progresses.

---

## Table of Contents

1. [Core Design Principles](#core-design-principles)
2. [System Architecture Overview](#system-architecture-overview)
3. [Phase 1: Discord-Based Knowledge Engine](#phase-1-discord-based-knowledge-engine)
4. [Phase 2: Grounding and Quality Control](#phase-2-grounding-and-quality-control)
5. [Phase 3: Internet-Augmented Research](#phase-3-internet-augmented-research)
6. [Phase 4: Audiovisual Experience](#phase-4-audiovisual-experience)
7. [Phase 5: Iteration and Expansion](#phase-5-iteration-and-expansion)
8. [Technology Stack by Phase](#technology-stack-by-phase)
9. [Data Models and Storage](#data-models-and-storage)
10. [API Design](#api-design)
11. [Deployment Architecture](#deployment-architecture)
12. [Design Decisions and Rationale](#design-decisions-and-rationale)

---

## Core Design Principles

1. **Start Small, Prove Core Value Early**
   - Phase 1 focuses on book-based question answering only.
   - Validate retrieval + generation before adding complexity.
   - Fast feedback loop enables quick iteration.

2. **Prefer Sourced Answers Over Unsupported Generation**
   - Every answer must cite its sources.
   - System refuses to answer if sources are weak or missing.
   - Transparency builds user trust.

3. **Modular, Layered Architecture**
   - Each layer has a single responsibility.
   - Layers can be tested independently.
   - Future phases extend or replace layers without breaking others.

4. **Design for Local Testing and Iteration**
   - Phase 1 runs entirely locally (no external APIs required except optional LLM hosting).
   - Developers can experiment with chunk sizes, models, and prompts quickly.
   - Minimal infrastructure means lower cost and faster debugging.

5. **Maintain Separation of Concerns**
   - Data ingestion, indexing, retrieval, generation, and serving are distinct.
   - Decoupling enables parallel work and easier testing.

---

## System Architecture Overview

### High-Level Conceptual Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                     │
│   (Discord Server, Slash Commands, Message Replies, Threads)│
└────────────────────┬────────────────────────────────────────┘
                     │
                     │ HTTP / WebSocket
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                   API & Orchestration Layer                  │
│    (Discord Bot + FastAPI Support Server, Routing, Format)  │
└─────┬──────────────────────┬──────────────────────┬──────────┘
      │                      │                      │
      ▼                      ▼                      ▼
┌────────────┐         ┌────────────┐        ┌───────────┐
│ Retrieval  │         │ Generation │        │ Media     │
│ Engine     │         │ Engine     │        │ Service   │
│ (Phases 1–3)         │ (Phases 1–4)        │ (Phase 4) │
└────────────┘         └────────────┘        └───────────┘
      │                      │                      │
      ▼                      ▼                      ▼
┌────────────────────────────────────────────────────────────┐
│              Data Layer & External Services                 │
│   (Vector DB, Metadata DB, LLM, TTS, Search APIs, etc.)   │
└────────────────────────────────────────────────────────────┘
```

### Component Hierarchy

```
ManlyPHallAI/
├── backend/                     # Python backend (FastAPI)
│   ├── ingestion/              # Phase 1: Parse and prepare books
│   ├── indexing/               # Phase 1: Vector storage and retrieval
│   ├── retrieval/              # Phase 1–3: Query and reranking
│   ├── generation/             # Phase 1–4: Answer and media generation
│   ├── api/                    # Phase 1+: FastAPI routes and models
│   ├── config.py               # Centralized configuration
│   └── main.py                 # Application entry point
├── bot/                        # Discord bot interface
│   ├── __init__.py             # Bot package
│   └── discord_bot.py          # Discord entry point
├── frontend/                   # Legacy/demo interfaces
│   ├── web/                    # Optional browser demo
│   ├── cli/                    # Optional command-line interface
│   └── avatar/                 # Phase 4: Avatar display
├── data/                        # Data storage
│   ├── books/                  # Phase 1: Book files (PDF, EPUB, TXT)
│   ├── chroma_db/              # Phase 1: Vector index
│   ├── cache/                  # Phase 3+: Cached web pages, TTS audio
│   └── models/                 # Phase 1+: Downloaded embeddings and LLM
├── tests/                       # Test suite
├── docs/                        # Documentation
│   ├── ARCHITECTURE.md         # This file
│   ├── IMPLEMENTATION_GUIDE.md # Step-by-step build instructions
│   ├── DECISIONS.md            # Design rationale and trade-offs
│   └── PROJECT_EVOLUTION.md    # Tracking changes and learnings
└── requirements.txt            # Python dependencies
```

---

## Phase 1: Discord-Based Knowledge Engine

**Goal**: Build a Discord bot that answers questions using a curated collection of books.

**Outcome**: A working system that retrieves relevant passages, generates grounded answers with citations, and replies inside Discord.

### Phase 1 Architecture

#### Layer Diagram

```
┌──────────────────────────────────────────────┐
│       Discord Interface                     │
│  Slash Commands, Mentions, Replies          │
└────────────────────┬─────────────────────────┘
                     │
┌────────────────────▼─────────────────────────┐
│   Discord Bot + FastAPI Support Server      │
│   /ask, /status, /ingest (support)          │
└────────────────────┬─────────────────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
    ▼                ▼                ▼
┌────────┐      ┌────────┐       ┌─────────┐
│Retrieval      │Generate│       │Ingestion│
│Engine         │Engine  │       │Pipeline │
└────┬───┘      └───┬────┘       └────┬────┘
     │              │                 │
     ▼              ▼                 ▼
  Chroma       Ollama/Llama    Parser + Chunker
  (Vector DB)  (Local LLM)     (PyPDF2, ebooklib)
     │              │                 │
     └──────────────┴─────────────────┘
            │
            ▼
    ┌──────────────────┐
    │   Data Storage   │
    │ • Chroma vectors │
    │ • Book files     │
    │ • Config & logs  │
    └──────────────────┘
```

#### Component Descriptions

**1. Ingestion Pipeline**

Responsibility: Parse books and extract clean, structured text with metadata.

Components:
- **PDF Parser** (`ingestion/parsers.py`): Extracts text from PDF files while preserving chapter/page structure.
- **EPUB Parser**: Extracts text from EPUB files.
- **Text Reader**: Handles plain text files.
- **Cleaner** (`ingestion/cleaner.py`): Normalizes text, removes noise (headers, footers, page numbers), standardizes quotes and whitespace.
- **Chunker** (`ingestion/chunker.py`): Splits cleaned text into semantic chunks with configurable size and overlap.

Input: Book files (PDF, EPUB, TXT)
Output: Structured chunk objects with metadata (source, chapter, page, token count)

**2. Indexing Pipeline**

Responsibility: Convert text chunks to embeddings and store in a searchable index.

Components:
- **Embedder** (`indexing/embedder.py`): Generates dense vector representations using sentence-transformers.
- **Vector Store** (`indexing/store.py`): Manages Chroma database instance, handles collection creation and vector insertion.

Input: Cleaned and chunked text with metadata
Output: Indexed vectors in Chroma with searchable metadata

**3. Retrieval Engine**

Responsibility: Answer user queries by finding and ranking relevant passages.

Components:
- **Query Embedder**: Embeds user query using the same model as ingestion.
- **Vector Search** (`retrieval/retriever.py`): Queries Chroma for top-K similar passages.
- **Reranker** (future): Optional reranking by relevance score or metadata filters.

Input: User question
Output: Ranked list of relevant passages with metadata and similarity scores

**4. Generation Engine**

Responsibility: Generate grounded answers using retrieved passages and an LLM.

Components:
- **Prompt Builder** (`generation/prompts.py`): Constructs grounded prompts that inject retrieved passages.
- **LLM Client** (`generation/llm.py`): Communicates with Ollama or Hugging Face to generate answers.
- **Citation Formatter**: Extracts and formats source references in the response.

Input: User question + retrieved passages
Output: Grounded answer with inline citations and source metadata

**5. API Server**

Responsibility: Serve HTTP endpoints for question answering and ingestion management.

Components:
- **FastAPI Support App** (`main.py`): Health, admin, and support endpoints.
- **Routes** (`api/routes.py`): Endpoint definitions.
- **Request/Response Models** (`api/models.py`): Pydantic schemas for validation.
- **Error Handling**: Middleware for logging and exception handling.

Endpoints:
- `POST /ask`: Submit a question, receive an answer with sources.
- `POST /ingest`: Trigger book ingestion from uploaded files or directory.
- `GET /status`: Check ingestion progress and system health.

**6. Configuration Management**

Responsibility: Centralize all tunable parameters.

File: `config.py`

Parameters:
- `CHUNK_SIZE`: Number of tokens per chunk (default: 256)
- `CHUNK_OVERLAP`: Percentage overlap between chunks (default: 50%)
- `RETRIEVAL_K`: Number of passages to retrieve (default: 5)
- `RELEVANCE_THRESHOLD`: Minimum similarity score to consider a passage relevant (default: 0.5)
- `EMBEDDING_MODEL`: sentence-transformers model name
- `LLM_MODEL`: Ollama model name (e.g., "llama2:7b")
- `MAX_CONTEXT_LENGTH`: Max tokens in the prompt to LLM (default: 2048)

#### Data Flow: Question Answering

```
1. User submits question in Discord via slash command or mention
   Question: "What did Manly P. Hall say about Freemasonry?"

2. System receives request at POST /ask endpoint
   → Validate input, log query

3. Query Embedding
   → Embed query using sentence-transformers
   → Result: 384-dimensional vector

4. Vector Retrieval
   → Search Chroma for top-K=5 similar passages
   → Filter by RELEVANCE_THRESHOLD
   → Result: [
       {
         "content": "Freemasonry is a system of morality...",
         "source": "Secret Teachings of All Ages",
         "chapter": "Chapter 5: Freemasonry",
         "score": 0.87
       },
       ... (4 more)
     ]

5. Prompt Construction
   → Build system prompt: "Use ONLY these passages to answer."
   → Inject passages into user context
   → Final prompt: "Passages: [all 5 passages]. Question: [user question]"

6. LLM Generation
   → Send prompt to Ollama/Llama
   → LLM generates response grounded in passages
   → Response: "According to Secret Teachings of All Ages (Chapter 5), 
       Freemasonry is a system of morality..."

7. Response Formatting
   → Extract answer text
   → Extract and format citations
   → Build response JSON:
     {
       "answer": "According to Secret Teachings...",
       "sources": [
         {"title": "Secret Teachings...", "chapter": "5", "score": 0.87}
       ],
       "confidence": 0.87
     }

8. Return to user
   → Display answer and sources in Discord with citations
```

#### Data Flow: Ingestion

```
1. User initiates ingestion via POST /ingest
   → Upload PDF, EPUB, or TXT file
   → Specify book metadata (title, author)

2. File Parsing
   → Route to appropriate parser (PDF/EPUB/TXT)
   → Extract raw text and structure (chapters, sections)
   → Result: List of (text, metadata) tuples

3. Text Cleaning
   → Remove headers, footers, page numbers
   → Normalize whitespace, quotes
   → Standardize section markers
   → Result: Clean text string

4. Semantic Chunking
   → Split by character/sentence/paragraph boundaries
   → Ensure chunks don't exceed CHUNK_SIZE tokens
   → Add overlap (CHUNK_OVERLAP%) to preserve context
   → Result: List of chunk objects:
     [
       {
         "id": "secret-teachings-ch5-001",
         "content": "Freemasonry is...",
         "source_title": "Secret Teachings of All Ages",
         "chapter": "Chapter 5: Freemasonry",
         "page_range": "120-125",
         "tokens": 245,
         "order": 1
       },
       ... (many more)
     ]

5. Embedding Generation
   → Batch embed chunks using sentence-transformers
   → Generate 384-dim vector for each chunk
   → Result: List of (vector, chunk_metadata) pairs

6. Vector Storage
   → Create/open Chroma collection for this book
   → Insert vectors with full metadata
   → Persist to disk at ./data/chroma_db/
   → Log: "Ingested 'Secret Teachings' with 1,247 chunks, ~500KB index"

7. Update Registry
   → Record book metadata in ingestion log
   → Track: title, author, file hash, ingestion date, chunk count
   → Enable later re-ingestion or updates
```

### Phase 1 Data Models

#### Chunk (Internal Representation)

```python
@dataclass
class Chunk:
    id: str                      # Unique identifier (e.g., "book-ch3-001")
    content: str                 # Text content
    source_title: str            # Book title
    source_author: str           # Book author
    chapter: Optional[str]       # Chapter name or section
    page_range: Optional[str]    # Pages in original book
    tokens: int                  # Token count (for tracking size)
    position_in_chapter: int     # Ordinal position within chapter
    file_hash: str              # Hash of source file (for version tracking)
    ingestion_date: datetime    # When this chunk was indexed
```

#### SearchResult (API Response)

```python
@dataclass
class SearchResult:
    chunk_id: str
    content: str
    source_title: str
    chapter: Optional[str]
    similarity_score: float      # 0.0 to 1.0
```

#### Answer (API Response)

```python
@dataclass
class Answer:
    answer: str                  # Generated text
    sources: List[SearchResult]  # List of cited passages
    confidence: float            # Avg similarity of retrieved passages
    generation_time_ms: float
    retrieval_time_ms: float
```

---

## Phase 2: Grounding and Quality Control

**Goal**: Improve answer reliability, enforce citations, and reduce hallucinations.

**Key Changes**:
- Introduce evaluation framework and test datasets.
- Refine prompt templates for better grounding.
- Add refusal logic and confidence scoring.
- Implement observability and metrics.

**Architecture Impact**:
- Addition of `evaluation/` module for testing.
- Extension of `generation/prompts.py` with multiple prompt strategies.
- Addition of `monitoring/` module for logging and metrics.
- Optional: Basic SQLite database for tracking evaluation results.

---

## Phase 3: Internet-Augmented Research

**Goal**: Expand the assistant to include approved online information while maintaining grounding.

**Key Changes**:
- Add web search integration (Brave, Tavily, or SerpAPI).
- Implement source ranking and filtering.
- Combine book and web evidence in responses.
- Introduce caching to reduce redundant searches.

**Architecture Impact**:
- Addition of `search/` module for web queries.
- New `sources/` module for managing book and web sources separately.
- Integration of `retrieval/` to handle multiple source types.
- Optional: Redis cache layer.
- New metadata tracking: URLs, domains, trust scores.

---

## Phase 4: Audiovisual Experience

**Goal**: Transform the assistant into a spoken and visual experience.

**Key Changes**:
- Add text-to-speech (TTS) generation.
- Integrate avatar or talking-image provider.
- Implement media streaming for low latency.
- Synchronize speech, avatar animation, and text.

**Architecture Impact**:
- Addition of `media/tts.py` for speech generation.
- Addition of `media/avatar.py` for avatar control.
- Extension of API to support streaming responses.
- Discord bot upgrade to handle rich embeds, attachments, and interactive controls.
- New media storage for generated audio/video files.

---

## Phase 5: Iteration and Expansion

**Goal**: Improve the system through real usage, broader content, and stronger evaluation.

**Key Changes**:
- Implement experiment tracking and prompt versioning.
- Add A/B testing and feature flags.
- Build dashboards for metrics and analytics.
- Scale indexing and re-indexing pipelines.
- Add CI/CD for safe deployment.

**Architecture Impact**:
- Integration of experiment tracking tool (e.g., MLflow).
- Metrics and analytics dashboard.
- Automated testing and deployment pipeline.
- Distributed indexing for handling larger datasets.

---

## Technology Stack by Phase

### Phase 1: Core Technologies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Language** | Python 3.10+ | Rich ecosystem for data processing and ML; async support via asyncio and FastAPI |
| **Web Framework** | FastAPI | Async, built-in API docs, Pydantic validation, fast development |
| **Parsing** | PyPDF2, ebooklib | Standard, lightweight libraries for PDF and EPUB extraction |
| **Text Splitting** | LangChain RecursiveCharacterTextSplitter | Semantic chunking with overlap; battle-tested |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) | Lightweight (22MB), fast inference, no GPU needed, works offline |
| **Vector DB** | Chroma | Local mode for Phase 1; persistent storage; easy to migrate to server mode later |
| **LLM** | Ollama + Llama 2/3 | Local execution, no API costs, full privacy, can run offline |
| **Discord Bot** | discord.py | Native Discord UX, slash commands, rich embeds |
| **Support API** | FastAPI | Health checks, admin workflows, ingestion support |
| **Testing** | pytest | Standard Python testing framework |
| **Logging** | Python `logging` module | Built-in, configurable |

### Phase 2+: Extended Technologies

| Phase | Component | Technology |
|-------|-----------|-----------|
| **2** | Evaluation | pytest, custom evaluation scripts |
| **2** | Metrics | Python `dataclasses`, JSON output |
| **3** | Web Search | Brave Search API or Tavily |
| **3** | Caching | Redis (optional) |
| **4** | TTS | ElevenLabs API or OpenAI TTS or Azure Speech |
| **4** | Avatar | D-ID, HeyGen, or custom |
| **4** | Streaming** | HTTP Server-Sent Events (SSE) |
| **5** | Experiment Tracking | MLflow or Weights & Biases |
| **5** | Deployment | Docker, Kubernetes (optional) |

---

## Data Models and Storage

### File Structure

```
data/
├── books/
│   ├── secret_teachings.pdf
│   ├── kybalion.epub
│   └── tarot_symbolism.txt
├── chroma_db/
│   ├── index/
│   │   └── (Chroma vector storage)
│   └── metadata.json          # Registry of ingested books
└── ingestion_log.json         # Timestamps and stats per book
```

### Metadata Registry

File: `data/metadata.json`

```json
{
  "books": [
    {
      "title": "The Secret Teachings of All Ages",
      "author": "Manly P. Hall",
      "file_path": "data/books/secret_teachings.pdf",
      "file_hash": "abc123def456",
      "format": "pdf",
      "ingestion_date": "2026-05-16T14:30:00Z",
      "chunk_count": 1247,
      "total_tokens": 450000,
      "index_size_bytes": 524288,
      "status": "ready"
    }
  ]
}
```

### Chroma Collection Schema

Chroma stores vectors with metadata:

```
Collection: "books"
├── Vector ID: "secret-teachings-ch5-001"
│   ├── Embedding: [0.123, -0.456, ..., 0.789]  # 384-dim
│   └── Metadata:
│       ├── source_title: "The Secret Teachings of All Ages"
│       ├── chapter: "Chapter 5: Freemasonry"
│       ├── page_range: "120-125"
│       ├── file_hash: "abc123def456"
│       └── position: 1
├── Vector ID: "secret-teachings-ch5-002"
│   └── (similar structure)
└── ... (more chunks)
```

---

## API Design

### Phase 1 Endpoints

#### POST /ask

**Request**:
```json
{
  "question": "What did Manly P. Hall say about Freemasonry?",
  "top_k": 5,
  "include_raw_passages": false
}
```

**Response**:
```json
{
  "question": "What did Manly P. Hall say about Freemasonry?",
  "answer": "According to Secret Teachings of All Ages (Chapter 5, pages 120-125), Freemasonry is a system of morality...",
  "sources": [
    {
      "chunk_id": "secret-teachings-ch5-001",
      "content": "Freemasonry is a system of morality...",
      "source_title": "The Secret Teachings of All Ages",
      "chapter": "Chapter 5: Freemasonry",
      "page_range": "120-125",
      "similarity_score": 0.87
    }
  ],
  "metadata": {
    "confidence": 0.87,
    "retrieval_time_ms": 15.3,
    "generation_time_ms": 1250.5,
    "total_time_ms": 1265.8,
    "model_used": "llama2:7b",
    "embedding_model": "all-MiniLM-L6-v2"
  }
}
```

#### POST /ingest

**Request**:
```json
{
  "file_path": "data/books/secret_teachings.pdf",
  "book_title": "The Secret Teachings of All Ages",
  "book_author": "Manly P. Hall",
  "format": "pdf"
}
```

**Response**:
```json
{
  "status": "processing",
  "book_id": "secret-teachings-001",
  "chunks_processed": 1247,
  "estimated_time_remaining_s": 45
}
```

#### GET /status

**Response**:
```json
{
  "system_status": "ready",
  "books_indexed": 3,
  "total_chunks": 5421,
  "embedding_model": "all-MiniLM-L6-v2",
  "llm_model": "llama2:7b",
  "chroma_db_size_mb": 650
}
```

---

## Deployment Architecture

### Phase 1: Local Development

All components run on a single machine:

```
Developer Machine
├── Python venv (Python 3.10+)
├── Ollama (running Llama locally)
├── FastAPI server (localhost:8000)
├── Chroma (persistent to disk)
└── Discord Bot (guild channels, slash commands)
```

**How to Run**:
```bash
# 1. Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Download models
ollama pull llama2:7b
python scripts/download_embeddings_model.py

# 3. Start server
python main.py

# 4. Open browser
open http://localhost:8000
```

### Phase 2: Local with SQLite

Add SQLite for evaluation tracking and metrics:

```
Developer Machine
├── Python venv
├── Ollama
├── FastAPI server
├── Chroma (vectors)
├── SQLite (evaluation results, metrics)
└── Discord Bot
```

### Phase 3–4: Cloud-Integrated

Add external services:

```
Discord Client (Desktop/Mobile)
    ↓
CDN (static assets)
    ↓
API Gateway (auth, rate limiting)
    ↓
FastAPI Server (cloud VM or container)
    ├── Ollama or OpenAI API
    ├── Brave Search API (Phase 3)
    ├── ElevenLabs TTS (Phase 4)
    ├── D-ID Avatar (Phase 4)
    └── Redis Cache (Phase 3+)
    ↓
Persistent Storage
    ├── PostgreSQL (metadata, evaluation)
    ├── Chroma (managed or self-hosted)
    └── S3/GCS (book files, audio, video)
```

### Phase 5: Production-Ready

Full CI/CD and scaling:

```
Git Repo → CI/CD Pipeline → Docker Registry
                    ↓
            Kubernetes Cluster
            ├── API Pods (auto-scale)
            ├── Worker Pods (ingestion, TTS)
            ├── Cache (Redis)
            └── Database (PostgreSQL)
                    ↓
            Monitoring & Logging
            ├── Prometheus/Grafana
            ├── ELK Stack or Datadog
            └── Error Tracking (Sentry)
```

---

## Design Decisions and Rationale

### Decision 1: Why Chroma Over PostgreSQL+pgvector?

**Choice**: Chroma for Phase 1; PostgreSQL+pgvector for Phase 2+

**Rationale**:
- Chroma is embeddable and requires zero setup for local development.
- No need to run a separate database service during Phase 1.
- Easy to migrate vectors to PostgreSQL later without changing application logic.
- Chroma handles metadata alongside vectors, reducing query complexity.

**Trade-offs**:
- Chroma's persistence is file-based (not ACID-compliant for Phase 1).
- Harder to scale Chroma horizontally (but sufficient for Phase 1).
- PostgreSQL+pgvector would be more production-ready from the start, but adds operational complexity.

**Evolution Path**: Phase 2 introduces PostgreSQL for evaluation tracking; Phase 5 migrates vectors to PostgreSQL for multi-node deployment.

---

### Decision 2: Why sentence-transformers (all-MiniLM-L6-v2) Over Larger Models?

**Choice**: `all-MiniLM-L6-v2` (22MB, 384-dim) for Phase 1

**Alternatives Considered**:
- `all-mpnet-base-v2` (420MB, larger but slower)
- OpenAI embeddings API (requires API key, costs money)
- Hugging Face transformers with larger models (slower inference)

**Rationale**:
- Small enough to download and run locally without GPU.
- Fast inference (can embed a query in <50ms on CPU).
- Pre-trained on diverse domains; performs well on esoteric topics.
- Widely used in production; stable and battle-tested.
- Output is 384-dim; efficient for Chroma storage.

**Trade-offs**:
- Smaller than `all-mpnet-base-v2`; may miss some semantic nuance.
- No fine-tuning for esoteric terminology (Phase 2 could add domain-specific fine-tuning).

**Evolution Path**: Phase 2 could evaluate alternative embeddings and potentially fine-tune on curated examples if needed.

---

### Decision 3: Why Ollama + Llama Local LLM?

**Choice**: Ollama with Llama 2/3 (7B–13B) for Phase 1

**Alternatives Considered**:
- OpenAI GPT-4 or GPT-3.5 (best quality, but requires API key, subscription)
- Open-source models via Hugging Face Transformers (works, but more manual setup)
- Anthropic Claude API (excellent, but commercial)

**Rationale**:
- No subscription or API keys required.
- Full privacy: all data stays on developer's machine.
- Ollama provides simple UI for model management (download, run, stop).
- Llama 2/3 are strong open models; competitive with commercial APIs for grounded QA.
- Easy to experiment with different model sizes (7B vs. 13B) without changing code.

**Trade-offs**:
- Llama may produce slightly lower quality answers than GPT-4 or Claude.
- Requires more compute resources (needs 4–8GB RAM; GPU optional but helpful).
- Initial model download is large (~4GB for 7B, ~13GB for 13B).

**Evolution Path**: Phase 2 could add option to use OpenAI API for production. Phase 3 could support multiple LLM backends via abstraction layer.

---

### Decision 4: Why Recursive Chunking with Overlap?

**Choice**: LangChain's RecursiveCharacterTextSplitter with 256 tokens and 50% overlap

**Alternatives Considered**:
- Fixed-size token chunking (no semantic awareness).
- Sliding window chunking (similar to recursive, but less flexible).
- Sentence-level chunking (loses context, too fragmented).
- Paragraph-level chunking (loses granularity).

**Rationale**:
- Recursive splitting respects document structure (splits on sentences first, then words if needed).
- 256 tokens (~1000 characters) is large enough to preserve context, small enough for precise retrieval.
- 50% overlap ensures concepts at chunk boundaries are visible in multiple chunks.
- Example: If a concept is mentioned at the end of chunk 1 and beginning of chunk 2, both chunks will be retrieved if concept is queried.

**Trade-offs**:
- More overlap → larger index (storage cost).
- 50% overlap means each unique token appears in ~1.5 chunks on average.
- Too little overlap (e.g., 0%) → relevant passages may be split across chunks and missed in retrieval.
- Too much overlap (e.g., 80%) → redundant retrieval and slower search.

**Evolution Path**: Phase 1 testing will determine if 256 tokens and 50% overlap are optimal. Can adjust based on retrieval quality.

---

### Decision 5: Why Phase 1 is Text-Only (No Web, No Voice)?

**Choice**: Restrict Phase 1 to book-based QA only

**Rationale**:
- Web search adds complexity: source vetting, deduplication, conflicting info.
- Voice output adds latency and requires TTS infrastructure.
- Focusing on books proves core value quickly.
- Books are curated; easier to ensure citation accuracy.
- Foundation is stable before adding layers.

**Trade-offs**:
- Users can't ask about current events or information outside curated books.
- No voice interface for accessibility (addressed in Phase 4).

**Evolution Path**: Phase 3 adds web search; Phase 4 adds voice and avatar.

---

### Decision 6: Open-Source Stack Over Proprietary?

**Choice**: Prioritize open-source tools (Python, FastAPI, Llama, Chroma, etc.)

**Rationale**:
- No vendor lock-in; full control over code and data.
- Easier to debug and customize.
- Community support and transparency.
- Lower cost (no subscription to API providers in Phase 1).
- Educational value: learn how systems work under the hood.

**Trade-offs**:
- More operational responsibility (versus managed services).
- May need more infrastructure setup.
- Commercial alternatives (OpenAI, Anthropic) might offer better quality answers.

**Evolution Path**: Phase 3+ can integrate commercial APIs as optional upgrades (e.g., OpenAI for better LLM, Brave for web search).

---

## Evolution and Next Steps

### Tracking Changes

All architecture changes, decisions, and learnings are documented in:
- **[PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md)**: Detailed log of every phase transition, design modifications, and lessons learned.
- **[DECISIONS.md](DECISIONS.md)**: Design decisions with trade-offs and rationale.

### Phase 1 → Phase 2

Once Phase 1 is tested and working:
1. Evaluate answer quality and citation accuracy on 20–30 curated questions.
2. Identify failure cases: Where does the system hallucinate? Where are citations weak?
3. Implement Phase 2 improvements: stronger prompt templates, refusal logic, evaluation framework.
4. Re-evaluate on same question set; measure improvement.

### Beyond Phase 2

Phases 3–5 introduce web search, audiovisual features, and production-scale infrastructure. Each phase builds on the previous without replacing it.

---

## Summary

The Manly P. Hall AI Bot is designed as a **layered, modular system** that starts simple and grows in complexity as new phases are implemented. **Phase 1** focuses on book-based question answering with a simple architecture: ingest books → embed chunks → retrieve → generate grounded answers. **Subsequent phases** extend this foundation with quality control, web search, voice/avatar, and production infrastructure.

All decisions prioritize **learning and transparency**: use open-source tools, document trade-offs, and track evolution across phases. This enables both strong technical execution and clear demonstration of skills for potential employers or collaborators.

For implementation details and step-by-step instructions, see **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)**.
