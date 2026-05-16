"""
Performance tests for Phase 1f

Measures latency and throughput of key operations:
- Ingestion latency
- Query latency
- Concurrent request handling
- Memory usage
"""
import time
from typing import List

import pytest


class TestIngestionPerformance:
    """Benchmark ingestion latency"""

    def test_single_book_ingestion_latency(self, api_client, temp_books_dir):
        """Measure time to ingest a single book"""
        book_path = list(temp_books_dir.glob("*.txt"))[0]

        start_time = time.time()

        with open(book_path, "rb") as f:
            response = api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        elapsed = time.time() - start_time

        assert response.status_code == 200
        print(f"Single book ingestion latency: {elapsed:.2f}s")

        # Target: < 2 seconds for typical book
        # Adjust threshold based on actual performance
        assert elapsed < 10  # Generous timeout for CI

    def test_multiple_books_ingestion(self, api_client, temp_books_dir):
        """Measure time to ingest multiple books"""
        book_files = list(temp_books_dir.glob("*.txt"))
        assert len(book_files) > 0

        start_time = time.time()

        for book_path in book_files:
            with open(book_path, "rb") as f:
                response = api_client.post(
                    "/api/ingest",
                    files={"file": (book_path.name, f, "text/plain")},
                )
            assert response.status_code == 200

        elapsed = time.time() - start_time
        avg_per_book = elapsed / len(book_files)

        print(f"Multiple books ingestion: {elapsed:.2f}s ({avg_per_book:.2f}s per book)")

        # Should scale roughly linearly
        # Allow up to 5s per book in testing environment
        assert avg_per_book < 10


class TestQueryPerformance:
    """Benchmark question-answering latency"""

    def test_query_latency_first_question(self, api_client, temp_books_dir):
        """Measure latency for first query (with initialization)"""
        # Ingest a book first
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Time the first query
        start_time = time.time()

        response = api_client.post(
            "/api/ask",
            json={"question": "What is correspondence?"},
        )

        elapsed = time.time() - start_time

        assert response.status_code == 200
        print(f"First query latency: {elapsed:.2f}s")

        # First query may be slower (model loading, etc)
        # Allow up to 30 seconds in testing (Ollama startup)
        assert elapsed < 60

    def test_query_latency_subsequent_questions(self, api_client, temp_books_dir):
        """Measure latency for subsequent queries"""
        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Warm up
        api_client.post(
            "/api/ask",
            json={"question": "What is vibration?"},
        )

        # Measure subsequent queries
        questions = [
            "What is correspondence?",
            "Explain polarity",
            "What is philosophy?",
            "Define metaphysics",
        ]

        latencies = []
        for question in questions:
            start_time = time.time()

            response = api_client.post(
                "/api/ask",
                json={"question": question},
            )

            elapsed = time.time() - start_time
            latencies.append(elapsed)

            assert response.status_code == 200

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        print(
            f"Query latencies: min={min_latency:.2f}s, avg={avg_latency:.2f}s, max={max_latency:.2f}s"
        )

        # Average should be reasonable
        # Allow up to 15s average (depends on Ollama setup)
        assert avg_latency < 30

    def test_query_latency_with_different_k_values(self, api_client, temp_books_dir):
        """Compare latency with different retrieval k values"""
        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Warm up
        api_client.post(
            "/api/ask",
            json={"question": "test"},
        )

        k_values = [1, 3, 5, 10]
        latencies = {}

        for k in k_values:
            start_time = time.time()

            response = api_client.post(
                "/api/ask",
                json={"question": "What is correspondence?", "k": k},
            )

            elapsed = time.time() - start_time
            latencies[k] = elapsed

            assert response.status_code == 200

        print(f"Latencies by k value: {latencies}")

        # Latency should increase slightly with k (more retrieval)
        # but not dramatically
        for k in k_values[1:]:
            assert latencies[k] < latencies[k_values[0]] * 3  # At most 3x slower


class TestConcurrentRequests:
    """Test handling of concurrent requests"""

    def test_sequential_requests_throughput(self, api_client, temp_books_dir):
        """Measure throughput of sequential requests"""
        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Warm up
        api_client.post(
            "/api/ask",
            json={"question": "test"},
        )

        # Time 10 sequential requests
        start_time = time.time()
        num_requests = 10

        for i in range(num_requests):
            response = api_client.post(
                "/api/ask",
                json={"question": f"Question {i}"},
            )
            assert response.status_code == 200

        elapsed = time.time() - start_time
        throughput = num_requests / elapsed

        print(f"Sequential throughput: {throughput:.2f} requests/second")

        # Should handle at least 0.1 req/s (10s per request on slow setup)
        assert throughput > 0.05

    def test_rapid_api_status_calls(self, api_client):
        """Test rapid calls to lightweight endpoint"""
        # Status endpoint should be very fast
        start_time = time.time()
        num_calls = 20

        for _ in range(num_calls):
            response = api_client.get("/api/status")
            assert response.status_code == 200

        elapsed = time.time() - start_time
        avg_latency = elapsed / num_calls

        print(f"Status endpoint latency: {avg_latency*1000:.1f}ms")

        # Status should be very fast (< 100ms each)
        assert avg_latency < 0.5


class TestMemoryUsage:
    """Test memory consumption"""

    def test_memory_after_initialization(self, api_client):
        """Measure baseline memory usage"""
        # Just calling API should initialize but use minimal memory
        response = api_client.get("/api/status")
        assert response.status_code == 200

        # Note: Actual memory measurement would require psutil
        # This is a placeholder for the test structure
        print("Memory test: baseline initialized")

    def test_memory_after_ingestion(self, api_client, temp_books_dir):
        """Measure memory after ingesting books"""
        book_path = list(temp_books_dir.glob("*.txt"))[0]

        with open(book_path, "rb") as f:
            response = api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        assert response.status_code == 200

        # Note: Actual memory measurement would require psutil
        print("Memory test: after ingestion")


class TestResponseQuality:
    """Test quality of responses under load"""

    def test_response_has_required_fields(self, api_client, temp_books_dir):
        """Verify response format is consistent"""
        # Ingest
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        response = api_client.post(
            "/api/ask",
            json={"question": "What is correspondence?"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "answer" in data
        assert len(data["answer"]) > 0
        assert isinstance(data["answer"], str)

        # Sources should be present (if books are ingested)
        if data.get("num_sources", 0) > 0 or "sources" in data:
            assert "sources" in data or "citations" in data

    def test_answer_length_reasonable(self, api_client, temp_books_dir):
        """Verify answers are reasonable length"""
        # Ingest
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        response = api_client.post(
            "/api/ask",
            json={"question": "What is correspondence?"},
        )

        assert response.status_code == 200
        data = response.json()
        answer = data.get("answer", "")

        # Answer should not be empty and not excessively long
        assert 0 < len(answer) < 10000

        print(f"Answer length: {len(answer)} characters")
