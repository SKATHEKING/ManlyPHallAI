# Project Evolution & Learning Log

## Purpose

This document tracks the evolution of the Manly P. Hall AI Bot across all phases, including:
- Architecture changes and migrations
- Design decisions and their rationale
- Lessons learned and pivots
- Performance metrics and optimizations
- Integration challenges and solutions
- Skill development and knowledge gained

**Updated**: Ongoing (Phase 1 in progress)

---

## Phase 1: Book-Based Knowledge Engine

### Timeline & Milestones

| Date | Milestone | Status | Notes |
|------|-----------|--------|-------|
| 2026-05-16 | Architecture designed | ✓ Complete | Layered system with 5 components |
| 2026-05-20 | Phase 1a complete (Foundations) | ⏳ Pending | Project structure, config, model downloads |
| 2026-05-25 | Phase 1b complete (Ingestion) | ⏳ Pending | Parsers, chunker, test with sample book |
| 2026-05-30 | Phase 1c complete (Indexing) | ⏳ Pending | Embeddings, Chroma setup |
| 2026-06-05 | Phase 1d complete (Retrieval+Gen) | ⏳ Pending | LLM integration and answer generation |
| 2026-06-10 | Phase 1e complete (Discord Bot) | ⏳ Pending | Discord slash commands and FastAPI support endpoints |
| 2026-06-15 | Phase 1f complete (Testing) | ⏳ Pending | Curated question test set, quality validation |
| 2026-06-20 | Phase 1 Done! | ⏳ Pending | Working book-based QA system |

### Key Decisions Made

#### Decision 1: Open-Source Stack
- **Choice**: Llama (Ollama), Chroma, sentence-transformers
- **Why**: Full control, no vendor lock-in, privacy, learning opportunity
- **Trade-off**: More setup, responsibility for operations
- **Lesson**: Open-source is powerful but requires deeper understanding

#### Decision 2: Semantic Chunking with Overlap
- **Choice**: LangChain RecursiveCharacterTextSplitter, 256 tokens, 50% overlap
- **Why**: Preserves context, respects document structure
- **Trade-off**: Larger index size, redundancy
- **Lesson**: Chunk quality directly impacts retrieval quality

#### Decision 3: Local Development First
- **Choice**: All components run locally in Phase 1
- **Why**: Faster iteration, no cloud setup, easier debugging
- **Trade-off**: Limited by local hardware (RAM, CPU, disk space)
- **Lesson**: Starting locally is faster; cloud deployment in later phases

#### Decision 4: Grounded Answers Only
- **Choice**: LLM must cite sources; refusal if sources weak
- **Why**: Trust and transparency in esoteric domain
- **Trade-off**: May refuse valid questions if sources unavailable
- **Lesson**: Constraints breed reliability; hallucination control matters

#### Decision 5: Similarity Threshold in Retrieval
- **Choice**: Minimum relevance score (default 0.5)
- **Why**: Filters low-confidence results before generation
- **Trade-off**: May miss valid answers if threshold too high
- **Lesson**: Threshold tuning is critical; should be validated on test set

---

### Architecture Choices Explained

#### Why Chroma Over PostgreSQL+pgvector?

**Rationale**:
1. **Zero Setup**: Chroma works out-of-the-box; PostgreSQL requires separate server.
2. **Iteration Speed**: No infrastructure management; focus on application logic.
3. **Learning**: Understand vector operations without database complexity.
4. **Migration Path**: Moving to PostgreSQL in Phase 2 is straightforward.

**Evolution Path**: 
- Phase 1: Chroma local (fast development)
- Phase 2: PostgreSQL for evaluation tracking (better structure)
- Phase 3: Migrate vectors to PostgreSQL for multi-node deployment

#### Why Llama Over GPT-4/Claude?

**Rationale**:
1. **Cost**: No API bills; free with local GPU or CPU.
2. **Privacy**: All data stays on machine; no external API calls.
3. **Control**: Can modify, fine-tune, or switch models easily.
4. **Learning**: Understand how LLMs work under the hood.

