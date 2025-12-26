# main.py
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import docker
import json
import uuid
import tempfile
import threading
import time
import os
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db, Simulation, SessionLocal
from contextlib import asynccontextmanager
import asyncio

# Background task para verificar expirados
async def periodic_cleanup():
    """Roda cleanup a cada 5 minutos."""
    while True:
        try:
            cleanup_expired_simulations()
        except Exception as e:
            print(f"[PERIODIC-CLEANUP] Error: {e}")
        
        await asyncio.sleep(300)  # 5 minutos

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa ao startup e shutdown da API."""
    # STARTUP
    print("[STARTUP] Running initial cleanup...")
    cleanup_expired_simulations()
    
    # Iniciar background task
    task = asyncio.create_task(periodic_cleanup())
    print("[STARTUP] Background cleanup task started")
    
    yield  # API roda aqui
    
    # SHUTDOWN
    task.cancel()
    print("[SHUTDOWN] Background cleanup task stopped")


app = FastAPI(
    title="IoT Simulator API",
    description="API para criar simulações IoT com persistência",
    version="2.0.0",
    lifespan=lifespan
)

docker_client = docker.from_env()

# === Modelos Pydantic ===
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
    BROKER_URL: str = "test.mosquitto.org"
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
    config: dict

class SimulationListItem(BaseModel):
    simulation_id: str
    status: str
    created_at: str
    stopped_at: Optional[str]
    duration_minutes: int

def cleanup_expired_simulations():
    """Verifica e para simulações que já expiraram."""
    db = SessionLocal()
    
    try:
        # Buscar simulações running que já expiraram
        now = datetime.utcnow()
        expired = db.query(Simulation).filter(
            Simulation.status == "running",
            Simulation.expires_at <= now
        ).all()
        
        print(f"[CLEANUP] Found {len(expired)} expired simulations")
        
        for sim in expired:
            print(f"[CLEANUP] Stopping expired simulation {sim.simulation_id}")
            
            # Tentar parar container
            try:
                container = docker_client.containers.get(sim.container_id)
                container.stop(timeout=5)
                print(f"[CLEANUP] Container stopped: {sim.simulation_id}")
            except docker.errors.NotFound:
                print(f"[CLEANUP] Container already gone: {sim.simulation_id}")
            except Exception as e:
                print(f"[CLEANUP] Error stopping {sim.simulation_id}: {e}")
            
            # Atualizar BD
            sim.status = "expired"
            sim.stopped_at = datetime.utcnow()
            
            # Limpar ficheiro config
            if os.path.exists(sim.config_path):
                os.remove(sim.config_path)
        
        db.commit()
        print(f"[CLEANUP] Cleanup complete")
        
    except Exception as e:
        print(f"[CLEANUP] Error: {e}")
    finally:
        db.close()

# === Função Auto-Stop ===
def auto_stop_container(container_id: str, config_path: str, sim_id: str, duration_seconds: int):
    """Para container após duração."""
    time.sleep(duration_seconds)
    
    # Obter sessão BD
    db = SessionLocal()
    
    try:
        # Parar container
        try:
            container = docker_client.containers.get(container_id)
            print(f"[AUTO-STOP] Stopping simulation {sim_id}")
            container.stop(timeout=5)
        except docker.errors.NotFound:
            print(f"[AUTO-STOP] Container {sim_id} already stopped")
        except Exception as e:
            print(f"[AUTO-STOP] Error stopping {sim_id}: {e}")
        
        # Atualizar BD
        simulation = db.query(Simulation).filter(
            Simulation.simulation_id == sim_id
        ).first()
        
        if simulation:
            simulation.status = "expired"
            simulation.stopped_at = datetime.utcnow()
            db.commit()
            print(f"[AUTO-STOP] Updated DB for {sim_id}")
        
    finally:
        # Cleanup ficheiro
        if os.path.exists(config_path):
            os.remove(config_path)
            print(f"[AUTO-STOP] Cleaned config file for {sim_id}")
        
        db.close()

# === Endpoints ===
@app.post("/simulations", response_model=SimulationResponse, status_code=201,tags=["Create Simulation"])
async def create_simulation(config: SimulationConfig, db: Session = Depends(get_db)):
    """Cria nova simulação IoT"""
    sim_id = str(uuid.uuid4())[:8]
    
    # Preparar config para simulador
    simulator_config = config.dict(exclude={'duration_minutes'})
    
    # Criar ficheiro temporário
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(simulator_config, f, indent=2)
        config_path = f.name
    
    try:
        # Iniciar container
        container = docker_client.containers.run(
            "ghcr.io/damascenorafael/mqtt-simulator:sha-a73a2e8",
            command=["-f", "/config/settings.json"],
            name=f"sim-{sim_id}",
            volumes={config_path: {'bind': '/config/settings.json', 'mode': 'ro'}},
            detach=True,
            remove=True,
            labels={"simulation_id": sim_id}
        )
        # Calcular quando expira
        expires_at = datetime.utcnow() + timedelta(minutes=config.duration_minutes)
        
        # Guardar na BD
        db_simulation = Simulation(
            simulation_id=sim_id,
            container_id=container.id,
            config_path=config_path,
            config_json=json.dumps(config.dict()),
            status="running",
            duration_minutes=config.duration_minutes,
            expires_at=expires_at
        )
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)
        
        # Agendar auto-stop
        duration_seconds = config.duration_minutes * 60
        threading.Thread(
            target=auto_stop_container,
            args=(container.id, config_path, sim_id, duration_seconds),
            daemon=True
        ).start()
        
        return SimulationResponse(
            simulation_id=sim_id,
            container_id=container.id[:12],
            status="running",
            created_at=db_simulation.created_at.isoformat(),
            expires_in_minutes=config.duration_minutes,
            config=simulator_config
        )
        
    except docker.errors.ImageNotFound:
        if os.path.exists(config_path):
            os.remove(config_path)
        raise HTTPException(404, "Simulator image not found")
    except Exception as e:
        if os.path.exists(config_path):
            os.remove(config_path)
        raise HTTPException(500, f"Failed to start: {str(e)}")

@app.get("/simulations", response_model=List[SimulationListItem],tags=["List Simulations"])
async def list_simulations(
    status: Optional[str] = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Lista simulações (com filtro opcional por status)"""
    query = db.query(Simulation)
    
    if status:
        query = query.filter(Simulation.status == status)
    
    simulations = query.order_by(Simulation.created_at.desc()).limit(limit).all()
    
    return [
        SimulationListItem(
            simulation_id=sim.simulation_id,
            status=sim.status,
            created_at=sim.created_at.isoformat(),
            stopped_at=sim.stopped_at.isoformat() if sim.stopped_at else None,
            duration_minutes=sim.duration_minutes
        )
        for sim in simulations
    ]

