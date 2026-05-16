"""
Fixtures and test data for E2E tests
"""
import json
import tempfile
from pathlib import Path
from typing import Dict, List

import pytest


# Sample test data
SAMPLE_BOOKS = {
    "test_hermetic.txt": """
The Hermetic Principles

The Principle of Mentalism
All is Mind. The universe is mental. The all is spirit.

The Principle of Correspondence
As above, so below. As below, so above.
The macrocosm reflects in the microcosm.

The Principle of Vibration
Nothing rests. Everything vibrates.
All is motion in the universe.

The Principle of Polarity
Everything is dual. Everything has poles.
Opposites are identical in nature but different in degree.

The Principle of Rhythm
Everything flows. Everything has tides.
Compensation is the law.

The Principle of Cause and Effect
Every cause has its effect. Every effect has its cause.
Nothing happens by chance. All is governed by law.

The Principle of Gender
Gender is in everything. Masculine and feminine principles.
Procreation and creation in all dimensions.
""",
    "test_philosophy.txt": """
Introduction to Philosophy

What is Philosophy?
Philosophy comes from the Greek words for love (philo) and wisdom (sophia).
It is the pursuit of knowledge about existence, reality, and human nature.

Metaphysics
Metaphysics is the study of the nature of reality.
It asks: What exists? What is the nature of existence?
Does God exist? What is the mind?

Epistemology
Epistemology is the theory of knowledge.
It examines how we know what we know.
What is the source of knowledge? Can we trust our senses?

Ethics
Ethics is the study of morality and how we should live.
What is good? What is right? What are our duties?
How should society be organized?
""",
}

BENCHMARK_QUESTIONS = [
    {
        "id": "q1",
        "question": "What is the principle of correspondence?",
        "category": "hermetic",
        "expected_sources": ["test_hermetic.txt"],
        "difficulty": "easy",
        "expected_topics": ["as above", "so below", "macrocosm", "microcosm"],
    },
    {
        "id": "q2",
        "question": "Explain the principle of vibration.",
        "category": "hermetic",
        "expected_sources": ["test_hermetic.txt"],
        "difficulty": "medium",
        "expected_topics": ["vibration", "motion", "rest"],
    },
    {
        "id": "q3",
        "question": "What is metaphysics?",
        "category": "philosophy",
        "expected_sources": ["test_philosophy.txt"],
        "difficulty": "easy",
        "expected_topics": ["reality", "existence", "nature"],
    },
    {
        "id": "q4",
        "question": "Compare Hermetic principles with philosophical inquiry.",
        "category": "comparison",
        "expected_sources": ["test_hermetic.txt", "test_philosophy.txt"],
        "difficulty": "hard",
        "expected_topics": ["principles", "knowledge", "reality"],
    },
]


@pytest.fixture
def temp_books_dir():
    """Create temporary directory with test books"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        for filename, content in SAMPLE_BOOKS.items():
            (tmppath / filename).write_text(content)
        yield tmppath


@pytest.fixture
def benchmark_questions():
    """Return benchmark questions"""
    return BENCHMARK_QUESTIONS


@pytest.fixture
def expected_answers():
    """Expected answers for benchmark questions"""
    return {
        "q1": {
            "answer": "The principle of correspondence states 'as above, so below' and reflects macrocosm in microcosm",
            "min_length": 50,
            "max_length": 500,
        },
        "q2": {
            "answer": "Vibration principle: nothing rests, everything vibrates and is in motion",
            "min_length": 50,
            "max_length": 500,
        },
        "q3": {
            "answer": "Metaphysics is the study of the nature of reality and existence",
            "min_length": 50,
            "max_length": 500,
        },
        "q4": {
            "answer": "Both seek to understand fundamental truths about reality",
            "min_length": 80,
            "max_length": 1000,
        },
    }


@pytest.fixture
def api_client():
    """Return HTTP client for API testing"""
    from fastapi.testclient import TestClient
    from backend.main import app

    return TestClient(app)


@pytest.fixture
def sample_pdf_path(tmp_path):
    """Create a temporary PDF file for testing"""
    # For now, return path - actual PDF creation would use PyPDF2
    pdf_path = tmp_path / "test.pdf"
    pdf_path.write_text("Mock PDF content")
    return pdf_path
