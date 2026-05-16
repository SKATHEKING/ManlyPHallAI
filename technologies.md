# Technologies by Phase

This document outlines the technologies that are likely to be needed across the project roadmap for the Manly P. Hall AI Bot. The goal is to keep the stack practical, modular, and aligned with the phased plan: book-based answering first, then grounding, then web augmentation, then audiovisual delivery, and finally iteration and expansion.

## Phase 1: Book-Based Knowledge Engine

Primary goal: ingest books, chunk them, index them, and answer questions from retrieved passages.

Likely technologies:

- Python for data processing and backend orchestration.
- Discord.py for the primary Discord bot interface.
- FastAPI for lightweight support endpoints and health checks.
- PDF, EPUB, or text parsing libraries for source ingestion.
- OCR tools if any source material exists only as scanned images.
- Sentence chunking or token-based chunking utilities.
- Embeddings model provider for vector representations of book passages.
- Vector database such as PostgreSQL with pgvector, Pinecone, Weaviate, or Chroma.
- PostgreSQL for metadata, source tracking, and application records.
- Object storage for raw book files and processed assets.
- A hosted LLM provider or selected open model for initial answer generation.
- Discord slash commands and rich embeds for the primary user experience.

Supporting concerns:

- Source metadata such as title, author, chapter, page, and chunk ID.
- Basic ingestion jobs or scripts.
- Logging for indexing and retrieval behavior.

## Phase 2: Grounding and Quality Control

Primary goal: improve reliability, enforce citations, and reduce unsupported answers.

Likely technologies:

- Prompt templates or prompt management utilities.
- Evaluation frameworks for testing answer quality.
- Test question datasets stored in JSON, CSV, or a database table.
- Retrieval scoring and reranking tools if needed.
- Application logging and observability tools.
- Error tracking such as Sentry or a similar service.
- Basic analytics for response quality and user feedback.

Supporting concerns:

- Citation formatting and source traceability.
- Refusal logic when sources are weak or missing.
- Regression testing for response quality.

## Phase 3: Internet-Augmented Research

Primary goal: add approved web sources while keeping the system grounded and transparent.

Likely technologies:

- Search APIs such as Brave Search, Tavily, SerpAPI, Bing, or a curated web ingestion source.
- Web scraping or article extraction tools for approved pages.
- HTML parsing and readability extraction libraries.
- Source ranking and filtering logic.
- Additional metadata storage for URLs, domains, timestamps, and trust scores.
- Moderation or content filtering tools for handling unsafe or low-quality web input.
- Optional cache layer such as Redis to reduce repeated searches.

Supporting concerns:

- Source provenance and attribution.
- Deduplication between book and web content.
- Handling conflicting information.

## Phase 4: Audiovisual Experience

Primary goal: turn the assistant into a spoken and visual experience.

Likely technologies:

- Text-to-speech service such as OpenAI TTS, ElevenLabs, Azure TTS, or Amazon Polly.
- Audio playback components in the frontend.
- Streaming response handling so speech begins quickly.
- Avatar or talking-image provider such as D-ID, HeyGen, Synthesia, or a custom animation pipeline.
- Lip-sync or facial animation tooling if a custom avatar is used.
- Media storage for generated audio and visual assets.
- Frontend state management for synchronized text, audio, and animation.

Supporting concerns:

- Latency management for a natural speaking experience.
- Synchronization between speech and avatar motion.
- Media asset cleanup and reuse.

## Phase 5: Iteration and Expansion

Primary goal: improve the system through real usage, broader content, and stronger evaluation.

Likely technologies:

- Experiment tracking or prompt versioning tools.
- Dashboarding and analytics for quality, latency, and usage trends.
- A/B testing or feature flag tooling.
- Expanded indexing and re-indexing pipelines.
- Scheduled jobs or queues for maintenance tasks.
- CI/CD tooling for safe deployment of changes.
- Automated test suites covering ingestion, retrieval, generation, and media flow.

Supporting concerns:

- Source library growth and data refresh cycles.
- Monitoring for retrieval drift and answer degradation.
- Versioning for prompts, models, and indexed content.

## Cross-Cutting Technologies

These technologies are likely to be useful throughout multiple phases:

- Git for source control.
- Docker for reproducible local and production environments.
- A cloud hosting platform such as Vercel, AWS, Azure, or Google Cloud.
- Authentication and access control if the product is not public.
- Rate limiting and abuse protection.
- Secrets management for API keys and service credentials.
- Structured logging and metrics collection.
- Discord bot hosting, command handling, and rich message formatting.

## Recommended Practical Stack for the First Build

If the goal is to move quickly and validate the concept, a pragmatic starting stack would be:

- Interface: Discord bot with discord.py.
- Backend: FastAPI in Python for support endpoints.
- Optional demo UI: Next.js or React.
- Database: PostgreSQL with pgvector.
- LLM: a hosted model provider.
- Embeddings: a hosted embeddings API.
- Storage: object storage for source files and generated media.
- Audio: a hosted TTS service.
- Avatar: a hosted talking-image service first, custom later.
- Observability: logging plus a basic error tracker.

## Notes

- The first phase should stay intentionally simple so the knowledge workflow can be proven before adding media complexity.
- The audiovisual stack should be layered on top of a reliable retrieval and grounding system, not built first.
- The web layer should be curated and controlled, not treated as unrestricted browsing.
