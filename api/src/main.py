# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import docker
import json
import uuid
import tempfile
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="IoT Simulator API",
    description="API para criar simulações IoT sob demanda",
    version="1.0.0"
)

docker_client = docker.from_env()

# Modelos Pydantic (seguem estrutura do mqtt-simulator)
class DataField(BaseModel):
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
    TYPE: str = Field(pattern="^(single|multiple|list)$")
    PREFIX: str
    RANGE_START: Optional[int] = None
    RANGE_END: Optional[int] = None
    LIST: Optional[List[str]] = None
    TIME_INTERVAL: Optional[int] = None
    DATA: List[DataField]

class SimulationConfig(BaseModel):
    BROKER_URL: str = "localhost"
    BROKER_PORT: int = 1883
    TIME_INTERVAL: int = 10
    TOPICS: List[Topic]
    duration_minutes: int = Field(default=30, ge=1, le=120)

class SimulationResponse(BaseModel):
    simulation_id: str
    container_id: str
    status: str
    created_at: str
    expires_in_minutes: int

# Armazenar simulações ativas
active_simulations = {}

@app.post("/simulations", response_model=SimulationResponse, status_code=201)
async def create_simulation(config: SimulationConfig):
    """Cria nova simulação IoT"""
    sim_id = str(uuid.uuid4())[:8]
    
    # Preparar config para o simulador
    simulator_config = config.dict(exclude={'duration_minutes'})
    
    # Criar ficheiro temporário com config
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(simulator_config, f, indent=2)
        config_path = f.name
    
    # Iniciar container
    try:
        container = docker_client.containers.run(
            "ghcr.io/damascenorafael/mqtt-simulator:sha-a73a2e8",
            command=["-f", "/config/settings.json"],
            name=f"sim-{sim_id}",
            volumes={config_path: {'bind': '/config/settings.json', 'mode': 'ro'}},
            detach=True,
            remove=True,
            labels={"simulation_id": sim_id}
        )

        
        # Guardar info
        active_simulations[sim_id] = {
            "container_id": container.id,
            "config_path": config_path,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return SimulationResponse(
            simulation_id=sim_id,
            container_id=container.id[:12],
            status="running",
            created_at=datetime.utcnow().isoformat(),
            expires_in_minutes=config.duration_minutes
        )
        
    except docker.errors.ImageNotFound:
        raise HTTPException(404, "Simulator image not found. Run: docker pull ghcr.io/damascenorafael/mqtt-simulator:sha-a73a2e8")
    except Exception as e:
        raise HTTPException(500, f"Failed to start simulator: {str(e)}")

@app.get("/simulations")
async def list_simulations():
    """Lista simulações ativas"""
    simulations = []
    
    for sim_id, info in list(active_simulations.items()):
        try:
            container = docker_client.containers.get(info["container_id"])
            simulations.append({
                "simulation_id": sim_id,
                "container_id": info["container_id"][:12],
                "status": container.status,
                "created_at": info["created_at"]
            })
        except docker.errors.NotFound:
            # Container já não existe
            del active_simulations[sim_id]
    
    return {"simulations": simulations, "total": len(simulations)}

@app.get("/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    """Detalhes de simulação específica"""
    if sim_id not in active_simulations:
        raise HTTPException(404, "Simulation not found")
    
    info = active_simulations[sim_id]
    
    try:
        container = docker_client.containers.get(info["container_id"])
        logs = container.logs(tail=20).decode('utf-8')
        
        return {
            "simulation_id": sim_id,
            "container_id": info["container_id"][:12],
            "status": container.status,
            "created_at": info["created_at"],
            "logs": logs.split('\n')
        }
    except docker.errors.NotFound:
        raise HTTPException(404, "Container not found")

@app.delete("/simulations/{sim_id}")
async def stop_simulation(sim_id: str):
    """Para simulação"""
    if sim_id not in active_simulations:
        raise HTTPException(404, "Simulation not found")
    
    info = active_simulations[sim_id]
    
    try:
        container = docker_client.containers.get(info["container_id"])
        container.stop(timeout=5)
        
        # Cleanup
        del active_simulations[sim_id]
        
        return {"status": "stopped", "simulation_id": sim_id}
    except docker.errors.NotFound:
        del active_simulations[sim_id]
        raise HTTPException(404, "Container already stopped")

@app.get("/")
async def root():
    return {
        "service": "IoT Simulator API",
        "version": "1.0.0",
        "docs": "/docs",
        "active_simulations": len(active_simulations)
    }

@app.get("/health")
async def health():
    """Health check"""
    try:
        docker_client.ping()
        return {"status": "healthy", "docker": "connected"}
    except:
        return {"status": "unhealthy", "docker": "disconnected"}