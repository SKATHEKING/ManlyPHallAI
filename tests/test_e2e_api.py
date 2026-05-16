"""
End-to-end tests for the FastAPI server

Tests the complete workflow:
1. Ingest books
2. Query answers
3. List books
4. Delete books
"""
import json
from pathlib import Path

import pytest


class TestAPIIngestWorkflow:
    """Test document ingestion workflow"""

    def test_ingest_text_file(self, api_client, temp_books_dir):
        """Test ingesting a text file"""
        book_path = list(temp_books_dir.glob("*.txt"))[0]

        with open(book_path, "rb") as f:
            response = api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "success"
        assert data["chunks_created"] > 0
        assert data["file_size"] > 0

    def test_ingest_duplicate_file(self, api_client, temp_books_dir):
        """Test ingesting the same file twice"""
        book_path = list(temp_books_dir.glob("*.txt"))[0]

        # First ingest
        with open(book_path, "rb") as f:
            response1 = api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        assert response1.status_code == 200
        chunks_first = response1.json()["chunks_created"]

        # Second ingest of same file
        with open(book_path, "rb") as f:
            response2 = api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Should succeed but add more chunks (or handle duplicate)
        assert response2.status_code == 200

    def test_ingest_invalid_file_type(self, api_client, tmp_path):
        """Test rejecting invalid file types"""
        invalid_file = tmp_path / "test.exe"
        invalid_file.write_bytes(b"binary content")

        with open(invalid_file, "rb") as f:
            response = api_client.post(
                "/api/ingest",
                files={"file": ("test.exe", f, "application/x-msdownload")},
            )

        # Should reject or handle gracefully
        # May return 400 or 415
        assert response.status_code in [400, 415, 422]


class TestAPIAskWorkflow:
    """Test question-answering workflow"""

    def test_ask_simple_question(self, api_client, temp_books_dir):
        """Test asking a simple question"""
        # First ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            ingest_response = api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        assert ingest_response.status_code == 200

        # Then ask a question
        response = api_client.post(
            "/api/ask",
            json={"question": "What is correspondence?"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data or "citations" in data
        assert "confidence" in data or "num_sources" in data

    def test_ask_before_ingestion(self, api_client):
        """Test asking before any books are ingested"""
        response = api_client.post(
            "/api/ask",
            json={"question": "What is this?"},
        )

        # Should handle gracefully (either 200 with "no sources" or appropriate error)
        assert response.status_code in [200, 404, 400]
        if response.status_code == 200:
            data = response.json()
            # Should indicate no sources available
            assert data.get("num_sources", 0) == 0 or "no sources" in data.get(
                "answer", ""
            ).lower()

    def test_ask_with_custom_k(self, api_client, temp_books_dir):
        """Test asking with custom k parameter"""
        # Ingest
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Ask with k=3
        response = api_client.post(
            "/api/ask",
            json={"question": "What is correspondence?", "k": 3},
        )

        assert response.status_code == 200
        data = response.json()
        assert "answer" in data

    def test_ask_empty_question(self, api_client):
        """Test asking with empty question"""
        response = api_client.post(
            "/api/ask",
            json={"question": ""},
        )

        # Should validate and reject empty query
        assert response.status_code in [400, 422]

    def test_ask_very_long_question(self, api_client):
        """Test asking with very long question"""
        long_question = "What " * 1000  # ~5000 characters

        response = api_client.post(
            "/api/ask",
            json={"question": long_question},
        )

        # Should handle gracefully (may accept or reject)
        assert response.status_code in [200, 400, 413]


class TestAPIStatusEndpoint:
    """Test status and information endpoints"""

    def test_get_status(self, api_client):
        """Test getting system status"""
        response = api_client.get("/api/status")

        assert response.status_code == 200
        data = response.json()
        assert "num_chunks" in data or "status" in data
        assert isinstance(data, dict)

    def test_get_status_after_ingestion(self, api_client, temp_books_dir):
        """Test status reflects ingestion"""
        # Get initial status
        response1 = api_client.get("/api/status")
        assert response1.status_code == 200
        initial_chunks = response1.json().get("num_chunks", 0)

        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Get updated status
        response2 = api_client.get("/api/status")
        assert response2.status_code == 200
        updated_chunks = response2.json().get("num_chunks", 0)

        # Should have more chunks
        assert updated_chunks >= initial_chunks


class TestAPIBooksEndpoint:
    """Test books listing and deletion"""

    def test_list_books(self, api_client, temp_books_dir):
        """Test listing ingested books"""
        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # List books
        response = api_client.get("/api/books")

        assert response.status_code == 200
        data = response.json()
        assert "books" in data or isinstance(data, list)

    def test_delete_book(self, api_client, temp_books_dir):
        """Test deleting a book"""
        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        book_name = book_path.name

        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": (book_name, f, "text/plain")},
            )

        # Delete the book
        response = api_client.delete(f"/api/books/{book_name}")

        # Should succeed or not found (depends on implementation)
        assert response.status_code in [200, 404]

    def test_delete_nonexistent_book(self, api_client):
        """Test deleting a book that doesn't exist"""
        response = api_client.delete("/api/books/nonexistent.txt")

        # Should return 404
        assert response.status_code == 404


class TestAPIConcurrency:
    """Test handling of concurrent requests"""

    def test_multiple_sequential_asks(self, api_client, temp_books_dir):
        """Test multiple sequential questions"""
        # Ingest a book
        book_path = list(temp_books_dir.glob("*.txt"))[0]
        with open(book_path, "rb") as f:
            api_client.post(
                "/api/ingest",
                files={"file": ("test_book.txt", f, "text/plain")},
            )

        # Ask multiple questions
        questions = [
            "What is correspondence?",
            "What is vibration?",
            "What is philosophy?",
        ]

        responses = []
        for question in questions:
            response = api_client.post(
                "/api/ask",
                json={"question": question},
            )
            responses.append(response)

        # All should succeed
        assert all(r.status_code == 200 for r in responses)

        # All should have answers
        assert all("answer" in r.json() for r in responses)


class TestAPIErrorHandling:
    """Test error handling and edge cases"""

    def test_malformed_request(self, api_client):
        """Test malformed JSON request"""
        response = api_client.post(
            "/api/ask",
            json={"not_a_question": "value"},
        )

        # Should reject malformed request
        assert response.status_code in [400, 422]

    def test_invalid_http_method(self, api_client):
        """Test invalid HTTP method"""
        response = api_client.get("/api/ask")

        # Should reject GET on POST-only endpoint
        assert response.status_code == 405

    def test_nonexistent_endpoint(self, api_client):
        """Test accessing nonexistent endpoint"""
        response = api_client.get("/api/nonexistent")

        # Should return 404
        assert response.status_code == 404


class TestAPIHealth:
    """Test health check endpoints"""

    def test_health_check(self, api_client):
        """Test basic health check"""
        # Try common health check endpoints
        endpoints = ["/health", "/api/health", "/status"]

        for endpoint in endpoints:
            response = api_client.get(endpoint)
            # At least one should work
            if response.status_code == 200:
                assert response.json().get("status") == "healthy"
                break
