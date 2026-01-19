"""
Tests for health check endpoints.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for /health endpoint."""

    def test_health_returns_200(self, client: TestClient):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client: TestClient):
        """Health endpoint should return status field."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert data["status"] in ["healthy", "degraded"]

    def test_health_returns_kubernetes_status(self, client: TestClient):
        """Health endpoint should return kubernetes connection status."""
        response = client.get("/health")
        data = response.json()

        assert "kubernetes" in data
        assert data["kubernetes"] in ["connected", "disconnected"]

    def test_health_returns_database_status(self, client: TestClient):
        """Health endpoint should return database connection status."""
        response = client.get("/health")
        data = response.json()

        assert "database" in data
        assert data["database"] in ["connected", "disconnected"]

    def test_health_is_public(self, client: TestClient):
        """Health endpoint should be accessible without authentication."""
        # No auth headers provided
        response = client.get("/health")
        assert response.status_code == 200


class TestRootEndpoint:
    """Tests for root / endpoint."""

    def test_root_returns_200(self, client: TestClient):
        """Root endpoint should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_root_returns_welcome_message(self, client: TestClient):
        """Root endpoint should return welcome message."""
        response = client.get("/")
        data = response.json()

        assert "message" in data
        assert "IoT Simulator" in data["message"]

    def test_root_returns_docs_link(self, client: TestClient):
        """Root endpoint should include docs link."""
        response = client.get("/")
        data = response.json()

        assert "docs" in data
        assert data["docs"] == "/docs"

    def test_root_returns_version(self, client: TestClient):
        """Root endpoint should include version."""
        response = client.get("/")
        data = response.json()

        assert "version" in data