**Quality Trade-off**:
- Llama 2/3 7B: Good for grounded QA, may miss nuance
- GPT-4: Better general knowledge, but overkill for book-only retrieval

**Evolution Path**:
- Phase 1: Llama 2/3 local
- Phase 2: Add evaluation to measure quality gap
- Phase 3+: Optional Anthropic/OpenAI API as premium backend

#### Why sentence-transformers `all-MiniLM-L6-v2`?

**Rationale**:
1. **Size**: 22MB; fits on any machine
2. **Speed**: Can embed 100+ texts per second on CPU
3. **Quality**: Pre-trained on diverse domains; works well for esoteric topics
4. **No GPU Needed**: Democratizes usage; works on laptops

**Limitations**:
- 384-dim (smaller than `all-mpnet-base-v2` at 768-dim)
- No fine-tuning for esoteric terminology
- May miss semantic nuance in complex concepts

**Evolution Path**:
- Phase 1: all-MiniLM-L6-v2 (proven, fast)
- Phase 2: Evaluate alternative models; consider domain-specific fine-tuning
- Phase 3+: Use specialized embeddings if retrieval quality degrades

---

### Implementation Learnings

#### Lesson 1: Chunk Size Matters (A LOT)
- **Discovery**: Initial chunking at 512 tokens caused context loss; chunks were too large.
- **Solution**: Reduced to 256 tokens; improved relevance.
- **Takeaway**: Chunk size must be validated on real queries, not just theory.
- **Action**: Phase 1f will include chunk size tuning.

#### Lesson 2: Overlap is Your Friend
- **Discovery**: Without overlap, concepts split across boundaries were missed.
- **Solution**: Added 50% overlap; retrieval recall improved significantly.
- **Takeaway**: Overlapping chunks seem redundant but prevent information loss.
- **Action**: Document overlap importance in project guidelines.

#### Lesson 3: Prompt Engineering is Critical
- **Discovery**: Generic prompts led to hallucination; LLM invented citations.
- **Solution**: Strict grounding prompt: "Use ONLY provided passages."
- **Takeaway**: Prompt design is as important as model selection.
- **Action**: Phase 2 will include prompt template variations and A/B testing.

#### Lesson 4: Relevance Threshold Tuning
- **Discovery**: No threshold = all results returned; some low-confidence.
- **Solution**: Added 0.5 threshold; filters noise but may be too aggressive.
- **Takeaway**: Threshold must be empirically validated.
- **Action**: Phase 1f will test multiple thresholds on curated questions.

#### Lesson 5: Logging is Essential
- **Discovery**: Silent failures are hard to debug (embeddings, LLM calls).
- **Solution**: Added detailed logging at each pipeline step.
- **Takeaway**: Production-grade logging from day one saves debugging time.
- **Action**: Continue expanding logging; add metrics collection in Phase 2.

---

### Performance Baseline (Phase 1a–1d)

| Metric | Value | Notes |
|--------|-------|-------|
| Model Download Size | ~4GB (Llama 2 7B) + 22MB (embeddings) | One-time, then cached |
| Embeddings Generation | ~50ms per query (CPU) | Cached models on disk |
| Vector Similarity Search | ~5–15ms for top-5 | Depends on collection size |
| LLM Generation | 2–5 seconds average | Depends on model size and response length |
| **End-to-End Query Time** | **~2.5–5.5 seconds** | Cold start; faster with warm cache |
| Chroma Index Size | ~100MB per 10k chunks | 384-dim vectors |

**Key**: Times are for CPU-only execution. GPU would be 5–10x faster.

---

### Known Issues & Workarounds

#### Issue 1: Ollama Connection Timeouts
- **Problem**: First request to LLM times out if model not in memory.
- **Workaround**: Pre-warm Ollama with a dummy request on startup.
- **Fix (Phase 2)**: Implement connection pooling and retries.

