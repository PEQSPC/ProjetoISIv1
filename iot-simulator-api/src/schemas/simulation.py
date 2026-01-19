from typing import List, Optional
from pydantic import BaseModel, Field


class DataField(BaseModel):
    """Data field configuration for MQTT simulation."""
    NAME: str
    TYPE: str = Field(default="float", pattern="^(int|float|bool|math_expression|raw_values)$")
    MIN_VALUE: Optional[float] = None
    MAX_VALUE: Optional[float] = None
    MAX_STEP: Optional[float] = None
    INITIAL_VALUE: Optional[float] = None
    INCREASE_PROBABILITY: float = 0.5
    RETAIN_PROBABILITY: float = 0.0
    RESET_PROBABILITY: float = 0.0
    RESTART_ON_BOUNDARIES: bool = False


class Topic(BaseModel):
    """MQTT topic configuration."""
    TYPE: str = Field(pattern="^(single|multiple|list)$")
    PREFIX: str
    RANGE_START: Optional[int] = None
    RANGE_END: Optional[int] = None
    LIST: Optional[List[str]] = None
    TIME_INTERVAL: Optional[int] = None
    DATA: List[DataField]


class SimulationConfig(BaseModel):
    """Request model for creating a simulation."""
    BROKER_URL: str = "test.mosquitto.org"
    BROKER_PORT: int = 1883
    TIME_INTERVAL: int = 10
    TOPICS: List[Topic]
    duration_minutes: int = Field(default=30, ge=1, le=120)


class SimulationResponse(BaseModel):
    """Response model for simulation creation."""
    simulation_id: str
    pod_name: str
    status: str
    created_at: str
    expires_in_minutes: int
    mqtt_topic_hint: str
    config: dict


class SimulationListItem(BaseModel):
    """Response model for simulation list."""
    simulation_id: str
    status: str
    created_at: str
    duration_minutes: int


class SimulationDetailResponse(BaseModel):
    """Response model for simulation details."""
    simulation_id: str
    pod_name: str
    db_status: str
    k8s_status: str
    created_at: str
    config: dict
    logs: List[str]
