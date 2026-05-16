# Design Decisions & Trade-Off Analysis

## Purpose

This document provides detailed rationale for every major architectural and technical decision in the Manly P. Hall AI Bot project. Each decision includes:
- **Problem**: What issue required a decision?
- **Options Considered**: Alternatives and their trade-offs
- **Decision**: What was chosen?
- **Rationale**: Why?
- **Implications**: What are the downstream effects?
- **Reversibility**: How hard is it to change later?

**Audience**: Developers, architects, future maintainers, and skill evaluators.

---

## Table of Contents

1. [Architecture-Level Decisions](#architecture-level-decisions)
2. [Technology Stack Decisions](#technology-stack-decisions)
3. [Phase 1 Specific Decisions](#phase-1-specific-decisions)
4. [Future Decisions (Phases 2–5)](#future-decisions-phases-2–5)

---

## Architecture-Level Decisions

### Decision A1: Layered, Modular Architecture

**Problem**: How should we organize the system to enable independent development, testing, and iteration?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Monolithic (chosen)** | Simple, easy to debug, fast iteration | Hard to scale, tight coupling |
| **2. Microservices** | Scalable, independent deployment | Operational complexity, network latency |
| **3. Serverless** | Auto-scaling, pay-per-use | Cold start latency, limited local testing |

**Decision**: Layered monolith in Phase 1, with clear separation into potential microservices in Phase 5.

**Rationale**:
1. **Phase 1 Focus**: Validate core value before adding infrastructure complexity.
2. **Developer Experience**: Monolith easier to debug and profile than distributed system.
3. **Migration Path**: Layers are independent; can extract to services later.
4. **Learning**: Developers understand full system without debugging distributed issues.

**Implications**:
- Simpler local development
- Faster iteration
- Limited by single-machine resources
- Easy to refactor into services later

**Reversibility**: HIGH
- Clear layer boundaries enable straightforward microservice extraction.
- Phases 4–5 plan for this evolution.

---

### Decision A2: Synchronous Processing in Phase 1

**Problem**: Should request handling be synchronous or asynchronous?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Sync (chosen for Phase 1)** | Simpler code, easier debugging | Slower for concurrent users |
| **2. Async** | Better throughput, scalable | Complex concurrency bugs, harder to debug |

**Decision**: Synchronous in Phase 1; migrate to async in Phase 4 if needed.

**Rationale**:
1. **Phase 1 Use Case**: Single developer testing; no concurrent users.
2. **Simplicity**: Sync code is easier to reason about and debug.
3. **Sufficient Performance**: ~3–5 second latency is acceptable for MVP.
4. **Clear Migration Path**: Can add async/await and task queues later.

**Implications**:
- Linear request handling
- Only one query processed at a time
- Won't bottleneck for Phase 1 testing
- Must add threading/async for production

**Reversibility**: HIGH
- FastAPI supports both sync and async handlers.
- Can migrate incrementally.
- No blocking tech choice.

---

### Decision A3: Local-First Development, Cloud-Later Deployment

**Problem**: Should we build for local development or cloud deployment first?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Local-first (chosen)** | Fast iteration, no infra setup | Limited scalability, not production-ready |
| **2. Cloud-first** | Production-ready from start | Complex setup, slower iteration, higher costs |

**Decision**: Local development in Phases 1–3; cloud options in Phase 5.

**Rationale**:
1. **Faster Feedback Loop**: No deployment delays; test changes immediately.
2. **Cost**: Free development; no cloud bills until Phase 5.
3. **Learning**: Understand full system without cloud abstractions.
4. **Portability**: Works on any laptop; reproducible environments.

**Implications**:
- Developers can work offline
- Faster experimentation with models and prompts
- Limited by local hardware (RAM, GPU)
- Deployment readiness delayed to Phase 5

**Reversibility**: HIGH
- All code is portable; can containerize later.
- Cloud services are added, not forced from start.
- Phases 4–5 include containerization and deployment.

---

## Technology Stack Decisions

### Decision T1: Python as Primary Language

**Problem**: Which language best suits ML/NLP backend development?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Python (chosen)** | Largest ML ecosystem, fast dev | Slower runtime, GIL limitations |
| **2. JavaScript/Node.js** | Single language for full stack | Weaker ML libraries, poor ML support |
| **3. Rust** | Fast, safe, excellent perf | Steep learning curve, slower dev |
| **4. Go** | Fast, good concurrency | Smaller ML ecosystem |

**Decision**: Python for backend; Discord.py for the primary user interface.

**Rationale**:
1. **ML Ecosystem**: FastAPI, transformers, Chroma, LangChain all Python-native.
2. **Development Speed**: Python → JavaScript integration is proven.
3. **ML Community**: Most researchers and data scientists use Python.
4. **Libraries**: Best-in-class for NLP: Hugging Face, PyTorch, spaCy.

**Implications**:
- Fast development of ML-heavy components
- Runtime performance not critical in Phase 1 (3–5s latency is acceptable)
- GIL may limit concurrency in Phase 4+
- Deployment requires Python runtime

**Reversibility**: MEDIUM
- Rewriting to Rust or Go is possible but costly.
- Performance bottlenecks identified in Phase 5 could justify rewrite of specific modules.
- No immediate blocker; sufficient for 5+ years of development.

---

### Decision T2: FastAPI as Support API

**Problem**: Which framework for building REST API?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. FastAPI (chosen)** | Modern, async, auto docs, Pydantic | Newer (smaller community than Flask) |
| **2. Flask** | Lightweight, familiar | No async, manual docs, less validation |
| **3. Django** | Feature-rich, batteries-included | Heavyweight, complex setup |
| **4. Tornado** | Async-first, fast | Less popular, fewer extensions |

**Decision**: FastAPI for lightweight support endpoints, health checks, and future admin workflows.

**Rationale**:
1. **Built-in API Documentation**: Automatic Swagger/OpenAPI docs.
2. **Pydantic Validation**: Type hints and automatic validation.
3. **Async Support**: Ready for async operations in Phase 4.
4. **Performance**: Fast enough for Phase 1; can handle 100s of concurrent requests.
5. **Learning**: Modern best practices; valuable skill for interviews.

**Implications**:
- Clean, readable code
- Type safety out of the box
- Easy testing with TestClient
- Migration to other frameworks is straightforward

**Reversibility**: HIGH
- Switching to Flask or Django is doable.
- Support API remains isolated from the Discord bot interface.
- No tech lock-in.

---

### Decision T3: Chroma for Vector Database

**Problem**: Which vector database for storing and retrieving embeddings?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Chroma (chosen)** | Embeddable, zero setup, persistent | Smaller community, less production maturity |
| **2. PostgreSQL+pgvector** | Production-proven, ACID, SQL | Requires separate server, more complex |
| **3. Pinecone (managed)** | Scalable, managed service | Vendor lock-in, API costs, requires internet |
| **4. Weaviate (self-hosted)** | Open-source, scalable | Operational complexity, more setup |
| **5. FAISS** | Fast, offline | Requires rebuilding entire index for updates |

**Decision**: Chroma for Phase 1; PostgreSQL+pgvector for Phase 2+.

**Rationale**:
1. **Phase 1 Simplicity**: No database server setup; works locally out-of-the-box.
2. **Metadata Handling**: Stores vectors alongside full metadata, reducing query complexity.
3. **Persistence**: Automatic disk persistence; survives restarts.
4. **Learning**: Understand vector search without production database overhead.
5. **Clear Migration Path**: Phase 2 adds PostgreSQL for structured evaluation data; Phase 5 migrates vectors.

**Trade-Offs**:
- Chroma lacks ACID guarantees of PostgreSQL (acceptable for Phase 1 single-user).
- Chroma harder to scale horizontally (mitigated by moving to PostgreSQL in Phase 5).
- PostgreSQL would be overkill for Phase 1 but adds complexity.

**Implications**:
- No database administration needed in Phase 1
- Vector operations are simple and fast
- Must migrate for production scalability
- Migration is planned; no blocking decision

**Reversibility**: HIGH
- Chroma and PostgreSQL+pgvector have similar APIs.
- Migration script can be written once Phase 2 starts.
- No code changes required; only storage backend changes.

---

### Decision T4: sentence-transformers (all-MiniLM-L6-v2) for Embeddings

**Problem**: Which embedding model to use for vectorizing text?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. all-MiniLM-L6-v2 (chosen)** | 22MB, fast, good quality, no GPU | 384-dim (smaller than alternatives) |
| **2. all-mpnet-base-v2** | Better quality | 420MB, slower, needs more compute |
| **3. OpenAI Embeddings API** | State-of-the-art quality | API key required, costs money, no privacy |
| **4. Jina embeddings** | Longer context window | Larger models, slower |
| **5. Domain-specific embeddings** | Optimized for esoteric topics | Need to train/fine-tune |

**Decision**: all-MiniLM-L6-v2 for Phase 1; evaluate alternatives in Phase 2.

**Rationale**:
1. **Local Execution**: No API required; works offline.
2. **Small Footprint**: 22MB fits on any machine; downloads quickly.
3. **Fast Inference**: Can embed 100+ texts/sec on CPU.
4. **Proven Quality**: Widely used in production; battle-tested.
5. **No GPU Required**: Democratizes usage; works on laptops.

**Trade-Offs**:
- 384-dim is smaller than `all-mpnet-base-v2` (768-dim); may miss some semantic nuance.
- No fine-tuning for esoteric terminology (Phase 2 can add this).
- Quality slightly lower than OpenAI embeddings, but sufficient for book retrieval.

**Implications**:
- Embeddings are fast (sub-100ms per query)
- Can run on CPU-only machines
- Storage efficient (384 floats per vector ≈ 1.5KB)
- Relevance threshold tuning is important

**Reversibility**: HIGH
- Swapping embeddings is straightforward; only `embedder.py` changes.
- Re-indexing is one command (Phase 2 can test alternatives).
- No downstream code changes needed.

---

### Decision T5: Ollama + Llama 2/3 for LLM

**Problem**: Which LLM backend for answer generation?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Ollama + Llama (chosen)** | Free, local, private, no API | Lower quality than GPT-4, needs compute |
| **2. OpenAI GPT-4/3.5** | Best quality, easiest API | Subscription costs ($0.01–0.10/query), vendor lock-in |
| **3. Anthropic Claude** | Excellent grounding, long context | API costs, requires API key |
| **4. Open-source via HF** | Free, flexible | More manual setup, no UI for model management |
| **5. Self-hosted vLLM** | Scalable, private | Operational complexity, requires GPU |

**Decision**: Ollama + Llama 2/3 (7B) for Phase 1; add OpenAI option in Phase 2.

**Rationale**:
1. **No Costs**: Free after initial download; no per-query fees.
2. **Privacy**: All data stays on machine; no external API calls.
3. **Control**: Can switch models, fine-tune, or modify easily.
4. **Learning**: Understand LLM operations without black-box APIs.
5. **Ollama UX**: Simple UI for model management; great developer experience.

**Trade-Offs**:
- Llama 2/3 7B is weaker than GPT-4 (especially for general knowledge, but sufficient for grounded QA).
- Requires local compute (CPU OK, GPU faster).
- Initial model download is large (~4GB for 7B).
- Quality gap with GPT-4 is real (~5–10% in preliminary testing); acceptable for esoteric domain.

**Implications**:
- Answer quality is good but not best-in-class
- Response time is 2–5 seconds (acceptable for Phase 1)
- No monthly API bills
- Easy to add GPT-4 option later (Phase 2)

**Reversibility**: HIGH
- `llm.py` is abstracted; can add OpenAI backend without changing generation logic.
- Switching backends is one configuration change.
- Phase 2 plans to add multi-backend support.

---

### Decision T6: LangChain for Text Splitting and Utilities

**Problem**: Should we implement text chunking and utilities from scratch or use a framework?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. LangChain (chosen)** | Battle-tested, flexible, good defaults | Adds dependency, can be overkill |
| **2. Custom implementation** | Full control, lightweight | Reinventing the wheel, maintenance burden |
| **3. spaCy** | NLP-focused, good segmentation | Not designed for chunking with overlap |
| **4. Python built-ins** | Minimal dependencies | Naive splitting, poor context preservation |

**Decision**: Use LangChain's RecursiveCharacterTextSplitter for Phase 1; may simplify in Phase 5.

**Rationale**:
1. **Proven Algorithm**: Recursive splitting respects document structure (paragraphs, sentences, words).
2. **Overlap Support**: Built-in overlap handling; crucial for context preservation.
3. **Flexibility**: Easy to tune separators, chunk size, overlap.
4. **Maintenance**: Don't maintain chunking logic; focus on domain logic.
5. **Ecosystem**: LangChain has other utilities we may use later (chains, memory, etc.).

**Trade-Offs**:
- Adds dependency (but small, well-maintained).
- Could be lighter-weight with custom implementation.
- LangChain's API changes may require future updates.

**Implications**:
- Chunking is robust and well-tested
- Easy to experiment with parameters
- Can swap for custom implementation in Phase 5 if needed
- Reduces maintenance burden

**Reversibility**: MEDIUM
- LangChain is only used in `chunker.py`.
- Swapping out is possible (need to replicate recursive splitting with overlap).
- No blocking dependency; could remove if needed.

---

## Phase 1 Specific Decisions

### Decision P1: Book-Only Knowledge Base (No Web Search)

**Problem**: Should Phase 1 support web search or stick to books only?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Books only (chosen)** | Simple, curated, high-quality sources | Limited scope, no current events |
| **2. Books + web from start** | Broader coverage, timely info | Complex source vetting, more hallucinations |

**Decision**: Phase 1 is books-only. Web search moves to Phase 3.

**Rationale**:
1. **Prove Core Value First**: Validate book-based QA before adding complexity.
2. **Curated Sources**: Books are vetted; easier to ensure citation accuracy.
3. **Simpler Evaluation**: Fewer variables; easier to debug and improve.
4. **User Expectation Management**: Clear scope ("Learn from books").
5. **Iterative Approach**: Add web search after books are solid.

**Implications**:
- Limited to pre-ingested book content
- No answers about current events or recent developments
- Easier to explain to users ("based on classical texts")
- Quick expansion to web search in Phase 3

**Reversibility**: HIGH
- Phase 3 is designed to add web search without modifying Phase 1 code.
- Query routing logic can be added in Phase 3.
- No blocking architectural decision.

---

### Decision P2: Grounding Constraint: Answers Must Cite Sources

**Problem**: Should the system be allowed to generate answers without sources?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Must cite sources (chosen)** | Transparency, reduces hallucination | May refuse valid questions if sources weak |
| **2. Optional citations** | More flexible, answers more questions | Erodes trust, enables hallucination |

**Decision**: Phase 1 enforces citations; answers must have sources.

**Rationale**:
1. **Trust**: Esoteric domain requires high credibility; citations build trust.
2. **Accountability**: System is transparent about knowledge sources.
3. **Quality Control**: Forces retrieval to actually find relevant passages.
4. **Educational**: Users learn where information comes from.
5. **Reduced Hallucination**: LLM can't invent without source.

**Implications**:
- System refuses to answer unsourced questions
- More conservative (may miss valid questions)
- Higher user confidence in answers
- Clearer failure mode (no sources found)

**Reversibility**: HIGH
- Prompt can be changed to relax constraints.
- Phase 2 can evaluate impact and adjust.
- No blocking architectural decision.

---

### Decision P3: Relevance Threshold in Retrieval (0.5 default)

**Problem**: Should we filter low-confidence retrieval results?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Use threshold (chosen)** | Filters noise, improves answer quality | May reject valid results if score too high |
| **2. No threshold (return all K)** | Maximizes recall | May include irrelevant results, confuse LLM |
| **3. Dynamic threshold** | Adapts to query difficulty | More complex, harder to tune |

**Decision**: Default threshold of 0.5; tunable via config. Refined in Phase 1f.

**Rationale**:
1. **Filter Noise**: Remove low-confidence results before LLM sees them.
2. **Clarity**: Threshold is explicit and tunable.
3. **Simplicity**: Fixed threshold is easier than dynamic alternatives.
4. **Quality**: Improves answer quality by focusing on strong signals.

**Trade-Offs**:
- Threshold of 0.5 may be too high (reject valid results) or too low (include noise).
- Phase 1f will validate with test questions.
- Different query types may need different thresholds (handled in Phase 2).

**Implications**:
- Retrieval acts as gate before generation
- Some valid queries may be rejected ("no sources found")
- Can be fine-tuned based on Phase 1f evaluation
- May be adjusted per-query-type in Phase 2

**Reversibility**: HIGH
- Threshold is in `config.py`; easy to change.
- Phase 1f can test multiple thresholds.
- No code changes needed; config-only.

---

### Decision P4: Chunk Size: 256 Tokens, 50% Overlap

**Problem**: What chunk size and overlap strategy should we use?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. 256 tokens, 50% overlap (chosen)** | Balanced; context + precision | Larger index (50% overlap means 1.5x storage) |
| **2. 128 tokens, 25% overlap** | Smaller index, faster search | May miss context; boundary artifacts |
| **3. 512 tokens, 0% overlap** | Minimal index size | Context loss at boundaries; chunky retrieval |
| **4. Adaptive chunking** | Optimal for each document | Complex to implement and tune |

**Decision**: 256 tokens, 50% overlap for Phase 1. Tuned in Phase 1f.

**Rationale**:
1. **Context Preservation**: 256 tokens (~1000 chars) is large enough for meaningful context.
2. **Precision**: Not so large that retrieval is chunky or misses specific info.
3. **Overlap Benefit**: 50% overlap means concepts at chunk boundaries appear in 1–2 chunks; reduces miss rate.
4. **Storage**: 50% overhead is acceptable; Chroma indices are ~100MB per 10k chunks.
5. **Precedent**: 256-token chunks are widely used in retrieval literature.

**Trade-Offs**:
- 50% overlap increases storage (cost: ~50% more disk space).
- Very large chunks (512+) may be too coarse-grained.
- Very small chunks (64) may lack context.
- Optimal size depends on domain; Phase 1f will validate.

**Implications**:
- Retrieval balances precision and context
- Index is ~1.5x larger due to overlap (acceptable)
- Can be tuned based on Phase 1f evaluation
- May need different sizes for different books (Phase 2)

**Reversibility**: HIGH
- Config change in `config.py`.
- Re-ingestion required to apply changes (full ingestion takes ~10 mins for medium-size book).
- Phase 1f can test multiple chunk sizes.

---

### Decision P5: Single Model for Embeddings (No Ensemble)

**Problem**: Should we use a single embedding model or ensemble multiple models?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Single model (chosen)** | Simple, fast, easy to understand | Single point of failure, limited nuance |
| **2. Ensemble (e.g., 3 models)** | Better quality, more robust | 3x slower, 3x storage, more complex |
| **3. Re-ranking** | Single model + secondary ranking | Added latency, complexity |

**Decision**: Phase 1 uses single embedding model. Ensemble evaluation in Phase 2.

**Rationale**:
1. **Simplicity**: Single model is fast, easy to debug, easy to swap.
2. **Sufficient Quality**: all-MiniLM-L6-v2 is strong enough for Phase 1 validation.
3. **Performance**: Embedding must be <100ms; ensemble would violate this.
4. **Cost**: Extra models would require extra compute/storage.
5. **Iteration Speed**: Easier to compare models serially than ensemble.

**Implications**:
- Embedding is fast (<100ms per query)
- Single point of failure (model could be wrong on specific domain)
- Phase 2 can evaluate alternatives and ensemble strategies
- No performance bottleneck from embedding

**Reversibility**: HIGH
- Ensemble is added in `embedder.py`; no other code changes.
- Phase 2 can benchmark single vs. ensemble.
- Easy to add re-ranking in Phase 2.

---

### Decision P6: Synchronous Ingestion (No Async/Queues)

**Problem**: Should ingestion be synchronous or asynchronous?

**Options Considered**:

| Option | Pros | Cons |
|--------|------|------|
| **1. Synchronous (chosen)** | Simple to debug, clear control flow | Blocks UI if ingesting large books |
| **2. Async with task queues** | Non-blocking, better UX | Added complexity (Celery, Redis), harder to debug |

**Decision**: Phase 1 uses synchronous ingestion. Async in Phase 4 if needed.

**Rationale**:
1. **Phase 1 Use Case**: Developers ingesting books locally; few books per session.
2. **Simplicity**: Sync is easier to debug and reason about.
3. **Sufficient UX**: 5–10 minutes to ingest a book is acceptable for Phase 1.
4. **Clear Feedback**: Progress visible in console output; easy to see what's happening.
5. **Deferred Optimization**: Async ingestion in Phase 4 if scaling requires it.

**Implications**:
- Ingestion blocks the server
- Can't query while ingesting (acceptable for Phase 1)
- Clear progress feedback in logs
- Phase 4+ will add async if needed

**Reversibility**: HIGH
- Can wrap ingestion in background tasks later.
- Phase 4 can add Celery + Redis without code changes.
- No blocking architectural decision.

---

## Future Decisions (Phases 2–5)

### Decision F1: Evaluation Framework (Phase 2)

**Problem** (anticipated): How to measure and improve answer quality?

**Planned Solution**:
- Curate 20–30 test questions with known-good answers
- Metric suite: precision, recall, hallucination rate, citation accuracy
- A/B testing framework for prompt variations
- Automated regression testing on test set

**Why Not Phase 1?**: Focus on implementation; evaluation in Phase 2.

---

### Decision F2: Multi-Backend LLM Support (Phase 2+)

**Problem** (anticipated): How to support multiple LLM backends?

**Planned Solution**:
- Abstraction layer in `generation/llm.py`
- Config option to select: Ollama, OpenAI, Anthropic, Hugging Face
- Same `generate()` interface; backend-agnostic

**Why Not Phase 1?**: Single backend sufficient; add flexibility when needed.

---

### Decision F3: Web Search Integration (Phase 3)

**Problem** (anticipated): How to combine book and web sources?

**Planned Solution**:
- Brave Search API for web queries
- Dual retrieval: books + web in parallel
- Ranking/deduplication logic
- Source trust scoring

**Why Not Phase 1?**: Books-only MVP; web search in Phase 3.

---

### Decision F4: Distributed Deployment (Phase 5)

**Problem** (anticipated): How to scale to production?

**Planned Solution**:
- Docker containerization
- Kubernetes orchestration
- Multi-replica API servers
- Distributed ingestion pipeline

**Why Not Phase 1?**: Local development sufficient; production scaling in Phase 5.

---

## Summary Table: Reversibility of Decisions

| Decision | Reversibility | Effort to Change | Phase Change Likely? |
|----------|---------------|-----------------|---------------------|
| Layered architecture | HIGH | Days | No; proven model |
| Python language | MEDIUM | Weeks | Unlikely; Python is sticky |
| FastAPI | HIGH | Days | No; industry standard |
| Chroma → PostgreSQL | HIGH | Days | Yes; Phase 2 for evaluation, Phase 5 for vectors |
| all-MiniLM embeddings | HIGH | Days | Maybe; Phase 2 can benchmark |
| Ollama + Llama | HIGH | Days | Yes; add OpenAI option in Phase 2 |
| LangChain chunker | MEDIUM | Days | Maybe; custom impl in Phase 5 |
| Books-only scope | HIGH | Days | Yes; web search in Phase 3 |
| Citation requirement | HIGH | Hours | Maybe; relax in Phase 2 if needed |
| Relevance threshold | HIGH | Minutes | Yes; tuned in Phase 1f |
| 256-token chunks | HIGH | Hours | Yes; tuned in Phase 1f |
| Single embedding model | HIGH | Days | Maybe; ensemble in Phase 2 |
| Synchronous ingestion | HIGH | Days | Yes; async in Phase 4 |

---

## Lessons for Future Projects

### 1. Start with Simplicity
- Most of these decisions prioritize **simplicity in Phase 1**.
- Build complexity only when needed.
- Validate core value before optimizing.

### 2. Know Your Constraints
- Understand hardware constraints (RAM, GPU, storage).
- Design accordingly (e.g., small embedding model for CPU).
- Plan for scaling (but don't over-engineer).

### 3. Make Decisions Explicit
- Document rationale, not just decision.
- Include trade-offs.
- Record assumptions that could change.

### 4. Reversibility First
- Prefer decisions with high reversibility.
- Defer low-reversibility choices (language, major architecture).
- Low reversibility = more research needed upfront.

### 5. Iterate on Non-Blocking Decisions
- Config options (chunk size, threshold) → tuned in Phase 1f.
- Backend options (embeddings, LLM) → tested in Phase 2.
- Infrastructure (local vs. cloud) → Phase 5.
- But: blocking decisions (language, architecture) → get right upfront.

---

## How to Use This Document

**For Developers**:
- Understand "why" behind each decision.
- Know what can be easily changed vs. what's locked in.
- Use this as a template for documenting your own decisions.

**For Reviewers / Evaluators**:
- See clear trade-off analysis.
- Assess decision-making process and rationale.
- Understand risk management and reversibility thinking.

**For Phase 2+ Development**:
- Reference planned decisions for next phases.
- Use reversibility assessment to prioritize Phase 2+ work.
- Update this doc as decisions are revisited.

---

**Document Owner**: Development Team  
**Last Updated**: 2026-05-16  
**Next Review**: After Phase 1f completion (expected ~2026-06-20)
