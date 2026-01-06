"""
Fixtures e configurações para testes.
"""
import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

# Mockar docker client antes de importar main
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Mock Docker client to prevent connection errors during testing
sys.modules['docker'] = MagicMock()

from database import Base, Simulation, get_db

# Mock docker_client before importing main
with patch('main.docker_client'):
    from main import app


@pytest.fixture(scope="function")
def test_db():
    """Cria uma sessão BD limpa em memória para cada teste."""
    # Use in-memory SQLite database for each test
    DATABASE_URL = "sqlite:///:memory:"
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )

    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()

    yield db

    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db):
    """Cliente de teste para a API com BD isolada."""
    # Garantir que cada cliente tem sua própria BD
    return TestClient(app)


@pytest.fixture
def sample_simulation_config():
    """Configuração de simulação de exemplo para testes."""
    return {
        "BROKER_URL": "test.mosquitto.org",
        "BROKER_PORT": 1883,
        "TIME_INTERVAL": 10,
        "duration_minutes": 10,
        "TOPICS": [
            {
                "TYPE": "single",
                "PREFIX": "sensor/temperature",
                "TIME_INTERVAL": 5,
                "DATA": [
                    {
                        "NAME": "value",
                        "TYPE": "float",
                        "MIN_VALUE": 15.0,
                        "MAX_VALUE": 30.0,
                        "MAX_STEP": 0.5,
                        "INITIAL_VALUE": 20.0
                    }
                ]
            }
        ]
    }


@pytest.fixture
def sample_simulation(test_db):
    """Cria uma simulação de exemplo no BD."""
    sim = Simulation(
        simulation_id="test-sim-001",
        container_id="container-abc123",
        config_path="/tmp/test-config.json",
        config_json='{"BROKER_URL": "test.mosquitto.org"}',
        status="running",
        duration_minutes=10,
        expires_at=datetime.utcnow() + timedelta(minutes=10)
    )
    test_db.add(sim)
    test_db.commit()
    test_db.refresh(sim)
    return sim
