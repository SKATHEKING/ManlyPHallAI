# Manly P. Hall AI Bot

A domain-specific AI assistant for esoteric knowledge, grounded in curated book sources with a clear evolution toward audiovisual presentation.

**Status**: Phase 1 (Book-Based Knowledge Engine) — Architecture & Implementation Guide Complete

---

## 📖 Documentation Hub

**Start here** to understand the project:

| Document | Purpose | Audience |
|----------|---------|----------|
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | System design, component interactions, all phases | Architects, developers, reviewers |
| **[IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)** | Step-by-step build instructions for Phase 1 | Developers, implementers |
| **[DECISIONS.md](DECISIONS.md)** | Design rationale, trade-offs, reversibility analysis | Decision-makers, evaluators |
| **[PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md)** | Learning log, phase transitions, metrics | Everyone (track progress & lessons) |
| **[technologies.md](technologies.md)** | Technology stack by phase | Tech evaluators |
| **[resources.md](resources.md)** | Links and references for learning | Developers |

**Quick Navigation**:
- 🏗️ **Want to understand the system?** → Read [ARCHITECTURE.md](ARCHITECTURE.md)
- 🛠️ **Ready to build Phase 1?** → Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- 🤔 **Curious about "why" these choices?** → Check [DECISIONS.md](DECISIONS.md)
- 📊 **Tracking progress and learnings?** → See [PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md)

---

## Project Overview

### Intent

Build a specialized AI assistant that:
- Answers questions about Manly P. Hall, esotericism, occult philosophy, symbolism, and mysticism
- **Grounds every answer** in curated book sources with explicit citations
- Evolves from text-only (Phase 1) → voice/avatar (Phase 4) → production-scale (Phase 5)
- Prioritizes **quality over breadth**: domain-focused, curated sources, reduced hallucination

### Why This Matters

1. **Domain Focus**: Narrow scope → better quality → faster iteration → proven value
2. **Transparency**: Every answer cites sources → builds trust in esoteric domain
3. **Learning Opportunity**: Full stack (ingestion → embedding → retrieval → generation → API) showcases skills
4. **Skill Showcase**: Demonstrates ML/NLP, backend architecture, decision-making, documentation

---

## Phase Overview

### Phase 1: Book-Based Knowledge Engine ✍️ **[IN PROGRESS]**

**Objective**: Build a text-based Q&A system grounded in books.

**What's included**:
- Book parsing (PDF, EPUB, TXT)
- Semantic text chunking with overlap
- Vector embeddings and retrieval (Chroma + sentence-transformers)
- LLM-based answer generation (Ollama + Llama 2/3)
- FastAPI REST server
- Simple web UI

**Tech Stack**: Python, FastAPI, LangChain, Chroma, Ollama, sentence-transformers

**Timeline**: 8–12 days of focused development

**Status**:
- ✓ Architecture designed
- ✓ Implementation guide written
- ⏳ Code modules to be implemented (Phase 1a–1f)

### Phase 2: Grounding and Quality Control (Planned)

Add evaluation framework, refine prompts, measure hallucination rate.

### Phase 3: Internet-Augmented Research (Planned)

Add web search (Brave, Tavily), combine book + web sources.

### Phase 4: Audiovisual Experience (Planned)

Add text-to-speech + avatar (ElevenLabs, D-ID).

### Phase 5: Iteration and Expansion (Planned)

Production deployment, scaling, A/B testing infrastructure.

---

## Quick Start (Phase 1)

### Prerequisites

- Python 3.10+
- ~10GB free disk space
- Ollama (for local LLM)
- Git

### Setup (5 minutes)

```bash
# 1. Clone and navigate
cd ManlyPHallAI

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Download models (one-time, ~5 min)
python scripts/download_embeddings_model.py

# 5. Start Ollama (separate terminal)
ollama serve
ollama pull llama2:7b

# 6. Run API server
python backend/main.py

# 7. Open browser
open http://localhost:8000
```

### Ingest a Book

```bash
python scripts/ingest_book.py data/books/my_book.pdf --title "My Book" --author "Author Name"
```