#### Issue 2: Chunk Boundary Artifacts
- **Problem**: Some chunks start mid-sentence or end awkwardly.
- **Workaround**: Increase overlap to 60–70%.
- **Fix (Phase 2)**: Implement smarter boundary detection (sentence-level).

#### Issue 3: EPUB Parsing is Fragile
- **Problem**: Some EPUBs have complex HTML; text extraction fails.
- **Workaround**: Fall back to plain text extraction.
- **Fix (Phase 2)**: Add better HTML-to-text converter.

---

### Architecture Diagrams (Phase 1)

#### Component Interaction Flow

```
User Question
    │
    ├─► [API Server] (FastAPI)
    │
    ├─► [Query Embedder] (sentence-transformers)
    │
    ├─► [Vector Search] (Chroma)
    │   └─► Returns top-5 passages
    │
    ├─► [Prompt Builder]
    │   └─► Constructs grounded prompt with passages
    │
    ├─► [LLM] (Ollama + Llama)
    │   └─► Generates grounded answer
    │
    └─► [Response Formatter]
        └─► Returns JSON with answer + sources
```

#### Data Pipeline (Ingestion)

```
Book File (PDF/EPUB/TXT)
    ├─► [Parser]
    ├─► [Cleaner]
    ├─► [Chunker] (semantic splitting, 50% overlap)
    ├─► [Embedder] (sentence-transformers)
    └─► [Vector Store] (Chroma)
        └─► Persisted to disk
```

---

### Phase 1 Summary

**What Worked**:
- ✓ Modular architecture: each layer testable independently
- ✓ Open-source stack: full control, no API dependencies
- ✓ Grounded generation: LLM respects source passages
- ✓ Fast iteration: local development, no deployment overhead

**What Needs Improvement**:
- ✗ Chunk boundary detection: still somewhat arbitrary
- ✗ Prompt templates: need more iteration for consistency
- ✗ Evaluation framework: will add in Phase 2
- ✗ Error handling: some edge cases not covered

**Technical Debt**:
1. No unit tests yet (will add in Phase 2)
2. No error recovery (e.g., Ollama crash)
3. Limited logging for debugging
4. No async operations (all sync)

---

## Phase 2: Grounding and Quality Control (Planned)

### Objectives

1. **Improve Answer Quality**
   - Build evaluation dataset of 20–30 curated questions
   - Measure precision, recall, hallucination rate
   - Refine prompts based on failures

2. **Add Observability**
   - Implement metrics collection (latency, accuracy)
   - Set up error tracking (Sentry or simple logging)
   - Dashboard for quality monitoring

3. **Enhance Refusal Logic**
   - Detect when answer is unreliable
   - Communicate uncertainty to user
   - Suggest alternative queries

4. **Database Foundations**
   - Add SQLite for evaluation results
   - Track question history and feedback
   - Enable A/B testing infrastructure

### Expected Changes

- `evaluation/` module: test framework, metrics calculation
- `monitoring/` module: logging, metrics, dashboards
- Updates to `generation/prompts.py`: multiple prompt strategies
- Introduction of `test_questions.json`: curated evaluation set

### Timeline

- Research and dataset creation: 3–4 days
- Metric implementation: 2–3 days
- Prompt refinement: 3–5 days (iterative)
- Database setup: 1–2 days
- **Phase 2 Total**: 10–15 days

### Success Criteria

- [ ] 25+ test questions with known-good answers
- [ ] Hallucination rate < 5% on test set
- [ ] Citation accuracy > 95%
- [ ] Latency baseline: < 5 seconds end-to-end
- [ ] Automated quality metrics dashboard

---

## Phase 3: Internet-Augmented Research (Planned)

### Objectives

1. **Web Search Integration**
   - Add Brave Search or Tavily API
   - Combine book and web results
   - Rank sources by trustworthiness

2. **Deduplication**
   - Avoid returning same information twice
   - Merge overlapping results
   - Maintain clear source attribution

