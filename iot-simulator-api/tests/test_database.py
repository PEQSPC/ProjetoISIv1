"""
Testes unitários para o módulo database.py
"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Simulation


class TestSimulationModel:
    """Testes para o modelo Simulation."""

    def test_create_simulation(self, test_db):
        """Testa criação básica de simulação."""
        sim = Simulation(
            simulation_id="test-001",
            container_id="container-001",
            config_path="/tmp/config.json",
            config_json='{"key": "value"}',
            status="running",
            duration_minutes=30,
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        # Verificar que foi criado
        assert sim.id is not None
        assert sim.simulation_id == "test-001"
        assert sim.status == "running"

    def test_simulation_unique_id(self, test_db):
        """Testa restrição de ID único."""
        sim1 = Simulation(
            simulation_id="unique-001",
            container_id="container-001",
            config_path="/tmp/config1.json",
            config_json='{"key": "value"}',
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim1)
        test_db.commit()

        # Tentar criar outro com mesmo ID
        sim2 = Simulation(
            simulation_id="unique-001",  # Mesmo ID
            container_id="container-002",
            config_path="/tmp/config2.json",
            config_json='{"key": "value"}',
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim2)

        # Deve lançar erro de integridade
        with pytest.raises(IntegrityError):
            test_db.commit()

    def test_simulation_default_status(self, test_db):
        """Testa status padrão."""
        sim = Simulation(
            simulation_id="test-status",
            container_id="container-001",
            config_path="/tmp/config.json",
            config_json='{}',
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        assert sim.status == "running"

    def test_simulation_nullable_fields(self, test_db):
        """Testa campos que podem ser NULL."""
        sim = Simulation(
            simulation_id="test-null",
            container_id=None,  # Pode ser nulo
            config_path="/tmp/config.json",
            config_json='{}',
            status="expired",
            stopped_at=None,  # Pode ser nulo
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        assert sim.container_id is None
        assert sim.stopped_at is None

    def test_simulation_repr(self, test_db):
        """Testa representação da simulação."""
        sim = Simulation(
            simulation_id="test-repr",
            container_id="container-001",
            config_path="/tmp/config.json",
            config_json='{}',
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        repr_str = repr(sim)
        assert "test-repr" in repr_str
        assert "running" in repr_str

    def test_simulation_datetime_tracking(self, test_db):
        """Testa rastreamento de datas."""
        before_creation = datetime.utcnow()

        sim = Simulation(
            simulation_id="test-dates",
            container_id="container-001",
            config_path="/tmp/config.json",
            config_json='{}',
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        after_creation = datetime.utcnow()

        # created_at deve estar entre before e after
        assert before_creation <= sim.created_at <= after_creation
        assert sim.stopped_at is None  # Ainda não parou

    def test_simulation_update_status(self, test_db):
        """Testa atualização de status."""
        sim = Simulation(
            simulation_id="test-update",
            container_id="container-001",
            config_path="/tmp/config.json",
            config_json='{}',
            status="running",
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        # Atualizar status
        sim.status = "stopped"
        sim.stopped_at = datetime.utcnow()
        test_db.commit()

        # Verificar atualização
        refreshed = test_db.query(Simulation).filter(
            Simulation.simulation_id == "test-update"
        ).first()
        assert refreshed.status == "stopped"
        assert refreshed.stopped_at is not None

    def test_simulation_config_json_storage(self, test_db):
        """Testa armazenamento de configuração JSON."""
        config = '{"BROKER_URL": "test.mosquitto.org", "PORT": 1883}'

        sim = Simulation(
            simulation_id="test-config",
            container_id="container-001",
            config_path="/tmp/config.json",
            config_json=config,
            expires_at=datetime.utcnow() + timedelta(minutes=30)
        )
        test_db.add(sim)
        test_db.commit()

        # Recuperar e verificar
        refreshed = test_db.query(Simulation).filter(
            Simulation.simulation_id == "test-config"
        ).first()
        assert refreshed.config_json == config