### Ask a Question

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Freemasonry?"}'
```

**Full details**: See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

---

## Project Structure

```
ManlyPHallAI/
├── docs/
│   ├── ARCHITECTURE.md           ← System design
│   ├── IMPLEMENTATION_GUIDE.md   ← Build instructions
│   ├── DECISIONS.md              ← Trade-off analysis
│   └── PROJECT_EVOLUTION.md      ← Learning log
│
├── backend/
│   ├── main.py                   # FastAPI app
│   ├── config.py                 # Centralized config
│   ├── ingestion/                # Parse books
│   ├── indexing/                 # Embeddings + vector store
│   ├── retrieval/                # Vector search
│   ├── generation/               # LLM answer generation
│   └── api/                      # REST endpoints
│
├── frontend/
│   ├── web/                      # HTML/JS chat UI
│   └── cli/                      # Command-line interface
│
├── data/
│   ├── books/                    # User-provided book files
│   ├── chroma_db/                # Vector index
│   └── models/                   # Cached embeddings model
│
├── scripts/
│   ├── ingest_book.py            # Ingestion pipeline
│   └── test_*.py                 # Tests
│
└── requirements.txt              # Dependencies
```

---

## Key Design Decisions (Summary)

| Decision | Choice | Why? | Reversibility |
|----------|--------|------|---------------|
| **Architecture** | Layered monolith | Simple, fast iteration | HIGH |
| **Vector DB** | Chroma → PostgreSQL | Local dev, then scale | HIGH |
| **Embeddings** | sentence-transformers (all-MiniLM-L6-v2) | Fast, lightweight, no GPU needed | HIGH |
| **LLM** | Ollama + Llama 2/3 (local) | Free, private, full control | HIGH |
| **Framework** | FastAPI | Modern, async-ready, great DX | HIGH |
| **Language** | Python | Best ML ecosystem | MEDIUM |
| **Scope (Phase 1)** | Books only, no web | Prove core value first | HIGH |

See [DECISIONS.md](DECISIONS.md) for detailed rationale and trade-offs.

---

## Development Workflow

### Phase 1a–1f: Implementation

Following [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md):

1. **1a (Foundations)**: Setup, config, model downloads — 1–2 days
2. **1b (Ingestion)**: Parsers, chunker, test — 2–3 days
3. **1c (Indexing)**: Embeddings, Chroma setup — 1–2 days
4. **1d (Retrieval + Gen)**: LLM integration — 2–3 days
5. **1e (API)**: FastAPI endpoints, frontend — 1–2 days
6. **1f (Testing)**: Curated questions, quality validation — 1–2 days

**Track progress** in [PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md).

### Evaluation Criteria (Phase 1)

- ✓ Book successfully ingested and indexed
- ✓ Queries retrieve relevant passages
- ✓ LLM generates grounded answers with citations
- ✓ API responds within 5 seconds end-to-end
- ✓ Frontend works and sends/receives correctly
- ✓ Citation accuracy > 95% on test set

---

## Skills Demonstrated

### Technical

- **System Architecture**: Modular, layered design; separation of concerns
- **ML/NLP**: Embeddings, vector search, LLM integration, prompt engineering
- **Python Backend**: FastAPI, async/await, REST APIs
- **Databases**: Vector DB (Chroma), SQL (Phase 2), caching (Phase 3)
- **DevOps**: Containerization (Phase 5), CI/CD (Phase 5)
- **Full Stack**: Backend, frontend, infrastructure

### Soft

- **Documentation**: Comprehensive architecture, implementation, evolution docs
- **Decision-Making**: Trade-off analysis, reversibility assessment
- **Learning**: Willingness to learn new tools and frameworks
- **Project Management**: Phased development, clear milestones, progress tracking

---

## Lessons & Insights

See [PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md) for ongoing learnings.

### Phase 1 Key Insights

1. **Chunk size matters**: Too large → context loss; too small → noise. 256 tokens + 50% overlap is balanced.
2. **Grounding is king**: Simple constraint ("use only provided passages") dramatically reduces hallucination.
3. **Local-first development**: Faster iteration than cloud; no infrastructure overhead.
4. **Threshold tuning**: Relevance threshold filters noise before LLM sees it; improves quality.
5. **Documentation ROI**: Comprehensive docs save debugging time and showcase skills.

---

## Technology Stack

### Phase 1

- **Language**: Python 3.10+
- **Web**: FastAPI, Uvicorn
- **ML**: sentence-transformers, Ollama (Llama 2/3)
- **Data**: LangChain (chunking), Chroma (vectors), JSON (metadata)
- **Dev**: pytest, Python logging, Click/Typer

### Phase 2+

- **Evaluation**: pytest, custom metrics
- **Database**: PostgreSQL + pgvector (metadata)
- **Web Search**: Brave Search API or Tavily
- **TTS/Avatar**: ElevenLabs, D-ID (Phase 4)
- **Infrastructure**: Docker, Kubernetes (Phase 5)

---

## Running Tests

```bash
# Phase 1 ingestion test
python scripts/test_ingestion.py