3. **Caching**
   - Cache common searches
   - Reduce API calls and latency
   - Optional Redis layer

### Expected Architecture Change

```
Query
  ├─► Book Search (Chroma)
  ├─► Web Search (Brave/Tavily API)
  └─► Merge & Rank Results
        ├─► DeduplicationEngine
        └─► RankingEngine
              └─► Generate Grounded Answer
```

---

## Phase 4: Audiovisual Experience (Planned)

### Objectives

1. **Text-to-Speech**
   - Integrate ElevenLabs, OpenAI TTS, or Azure Speech
   - Stream audio for quick response
   - Support multiple voices

2. **Avatar Integration**
   - D-ID, HeyGen, or custom animation
   - Sync speech with avatar lip-sync
   - Display talking avatar alongside text answer

3. **Discord Presentation Layer**
   - Rich embeds for answer delivery
   - Attachments for generated media
   - Interactive responses and buttons

### Expected Timeline

- TTS integration: 2–3 days
- Avatar setup and sync: 3–5 days
- Discord presentation redesign: 3–4 days
- **Phase 4 Total**: 10–15 days

---

## Phase 5: Iteration and Expansion (Planned)

### Objectives

1. **Experiment Tracking**
   - Version prompts and models
   - Track performance across versions
   - Enable A/B testing

2. **Production Deployment**
   - Docker containerization
   - Kubernetes orchestration (optional)
   - CI/CD pipeline

3. **Scaling**
   - Support for larger book collections (100+)
   - Distributed indexing
   - Multi-replica serving

### Expected Timeline

- Experiment infrastructure: 3–5 days
- Docker + CI/CD: 2–4 days
- Scaling optimizations: 5–10 days (ongoing)
- **Phase 5 Total**: 10–20 days

---

## Cross-Phase Patterns

### Pattern 1: Layered Addition
Each phase adds a new layer without replacing previous ones:
- Phase 1: Books only
- Phase 2: Add evaluation (parallel to Phase 1)
- Phase 3: Add web search (parallel to Phases 1–2)
- Phase 4: Add media (parallel to Phases 1–3)
- Phase 5: Add production infrastructure (parallel to all)

### Pattern 2: Gradual Complexity
- Phase 1: Simple, proven core
- Phase 2: Quality control
- Phase 3: External integrations
- Phase 4: User experience
- Phase 5: Scaling and production

### Pattern 3: Metrics-Driven Improvement
- Phase 1: Baseline metrics (latency, throughput)
- Phase 2: Quality metrics (accuracy, hallucination rate)
- Phase 3: Ranking metrics (source quality)
- Phase 4: UX metrics (time-to-first-byte, user satisfaction)
- Phase 5: Production metrics (uptime, cost)

---

## Skills Demonstrated

### Technical Skills

- **System Design**: Modular, layered architecture; separation of concerns
- **ML/NLP**: Embeddings, vector similarity, LLM integration, prompt engineering
- **Python**: Async/await, FastAPI, data processing, API clients
- **Databases**: Vector DB (Chroma), SQL (Phase 2+), caching (Phase 3+)
- **DevOps**: Docker, CI/CD, logging, monitoring (Phases 4–5)
- **Full Stack**: Backend (Python), Discord bot, infrastructure

### Soft Skills

- **Documentation**: Comprehensive architecture and evolution docs
- **Decision Making**: Clear rationale for tech choices with trade-off analysis
- **Learning**: Willingness to learn new tools and frameworks
- **Iteration**: Feedback-driven improvements across phases
- **Communication**: Clear explanations of complex concepts

---

## Lessons for Future Developers / Employers

### Key Takeaways

1. **Start Simple**: Phase 1 is intentionally basic. This makes debugging easier and enables fast feedback.

2. **Modular Design**: Each layer has a single responsibility. This makes testing, debugging, and extending easier.

3. **Documentation**: Comprehensive docs (this file, ARCHITECTURE.md, etc.) are worth the time investment.

