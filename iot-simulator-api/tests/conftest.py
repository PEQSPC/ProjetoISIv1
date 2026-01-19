"""
Pytest configuration and fixtures for API tests.
"""
import os
import sys
import pytest
from typing import Generator
from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Base, User, Simulation
from auth import get_password_hash


# === Test Database Setup ===
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_db() -> Generator[Session, None, None]:
    """Override database dependency for tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# === Mock K8s Service ===
class MockK8sService:
    """Mock Kubernetes service for testing."""

    def __init__(self):
        self.pods_created = []
        self.pods_deleted = []

    def create_pod(self, pod_name: str, sim_id: str, config_json: str, duration_minutes: int) -> None:
        self.pods_created.append({
            "pod_name": pod_name,
            "sim_id": sim_id,
            "config_json": config_json,
            "duration_minutes": duration_minutes
        })

    def get_pod_status(self, pod_name: str):
        return "Running", ["Log line 1", "Log line 2"]

    def delete_pod(self, pod_name: str) -> bool:
        self.pods_deleted.append(pod_name)
        return True

    def check_connection(self) -> bool:
        return True


def get_mock_k8s_service():
    """Return mock K8s service."""
    return MockK8sService()


# === Fixtures ===
@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with mocked dependencies."""
    from main import app
    from database import get_db
    from services.k8s_service import get_k8s_service

    # Override dependencies
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_k8s_service] = get_mock_k8s_service

    with TestClient(app) as test_client:
        yield test_client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create an admin user for testing."""
    user = User(
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role="admin",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def regular_user(db: Session) -> User:
    """Create a regular user for testing."""
    user = User(
        username="user1",
        hashed_password=get_password_hash("user123"),
        role="user",
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_token(client: TestClient, admin_user: User) -> str:
    """Get JWT token for admin user."""
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def user_token(client: TestClient, regular_user: User) -> str:
    """Get JWT token for regular user."""
    response = client.post(
        "/auth/login",
        data={"username": "user1", "password": "user123"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token: str) -> dict:
    """Get authorization headers for admin."""
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def user_headers(user_token: str) -> dict:
    """Get authorization headers for regular user."""
    return {"Authorization": f"Bearer {user_token}"}