# Phase 1 retrieval + generation test (after ingestion)
python scripts/test_retrieval_generation.py
```

---

## Contributing / Future Development

- Fork or clone this repository
- Follow [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) for Phase 1
- Update [PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md) with learnings
- Reference [DECISIONS.md](DECISIONS.md) for design pattern
- Document new decisions before implementing

---

## FAQ

**Q: Why Python and not JavaScript/Rust/Go?**  
A: Python dominates ML/NLP. Ecosystem (FastAPI, transformers, LangChain) is unmatched. See [DECISIONS.md](DECISIONS.md#decision-t1-python-as-primary-language).

**Q: Why local Llama and not GPT-4?**  
A: Phase 1 prioritizes learning and cost. Local Llama is free and private. Phase 2+ adds OpenAI option. See [DECISIONS.md](DECISIONS.md#decision-t5-ollama--llama-23-for-llm).

**Q: Will this work on a laptop (no GPU)?**  
A: Yes! all-MiniLM embeddings run on CPU. Llama 7B is slower on CPU but workable. GPU speeds up inference 5–10x.

**Q: How do I add my own books?**  
A: `python scripts/ingest_book.py /path/to/book.pdf` after server is running.

**Q: What's the expected answer quality?**  
A: Phase 1 is MVP; quality validated in Phase 2. Expect 80–90% accuracy on test set; 5–10% hallucination rate.

---

## Resources

- [ARCHITECTURE.md](ARCHITECTURE.md) — Deep dive into system design
- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) — Step-by-step build instructions
- [technologies.md](technologies.md) — Tech stack by phase
- [resources.md](resources.md) — Learning links (FastAPI, LLMs, embeddings, etc.)
- [PROJECT_EVOLUTION.md](PROJECT_EVOLUTION.md) — Learning log and phase updates

---

## License

Educational project. Free to use, modify, and distribute for learning purposes.

---

## Contact

Questions? See documentation files above; they cover most use cases.

Add speech and visual presentation to make the assistant more engaging.

Key work:

- Integrate text-to-speech.
- Add playback handling and timing.
- Introduce a talking image or avatar.
- Sync speech with visual output.

Outcome:

- A conversational audiovisual assistant that can speak and present itself visually.

### Phase 5: Iteration and Expansion

Refine the system through real usage.

Key work:

- Expand the source library.
- Improve retrieval accuracy.
- Tune latency and response flow.
- Add better evaluation and logging.
- Extend the knowledge base carefully over time.

Outcome:

- A stable, growing product that can evolve without losing quality.

## Implementation Plan

### Step 1: Define the source scope

Choose the first set of books and topics. Keep the initial scope intentionally narrow so the system can be tested quickly and improved in focused iterations.

### Step 2: Prepare the knowledge base

Convert source material into clean text, preserve metadata, and organize it so the assistant can retrieve relevant passages efficiently.

### Step 3: Build retrieval first

Use embeddings and search to find the most relevant excerpts for each question. The quality of retrieval will determine the quality of the answers.

### Step 4: Generate grounded responses

Have the model answer only from retrieved content. If the material does not support a clear answer, the bot should say so.

### Step 5: Add evaluation loops

Test with real questions, compare outputs against expected answers, and refine the system based on observed failures.

### Step 6: Introduce web sources

Add internet research only after the book-based workflow is stable. Keep the source selection controlled and explicit.

### Step 7: Add voice and avatar

Once the knowledge layer is trustworthy, add speech and the visual layer to create the audiovisual experience.

## Success Criteria

The project will be considered successful when it can:

- Answer questions accurately from books.
- Clearly cite source material.
- Distinguish between supported and unsupported claims.
- Expand to internet-based research without losing reliability.
- Deliver a polished audiovisual experience.

## Suggested Tech Stack

This can be implemented with a practical, modern stack such as:

- Frontend: Next.js or React
- Backend: Python with FastAPI or Node.js
- Retrieval: embeddings plus a vector database
- Storage: PostgreSQL and object storage
- LLM layer: a hosted model provider or selected open model
- Audio: text-to-speech service
- Avatar: a talking image or avatar provider

## Notes on Sources and Responsibility

Because this project is centered on books and online information, source selection matters. The assistant should prioritize legally usable, high-quality material and should make source provenance visible where possible.

It is also important to treat the subject matter with care. The bot should support inquiry and study, not claim authority beyond its sources.

## Next Steps

1. Finalize the first source list.
2. Define the first MVP question set.
3. Build book ingestion and retrieval.
4. Add citation-based answering.
5. Expand into web, voice, and avatar once the core loop is reliable.