@app.get("/simulations/{sim_id}", tags=["Get Simulation Details"])
async def get_simulation(sim_id: str, db: Session = Depends(get_db)):
    """Detalhes de simulação específica"""
    simulation = db.query(Simulation).filter(
        Simulation.simulation_id == sim_id
    ).first()
    
    if not simulation:
        raise HTTPException(404, "Simulation not found")
    
    # Tentar obter logs do container se ainda estiver ativo
    logs = None
    container_status = simulation.status
    
    if simulation.container_id and simulation.status == "running":
        try:
            container = docker_client.containers.get(simulation.container_id)
            container_status = container.status
            logs = container.logs(tail=50).decode('utf-8').split('\n')
        except docker.errors.NotFound:
            container_status = "stopped"
            # Atualizar BD
            simulation.status = "stopped"
            simulation.stopped_at = datetime.utcnow()
            db.commit()
    
    return {
        "simulation_id": simulation.simulation_id,
        "container_id": simulation.container_id[:12] if simulation.container_id else None,
        "status": container_status,
        "created_at": simulation.created_at.isoformat(),
        "stopped_at": simulation.stopped_at.isoformat() if simulation.stopped_at else None,
        "duration_minutes": simulation.duration_minutes,
        "config": json.loads(simulation.config_json),
        "logs": logs
    }

@app.delete("/simulations/{sim_id}",tags=["Stop Simulation"])
async def stop_simulation(sim_id: str, db: Session = Depends(get_db)):
    """Para simulação manualmente"""
    simulation = db.query(Simulation).filter(
        Simulation.simulation_id == sim_id
    ).first()
    
    if not simulation:
        raise HTTPException(404, "Simulation not found")
    
    if simulation.status in ["stopped", "expired", "failed"]:
        raise HTTPException(400, f"Simulation already {simulation.status}")
    
    # Parar container
    try:
        container = docker_client.containers.get(simulation.container_id)
        container.stop(timeout=5)
    except docker.errors.NotFound:
        pass  # Já parou
    except Exception as e:
        print(f"Error stopping container: {e}")
    
    # Atualizar BD
    simulation.status = "stopped"
    simulation.stopped_at = datetime.utcnow()
    db.commit()
    
    # Cleanup ficheiro
    if os.path.exists(simulation.config_path):
        os.remove(simulation.config_path)
    
    return {
        "status": "stopped",
        "simulation_id": sim_id,
        "stopped_at": simulation.stopped_at.isoformat()
    }

@app.get("/stats", tags=["Get Statistics"])
async def get_stats(db: Session = Depends(get_db)):
    """Estatísticas gerais"""
    total = db.query(Simulation).count()
    running = db.query(Simulation).filter(Simulation.status == "running").count()
    stopped = db.query(Simulation).filter(Simulation.status == "stopped").count()
    expired = db.query(Simulation).filter(Simulation.status == "expired").count()
    
    return {
        "total_simulations": total,
        "running": running,
        "stopped": stopped,
        "expired": expired
    }

@app.get("/", tags=["Root"])
async def root(db: Session = Depends(get_db)):
    running_count = db.query(Simulation).filter(Simulation.status == "running").count()
    
    return {
        "service": "IoT Simulator API",
        "version": "2.0.0",
        "docs": "/docs",
        "database": "sqlite",
        "active_simulations": running_count
    }

@app.get("/health", tags=["Health Check"])
async def health():
    """Health check"""
    try:
        docker_client.ping()
        docker_status = "connected"
    except:
        docker_status = "disconnected"
    
    # Verificar BD
    try:
        
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        db_status = "connected"
    except:
        db_status = "disconnected"
    
    healthy = docker_status == "connected" and db_status == "connected"
    
    return {
        "status": "healthy" if healthy else "unhealthy",
        "docker": docker_status,
        "database": db_status
    }
