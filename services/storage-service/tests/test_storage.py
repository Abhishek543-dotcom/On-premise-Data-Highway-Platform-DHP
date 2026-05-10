"""
Tests for Storage Service API endpoints.
"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.models import BucketCreateRequest
from app.s3_client import get_s3_client

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


class TestBucketEndpoints:
    def test_create_bucket(self, client):
        """Should create a bucket and return 201."""
        mock_s3 = MagicMock()
        mock_s3.create_bucket.return_value = {"status": "created"}
        app.dependency_overrides[get_s3_client] = lambda: mock_s3

        response = client.post(
            "/api/v1/storage/buckets",
            json={"name": "test-bucket"},
            headers=API_HEADERS,
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "test-bucket"
        assert data["status"] == "created"
        mock_s3.create_bucket.assert_called_once_with("test-bucket")

    def test_create_bucket_invalid_name(self, client):
        """Should return 422 for invalid bucket name."""
        response = client.post(
            "/api/v1/storage/buckets",
            json={"name": "AB"},  # too short and uppercase
            headers=API_HEADERS,
        )
        assert response.status_code == 422

    def test_list_buckets(self, client):
        """Should return a list of buckets."""
        mock_s3 = MagicMock()
        mock_s3.list_buckets.return_value = [
            {"name": "bucket-1", "creation_date": "2026-01-01T00:00:00Z"},
            {"name": "bucket-2", "creation_date": "2026-02-01T00:00:00Z"},
        ]
        app.dependency_overrides[get_s3_client] = lambda: mock_s3

        response = client.get("/api/v1/storage/buckets", headers=API_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["buckets"]) == 2

    def test_list_objects(self, client):
        """Should return objects in a bucket."""
        mock_s3 = MagicMock()
        mock_s3.list_objects.return_value = {
            "bucket": "test-bucket",
            "prefix": "",
            "objects": [{"key": "file.txt", "size": 1024}],
            "total": 1,
            "is_truncated": False,
        }
        app.dependency_overrides[get_s3_client] = lambda: mock_s3

        response = client.get(
            "/api/v1/storage/buckets/test-bucket/objects",
            headers=API_HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["objects"][0]["key"] == "file.txt"

    def test_list_objects_not_found(self, client):
        """Should return 404 for non-existent bucket."""
        mock_s3 = MagicMock()
        mock_s3.list_objects.return_value = None
        app.dependency_overrides[get_s3_client] = lambda: mock_s3

        response = client.get(
            "/api/v1/storage/buckets/nonexistent/objects",
            headers=API_HEADERS,
        )
        assert response.status_code == 404

    def test_presigned_url(self, client):
        """Should generate a presigned URL."""
        mock_s3 = MagicMock()
        mock_s3.generate_presigned_url.return_value = "https://minio:9000/bucket/key?signed=true"
        app.dependency_overrides[get_s3_client] = lambda: mock_s3

        response = client.post(
            "/api/v1/storage/buckets/test-bucket/presigned-url",
            json={"object_key": "data/file.parquet", "operation": "download", "expiry": 3600},
            headers=API_HEADERS,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["bucket"] == "test-bucket"
        assert data["object_key"] == "data/file.parquet"
        assert "url" in data

    def test_requires_api_key(self, client):
        """Should reject requests without API key."""
        response = client.get("/api/v1/storage/buckets")
        assert response.status_code == 401


class TestModels:
    def test_bucket_create_valid(self):
        req = BucketCreateRequest(name="my-bucket")
        assert req.name == "my-bucket"

    def test_bucket_create_invalid_pattern(self):
        with pytest.raises(Exception):
            BucketCreateRequest(name="Invalid-BUCKET!")

    def test_bucket_create_too_short(self):
        with pytest.raises(Exception):
            BucketCreateRequest(name="ab")
