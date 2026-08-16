"""
Shared vocabulary for the pipeline: the types and interfaces every layer agrees on.

This package deliberately depends on nothing else in backend/, so any layer can
import from it without creating a cycle. Ingestion, indexing, retrieval and
generation previously each defined their own near-identical shapes and passed
untyped dicts between them; the definitions here are the single source of truth.
"""
