# Manly P. Hall AI Bot

An audiovisual AI assistant focused on esotericism, the occult, and related symbolic traditions. The system will answer questions using grounded information from books and approved online sources, with a strong emphasis on citations, clarity, and trustworthy responses.

## Project Intent

The purpose of this project is to create a specialized chatbot that can:

- Answer user questions about Manly P. Hall, esotericism, occult philosophy, symbolism, mysticism, and related subjects.
- Ground responses in a curated body of books and reliable information from the internet.
- Present answers in a future audiovisual format, including speech and a talking image/avatar.
- Remain useful, accurate, and easy to expand over time.

The long-term goal is not just to generate text, but to provide a guided, conversational knowledge experience that feels thoughtful, accessible, and expressive.

## Product Vision

This project is being built as a domain-specific AI assistant rather than a general-purpose chatbot. That focus gives it three advantages:

1. Better quality answers through a limited and curated knowledge scope.
2. Faster iteration because the first version can be tested on a narrow set of sources.
3. A stronger user experience because voice and visual presentation can be added once the core answer engine is reliable.

## Guiding Principles

- Start small and prove the core value early.
- Prefer sourced answers over unsupported generation.
- Keep the system transparent about where information came from.
- Design for iteration, not perfection on the first release.
- Add audiovisual features only after the knowledge layer is stable.

## MVP Scope

The initial MVP will focus on book-based question answering only.

### MVP Goals

- Support questions about a narrow and curated source set.
- Retrieve relevant passages from books.
- Generate concise answers grounded in those passages.
- Include citations or source references for each answer.

### What the MVP Will Not Include

- Full web browsing across the open internet.
- Complex memory or personalization.
- Voice output.
- Avatar animation.
- Broad coverage of all esoteric traditions.

## Roadmap

### Phase 1: Book-Based Knowledge Engine

Build the first version around a small, curated collection of books.

Key work:

- Collect and organize source texts.
- Extract and clean book content.
- Split content into searchable chunks.
- Index the chunks in a retrieval system.
- Generate answers from retrieved passages only.

Outcome:

- A text-based chatbot that can answer questions using books and cite its sources.

### Phase 2: Grounding and Quality Control

Improve answer reliability and source discipline.

Key work:

- Refine prompt structure for grounded answers.
- Add refusal behavior when sources are weak or missing.
- Build a small evaluation set of test questions.
- Review response quality and citation accuracy.

Outcome:

- More dependable answers with fewer hallucinations and clearer source attribution.

### Phase 3: Internet-Augmented Research

Expand the assistant to include approved online information.

Key work:

- Add controlled web search or curated web ingestion.
- Rank and filter internet sources for trustworthiness.
- Combine book and web evidence in the response flow.
- Preserve citations and provenance.

Outcome:

- A broader research assistant that still remains grounded in traceable sources.

### Phase 4: Audiovisual Experience

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
