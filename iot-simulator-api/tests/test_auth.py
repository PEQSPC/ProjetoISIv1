"""
Tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from database import User


class TestLogin:
    """Tests for POST /auth/login endpoint."""

    def test_login_success(self, client: TestClient, admin_user: User):
        """Valid credentials should return JWT token."""
        response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "admin123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, client: TestClient, admin_user: User):
        """Wrong password should return 401."""
        response = client.post(
            "/auth/login",
            data={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_wrong_username(self, client: TestClient, admin_user: User):
        """Non-existent user should return 401."""
        response = client.post(
            "/auth/login",
            data={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401

    def test_login_empty_credentials(self, client: TestClient):
        """Empty credentials should return 422."""
        response = client.post("/auth/login", data={})
        assert response.status_code == 422


class TestGetCurrentUser:
    """Tests for GET /auth/me endpoint."""

    def test_get_me_with_valid_token(self, client: TestClient, auth_headers: dict, admin_user: User):
        """Valid token should return user info."""
        response = client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "admin"
        assert data["role"] == "admin"
        assert data["is_active"] is True

    def test_get_me_without_token(self, client: TestClient):
        """Missing token should return 401."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    def test_get_me_with_invalid_token(self, client: TestClient):
        """Invalid token should return 401."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"}
        )
        assert response.status_code == 401


class TestCreateUser:
    """Tests for POST /auth/users endpoint."""

    def test_create_user_as_admin(self, client: TestClient, auth_headers: dict):
        """Admin should be able to create new user."""
        response = client.post(
            "/auth/users",
            headers=auth_headers,
            json={"username": "newuser", "password": "newpass123", "role": "user"}
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["role"] == "user"
        assert data["is_active"] is True

    def test_create_admin_user(self, client: TestClient, auth_headers: dict):
        """Admin should be able to create another admin."""
        response = client.post(
            "/auth/users",
            headers=auth_headers,
            json={"username": "admin2", "password": "admin123", "role": "admin"}
        )
        assert response.status_code == 201
        assert response.json()["role"] == "admin"

    def test_create_user_as_regular_user(self, client: TestClient, user_headers: dict):
        """Regular user should not be able to create users."""
        response = client.post(
            "/auth/users",
            headers=user_headers,
            json={"username": "newuser", "password": "newpass123", "role": "user"}
        )
        assert response.status_code == 403
        assert "Admin privileges required" in response.json()["detail"]

    def test_create_user_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.post(
            "/auth/users",
            json={"username": "newuser", "password": "newpass123", "role": "user"}
        )
        assert response.status_code == 401

    def test_create_duplicate_user(self, client: TestClient, auth_headers: dict):
        """Duplicate username should return 400."""
        # Create first user
        client.post(
            "/auth/users",
            headers=auth_headers,
            json={"username": "duplicate", "password": "pass123", "role": "user"}
        )
        # Try to create again
        response = client.post(
            "/auth/users",
            headers=auth_headers,
            json={"username": "duplicate", "password": "pass456", "role": "user"}
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_create_user_invalid_role(self, client: TestClient, auth_headers: dict):
        """Invalid role should return 400."""
        response = client.post(
            "/auth/users",
            headers=auth_headers,
            json={"username": "newuser", "password": "pass123", "role": "superadmin"}
        )
        assert response.status_code == 400
        assert "Role must be" in response.json()["detail"]


class TestListUsers:
    """Tests for GET /auth/users endpoint."""

    def test_list_users_as_admin(self, client: TestClient, auth_headers: dict, admin_user: User):
        """Admin should see all users."""
        response = client.get("/auth/users", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the admin user

    def test_list_users_as_regular_user(self, client: TestClient, user_headers: dict):
        """Regular user should not be able to list users."""
        response = client.get("/auth/users", headers=user_headers)
        assert response.status_code == 403

    def test_list_users_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.get("/auth/users")
        assert response.status_code == 401


class TestDeleteUser:
    """Tests for DELETE /auth/users/{user_id} endpoint."""

    def test_delete_user_as_admin(self, client: TestClient, auth_headers: dict, db: Session):
        """Admin should be able to delete other users."""
        # Create a user to delete
        response = client.post(
            "/auth/users",
            headers=auth_headers,
            json={"username": "todelete", "password": "pass123", "role": "user"}
        )
        user_id = response.json()["id"]

        # Delete the user
        response = client.delete(f"/auth/users/{user_id}", headers=auth_headers)
        assert response.status_code == 204

        # Verify user is gone
        response = client.get("/auth/users", headers=auth_headers)
        usernames = [u["username"] for u in response.json()]
        assert "todelete" not in usernames

    def test_delete_self_not_allowed(self, client: TestClient, auth_headers: dict, admin_user: User):
        """Admin should not be able to delete themselves."""
        response = client.delete(f"/auth/users/{admin_user.id}", headers=auth_headers)
        assert response.status_code == 400
        assert "Cannot delete yourself" in response.json()["detail"]

    def test_delete_user_as_regular_user(self, client: TestClient, user_headers: dict, admin_user: User):
        """Regular user should not be able to delete users."""
        response = client.delete(f"/auth/users/{admin_user.id}", headers=user_headers)
        assert response.status_code == 403

    def test_delete_nonexistent_user(self, client: TestClient, auth_headers: dict):
        """Deleting non-existent user should return 404."""
        response = client.delete("/auth/users/99999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_user_without_auth(self, client: TestClient):
        """Unauthenticated request should return 401."""
        response = client.delete("/auth/users/1")
        assert response.status_code == 401
