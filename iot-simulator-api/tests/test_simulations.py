"""
Tests for simulation endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import User, Simulation


# Valid simulation config for testing
VALID_CONFIG = {
    "BROKER_URL": "test.mosquitto.org",
    "BROKER_PORT": 1883,
    "TIME_INTERVAL": 2,
    "TOPICS": [{
        "TYPE": "single",
        "PREFIX": "test/sensor",
        "DATA": [{
            "NAME": "temperature",
            "TYPE": "float",
            "MIN_VALUE": 20,
            "MAX_VALUE": 35
        }]
    }],
    "duration_minutes": 5
}


class TestCreateSimulation:
    """Tests for POST /simulations endpoint."""

    def test_create_simulation_success(self, client: TestClient, auth_headers: dict):
        """Valid config should create simulation."""
        response = client.post(
            "/simulations",
            headers=auth_headers,
            json=VALID_CONFIG
        )
        assert response.status_code == 201
        data = response.json()
        assert "simulation_id" in data
        assert "pod_name" in data
        assert data["status"] == "running"
        assert data["expires_in_minutes"] == 5

    def test_create_simulation_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.post("/simulations", json=VALID_CONFIG)
        assert response.status_code == 401

    def test_create_simulation_invalid_duration(self, client: TestClient, auth_headers: dict):
        """Duration outside range should return 422."""
        invalid_config = VALID_CONFIG.copy()
        invalid_config["duration_minutes"] = 200  # Max is 120
        response = client.post(
            "/simulations",
            headers=auth_headers,
            json=invalid_config
        )
        assert response.status_code == 422

    def test_create_simulation_missing_topics(self, client: TestClient, auth_headers: dict):
        """Missing TOPICS should return 422."""
        invalid_config = {
            "BROKER_URL": "test.mosquitto.org",
            "BROKER_PORT": 1883,
            "duration_minutes": 5
        }
        response = client.post(
            "/simulations",
            headers=auth_headers,
            json=invalid_config
        )
        assert response.status_code == 422

    def test_create_simulation_as_regular_user(self, client: TestClient, user_headers: dict):
        """Regular user should be able to create simulations."""
        response = client.post(
            "/simulations",
            headers=user_headers,
            json=VALID_CONFIG
        )
        assert response.status_code == 201


class TestListSimulations:
    """Tests for GET /simulations endpoint."""

    def test_list_simulations_empty(self, client: TestClient, auth_headers: dict):
        """Should return empty list when no simulations."""
        response = client.get("/simulations", headers=auth_headers)
        assert response.status_code == 200
        assert response.json() == []

    def test_list_simulations_with_data(self, client: TestClient, auth_headers: dict):
        """Should list created simulations."""
        # Create a simulation
        client.post("/simulations", headers=auth_headers, json=VALID_CONFIG)

        response = client.get("/simulations", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "simulation_id" in data[0]
        assert "status" in data[0]
        assert "created_at" in data[0]
        assert "duration_minutes" in data[0]

    def test_list_simulations_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.get("/simulations")
        assert response.status_code == 401

    def test_admin_sees_all_simulations(
        self,
        client: TestClient,
        auth_headers: dict,
        user_headers: dict
    ):
        """Admin should see simulations from all users."""
        # User creates simulation
        client.post("/simulations", headers=user_headers, json=VALID_CONFIG)

        # Admin creates simulation
        client.post("/simulations", headers=auth_headers, json=VALID_CONFIG)

        # Admin should see both
        response = client.get("/simulations", headers=auth_headers)
        assert len(response.json()) == 2

    def test_user_sees_only_own_simulations(
        self,
        client: TestClient,
        auth_headers: dict,
        user_headers: dict
    ):
        """Regular user should only see their own simulations."""
        # Admin creates simulation
        client.post("/simulations", headers=auth_headers, json=VALID_CONFIG)

        # User creates simulation
        client.post("/simulations", headers=user_headers, json=VALID_CONFIG)

        # User should only see their own
        response = client.get("/simulations", headers=user_headers)
        assert len(response.json()) == 1


class TestGetSimulation:
    """Tests for GET /simulations/{sim_id} endpoint."""

    def test_get_simulation_success(self, client: TestClient, auth_headers: dict):
        """Should return simulation details."""
        # Create a simulation
        create_response = client.post(
            "/simulations",
            headers=auth_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        response = client.get(f"/simulations/{sim_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["simulation_id"] == sim_id
        assert "pod_name" in data
        assert "db_status" in data
        assert "k8s_status" in data
        assert "logs" in data

    def test_get_simulation_not_found(self, client: TestClient, auth_headers: dict):
        """Non-existent simulation should return 404."""
        response = client.get("/simulations/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_get_simulation_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.get("/simulations/some-id")
        assert response.status_code == 401

    def test_user_cannot_see_others_simulation(
        self,
        client: TestClient,
        auth_headers: dict,
        user_headers: dict
    ):
        """User should not see simulation owned by another user."""
        # Admin creates simulation
        create_response = client.post(
            "/simulations",
            headers=auth_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        # User tries to access it
        response = client.get(f"/simulations/{sim_id}", headers=user_headers)
        assert response.status_code == 403

    def test_admin_can_see_user_simulation(
        self,
        client: TestClient,
        auth_headers: dict,
        user_headers: dict
    ):
        """Admin should be able to see any simulation."""
        # User creates simulation
        create_response = client.post(
            "/simulations",
            headers=user_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        # Admin accesses it
        response = client.get(f"/simulations/{sim_id}", headers=auth_headers)
        assert response.status_code == 200


class TestDeleteSimulation:
    """Tests for DELETE /simulations/{sim_id} endpoint."""

    def test_delete_simulation_success(self, client: TestClient, auth_headers: dict):
        """Should stop and delete simulation."""
        # Create a simulation
        create_response = client.post(
            "/simulations",
            headers=auth_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        # Delete it
        response = client.delete(f"/simulations/{sim_id}", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "success"

    def test_delete_simulation_not_found(self, client: TestClient, auth_headers: dict):
        """Non-existent simulation should return 404."""
        response = client.delete("/simulations/nonexistent", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_simulation_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.delete("/simulations/some-id")
        assert response.status_code == 401

    def test_user_cannot_delete_others_simulation(
        self,
        client: TestClient,
        auth_headers: dict,
        user_headers: dict
    ):
        """User should not delete simulation owned by another user."""
        # Admin creates simulation
        create_response = client.post(
            "/simulations",
            headers=auth_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        # User tries to delete it
        response = client.delete(f"/simulations/{sim_id}", headers=user_headers)
        assert response.status_code == 403

    def test_admin_can_delete_user_simulation(
        self,
        client: TestClient,
        auth_headers: dict,
        user_headers: dict
    ):
        """Admin should be able to delete any simulation."""
        # User creates simulation
        create_response = client.post(
            "/simulations",
            headers=user_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        # Admin deletes it
        response = client.delete(f"/simulations/{sim_id}", headers=auth_headers)
        assert response.status_code == 200

    def test_user_can_delete_own_simulation(self, client: TestClient, user_headers: dict):
        """User should be able to delete their own simulation."""
        # User creates simulation
        create_response = client.post(
            "/simulations",
            headers=user_headers,
            json=VALID_CONFIG
        )
        sim_id = create_response.json()["simulation_id"]

        # User deletes it
        response = client.delete(f"/simulations/{sim_id}", headers=user_headers)
        assert response.status_code == 200
