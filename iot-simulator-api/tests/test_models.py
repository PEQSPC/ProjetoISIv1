"""
Testes para modelos Pydantic da API.
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import DataField, Topic, SimulationConfig, SimulationResponse


class TestDataFieldModel:
    """Testes para o modelo DataField."""

    def test_create_valid_data_field(self):
        """Testa criação de campo válido."""
        field = DataField(
            NAME="temperature",
            TYPE="float",
            MIN_VALUE=15.0,
            MAX_VALUE=30.0
        )
        assert field.NAME == "temperature"
        assert field.TYPE == "float"

    def test_data_field_default_type(self):
        """Testa tipo padrão."""
        field = DataField(NAME="test")
        assert field.TYPE == "float"

    def test_data_field_invalid_type(self):
        """Testa validação de tipo."""
        with pytest.raises(ValidationError):
            DataField(
                NAME="test",
                TYPE="invalid_type"
            )

    def test_data_field_valid_types(self):
        """Testa tipos válidos."""
        valid_types = ["int", "float", "bool", "math_expression", "raw_values"]
        for type_name in valid_types:
            field = DataField(NAME="test", TYPE=type_name)
            assert field.TYPE == type_name


class TestTopicModel:
    """Testes para o modelo Topic."""

    def test_create_valid_topic(self):
        """Testa criação de tópico válido."""
        topic = Topic(
            TYPE="single",
            PREFIX="sensor/temperature",
            DATA=[
                DataField(NAME="value", TYPE="float")
            ]
        )
        assert topic.TYPE == "single"
        assert topic.PREFIX == "sensor/temperature"

    def test_topic_invalid_type(self):
        """Testa validação de tipo de tópico."""
        with pytest.raises(ValidationError):
            Topic(
                TYPE="invalid",
                PREFIX="sensor/temp",
                DATA=[]
            )

    def test_topic_valid_types(self):
        """Testa tipos válidos de tópico."""
        valid_types = ["single", "multiple", "list"]
        for topic_type in valid_types:
            topic = Topic(
                TYPE=topic_type,
                PREFIX="sensor/test",
                DATA=[DataField(NAME="value")]
            )
            assert topic.TYPE == topic_type


class TestSimulationConfigModel:
    """Testes para o modelo SimulationConfig."""

    def test_create_valid_config(self):
        """Testa criação de configuração válida."""
        config = SimulationConfig(
            BROKER_URL="test.mosquitto.org",
            BROKER_PORT=1883,
            TIME_INTERVAL=10,
            duration_minutes=30,
            TOPICS=[
                Topic(
                    TYPE="single",
                    PREFIX="sensor/temp",
                    DATA=[DataField(NAME="value")]
                )
            ]
        )
        assert config.BROKER_URL == "test.mosquitto.org"
        assert config.duration_minutes == 30

    def test_simulation_config_default_broker(self):
        """Testa broker padrão."""
        config = SimulationConfig(
            BROKER_PORT=1883,
            TIME_INTERVAL=10,
            duration_minutes=30,
            TOPICS=[
                Topic(
                    TYPE="single",
                    PREFIX="sensor/temp",
                    DATA=[DataField(NAME="value")]
                )
            ]
        )
        assert config.BROKER_URL == "test.mosquitto.org"

    def test_simulation_config_duration_validation_min(self):
        """Testa validação mínima de duração."""
        with pytest.raises(ValidationError):
            SimulationConfig(
                BROKER_URL="test.mosquitto.org",
                BROKER_PORT=1883,
                TIME_INTERVAL=10,
                duration_minutes=0,  # < 1 (mínimo)
                TOPICS=[]
            )

    def test_simulation_config_duration_validation_max(self):
        """Testa validação máxima de duração."""
        with pytest.raises(ValidationError):
            SimulationConfig(
                BROKER_URL="test.mosquitto.org",
                BROKER_PORT=1883,
                TIME_INTERVAL=10,
                duration_minutes=121,  # > 120 (máximo)
                TOPICS=[]
            )

    def test_simulation_config_valid_duration_range(self):
        """Testa duração válida."""
        for duration in [1, 30, 60, 120]:
            config = SimulationConfig(
                BROKER_URL="test.mosquitto.org",
                BROKER_PORT=1883,
                TIME_INTERVAL=10,
                duration_minutes=duration,
                TOPICS=[
                    Topic(
                        TYPE="single",
                        PREFIX="sensor/temp",
                        DATA=[DataField(NAME="value")]
                    )
                ]
            )
            assert config.duration_minutes == duration


class TestSimulationResponseModel:
    """Testes para o modelo SimulationResponse."""

    def test_create_response(self):
        """Testa criação de resposta."""
        response = SimulationResponse(
            simulation_id="test-001",
            container_id="container-abc",
            status="running",
            created_at="2026-01-06T00:00:00",
            expires_in_minutes=30,
            config={"key": "value"}
        )
        assert response.simulation_id == "test-001"
        assert response.status == "running"
