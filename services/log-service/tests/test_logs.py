"""
Tests for Log Service API endpoints.
"""
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.logs import get_loki_client

API_HEADERS = {"X-API-Key": "dev-api-key-change-me"}


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestHealthEndpoints:
    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "version" in data

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestLogEndpoints:
    def test_get_logs_success(self, client):
        """Should return logs for a given job_id."""
        mock_loki = AsyncMock()
        mock_loki.query_logs.return_value = [
            {"timestamp": "2026-03-28T10:00:00Z", "source": "stdout", "message": "Starting Spark"},
            {"timestamp": "2026-03-28T10:00:01Z", "source": "stdout", "message": "Job complete"},
        ]
        app.dependency_overrides[get_loki_client] = lambda: mock_loki

        response = client.get("/api/v1/logs/job-123", headers=API_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job-123"
        assert data["log_count"] == 2
        assert len(data["entries"]) == 2
        mock_loki.query_logs.assert_awaited_once_with(
            job_id="job-123", source="all", tail=500
        )

    def test_get_logs_with_params(self, client):
        """Should pass source and tail parameters to Loki."""
        mock_loki = AsyncMock()
        mock_loki.query_logs.return_value = []
        app.dependency_overrides[get_loki_client] = lambda: mock_loki

        response = client.get(
            "/api/v1/logs/job-456?source=stderr&tail=100",
            headers=API_HEADERS,
        )
        assert response.status_code == 200
        mock_loki.query_logs.assert_awaited_once_with(
            job_id="job-456", source="stderr", tail=100
        )

    def test_get_logs_empty(self, client):
        """Should return empty entries for a job with no logs."""
        mock_loki = AsyncMock()
        mock_loki.query_logs.return_value = []
        app.dependency_overrides[get_loki_client] = lambda: mock_loki

        response = client.get("/api/v1/logs/no-logs-job", headers=API_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["log_count"] == 0
        assert data["entries"] == []

    def test_get_logs_requires_api_key(self, client):
        """Should reject requests without API key."""
        response = client.get("/api/v1/logs/job-123")
        assert response.status_code == 401

    def test_get_logs_invalid_api_key(self, client):
        """Should reject requests with wrong API key."""
        response = client.get(
            "/api/v1/logs/job-123",
            headers={"X-API-Key": "wrong-key"},
        )
        assert response.status_code == 401