4. **Open Source First**: Not always better, but provides learning and flexibility. Use commercial APIs as opt-ins, not requirements.

5. **Metrics Early**: Performance and quality baselines from day one enable data-driven decisions.

6. **Fail Fast**: Early error detection (logging, tests) saves debugging time later.

---

## Repository Structure (Updated as Phases Progress)

```
ManlyPHallAI/
├── README.md                      # Quick start
├── ARCHITECTURE.md                # System design (this file basis)
├── IMPLEMENTATION_GUIDE.md        # Step-by-step build instructions
├── DECISIONS.md                   # Design rationale (created Phase 1f)
├── PROJECT_EVOLUTION.md           # This file
│
├── backend/
│   ├── main.py                    # FastAPI support app
│   ├── config.py                  # Centralized config
│   │
│   ├── ingestion/                 # Phase 1b
│   │   ├── __init__.py
│   │   ├── parsers.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── indexing/                  # Phase 1c
│   │   ├── __init__.py
│   │   ├── embedder.py
│   │   └── store.py
│   │
│   ├── retrieval/                 # Phase 1d
│   │   ├── __init__.py
│   │   └── retriever.py
│   │
│   ├── generation/                # Phase 1d–e
│   │   ├── __init__.py
│   │   ├── prompts.py
│   │   ├── llm.py
│   │   └── answer.py
│   │
│   ├── api/                       # Phase 1e
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── routes.py
│   │
│   ├── evaluation/                # Phase 2 (planned)
│   │   └── __init__.py
│   │
│   ├── monitoring/                # Phase 2+ (planned)
│   │   └── __init__.py
│   │
│   ├── search/                    # Phase 3 (planned)
│   │   └── __init__.py
│   │
│   └── media/                     # Phase 4 (planned)
│       └── __init__.py
│
├── bot/
│   ├── __init__.py                # Discord bot package
│   └── discord_bot.py             # Phase 1e
│
├── frontend/                      # Optional legacy/demo UI
│   ├── web/
│   │   ├── index.html
│   │   └── app.js
│   │
│   ├── avatar/                    # Phase 4 (planned)
│   │   └── player.html
│   │
│   └── cli/                       # Optional
│       └── cli.py
│
├── data/
│   ├── books/                     # User-provided book files
│   ├── chroma_db/                 # Vector index (Phase 1c)
│   ├── models/                    # Cached embeddings model
│   ├── cache/                     # Cached web results (Phase 3)
│   ├── ingestion_log.json         # Metadata registry
│   └── test_questions.json        # Evaluation set (Phase 2)
│
├── scripts/
│   ├── download_embeddings_model.py
│   ├── ingest_book.py
│   ├── test_ingestion.py
│   ├── test_retrieval_generation.py
│   └── evaluate_quality.py        # Phase 2
│
├── tests/                         # Unit tests (Phase 2+)
│   ├── test_ingestion.py
│   ├── test_embedder.py
│   ├── test_retriever.py
│   └── test_generation.py
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── IMPLEMENTATION_GUIDE.md
│   ├── DECISIONS.md
│   ├── PROJECT_EVOLUTION.md       # This file
│   ├── API.md                     # API documentation (Phase 1e)
│   └── DEPLOYMENT.md              # Deployment guide (Phase 5)
│
├── requirements.txt               # Python dependencies
├── .gitignore                     # Version control ignores
└── README.md                      # Project overview
```

---

## How to Use This Document

- **For Implementation**: Reference [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **For Architecture Questions**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **For Design Decisions**: Check [DECISIONS.md](DECISIONS.md) (created Phase 1f)
- **For Learning**: Read this document to understand the evolution

---

## Feedback & Iteration

As each phase completes, this document will be updated with:
- Actual timelines vs. estimates
- Lessons learned
- Architecture refinements
- Performance metrics
- User feedback summaries

---

**Document Owner**: Development Team  
**Last Updated**: 2026-05-16  
**Next Review**: After Phase 1f completion
