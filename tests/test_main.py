"""
Unit tests for the main FastAPI application endpoints.
"""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestMainEndpoints:
    """Test class for main application endpoints."""

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint returns API information."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        # As per task.md: GET / - Return API information and available endpoints
        # Check that we get some API information
        assert isinstance(data, dict)
        
        # Should contain some form of endpoint information
        # (Implementation can vary - dynamic or static)
        assert len(data) > 0

    def test_health_check_endpoint(self, client: TestClient):
        """Test the health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # As per task.md: GET /health - Return API health status
        assert "status" in data
        assert data["status"] == "healthy"

    def test_openapi_docs_accessible(self, client: TestClient):
        """Test that OpenAPI documentation is accessible."""
        # From task.md testing section: http://localhost:8000/docs
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_json_accessible(self, client: TestClient):
        """Test that OpenAPI JSON schema is accessible."""
        # From task.md testing section: http://localhost:8000/openapi.json
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
