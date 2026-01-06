from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from kubernetes import client, config
import json
import uuid
import os
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db, Simulation, Base, engine
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging
from fastapi.middleware.cors import CORSMiddleware

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Kubernetes Config
try:
    # Tries to load config from the cluster (when running in K8s)
    config.load_incluster_config()
    logger.info("Loaded in-cluster Kubernetes config.")
except config.ConfigException:
    try:
        # Fallback for local testing (reading ~/.kube/config)
        config.load_kube_config()
        logger.info("Loaded local kube-config.")
    except Exception as e:
        logger.error(f"Failed to load Kubernetes config: {e}")

# K8s Client
v1 = client.CoreV1Api()
NAMESPACE = os.getenv("K8s_NAMESPACE", "iot-sims") # Default namespace
SIMULATOR_IMAGE = os.getenv("SIMULATOR_IMAGE", "None") # Must be set in Deployment env
if SIMULATOR_IMAGE == "None":
    logger.warning("SIMULATOR_IMAGE environment variable is not set. Pods may fail to start.")
    raise ValueError("CRITICAL: SIMULATOR_IMAGE env var is missing!")
logger.info(f"Using simulator image: {SIMULATOR_IMAGE}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic (if any)
    logger.info("[STARTUP] API Initialized. Connected to Kubernetes.")
    yield
    # Shutdown logic
    logger.info("[SHUTDOWN] API Stopping.")

app = FastAPI(
    title="IoT Simulator API (K8s Edition)",
    description="API for creating ephemeral IoT simulation pods in Kubernetes",
    version="2.0.0",
    lifespan=lifespan
)

# DANGEROUS: Allow all CORS (for demo/development purposes)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite tudo (apenas para desenvolvimento/demo)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Pydantic Models ===
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
    pod_name: str
    status: str
    created_at: str
    expires_in_minutes: int
    mqtt_topic_hint: str
    config: dict

class SimulationListItem(BaseModel):
    simulation_id: str
    status: str
    created_at: str
    duration_minutes: int

# === Endpoints ===

@app.post("/simulations", response_model=SimulationResponse, status_code=201, tags=["Create Simulation"])
async def create_simulation(config: SimulationConfig, db: Session = Depends(get_db)):
    """Creates a new Kubernetes Pod running the simulator."""
    sim_id = str(uuid.uuid4())[:8]
    pod_name = f"sim-{sim_id}"
    
    # Prepare the config JSON string to inject into the pod
    simulator_config_dict = config.dict(exclude={'duration_minutes'})
    simulator_config_json = json.dumps(simulator_config_dict)

    # Calculate timestamps
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=config.duration_minutes)

    # === KUBERNETES POD DEFINITION ===
    pod_manifest = {
        "apiVersion": "v1",
        "kind": "Pod",
        "metadata": {
            "name": pod_name,
            "labels": {
                "app": "iot-simulator",
                "simulation_id": sim_id
            }
        },
        "spec": {
            "restartPolicy": "Never",
            "activeDeadlineSeconds": config.duration_minutes * 60, # AUTO-KILL Feature
            "containers": [{
                "name": "simulator",
                # Use your public image
                "image": f"{SIMULATOR_IMAGE}", 
                "imagePullPolicy": "IfNotPresent", 
                # We inject the config via an Environment Variable instead of a file volume
                # This is much simpler for K8s than managing temporary PVCs or ConfigMaps
                "env": [
                    {"name": "SIMULATOR_CONFIG_JSON", "value": simulator_config_json}
                    # NOTE: Your simulator python script needs to read os.environ['SIMULATOR_CONFIG_JSON']
                    # OR we can use an init-container to write it to a file if strictly required.
                ]
                # If your container strictly requires a file at /config/settings.json, 
                # let me know, and I will add the 'ConfigMap' logic here.
            }]
        }
    }

    try:
        # 1. Create Pod in Kubernetes
        v1.create_namespaced_pod(namespace=NAMESPACE, body=pod_manifest)
        logger.info(f"Created Pod {pod_name} in namespace {NAMESPACE}")
        logger.info(f"Pod created with simulator image: {SIMULATOR_IMAGE}")
        logger.debug(f"Pod Manifest: {pod_manifest}")

        # 2. Save to Database
        db_simulation = Simulation(
            simulation_id=sim_id,
            container_id=pod_name, # Storing Pod Name instead of Docker ID
            config_json=simulator_config_json,
            status="running",
            duration_minutes=config.duration_minutes,
            created_at=created_at,
            expires_at=expires_at
        )
        db.add(db_simulation)
        db.commit()
        db.refresh(db_simulation)

        return SimulationResponse(
            simulation_id=sim_id,
            pod_name=pod_name,
            status="running",
            created_at=created_at.isoformat(),
            expires_in_minutes=config.duration_minutes,
            mqtt_topic_hint=f"Check config for prefixes",
            config=simulator_config_dict
        )

    except client.exceptions.ApiException as e:
        logger.error(f"K8s API Error: {e}")
        raise HTTPException(500, f"Kubernetes failed to start pod: {e.reason}")
    except Exception as e:
        logger.error(f"General Error: {e}")
        raise HTTPException(500, f"Failed to start simulation: {str(e)}")

@app.get("/simulations", response_model=List[SimulationListItem], tags=["List Simulations"])
async def list_simulations(limit: int = 20, db: Session = Depends(get_db)):
    """List simulations from DB"""
    simulations = db.query(Simulation).order_by(Simulation.created_at.desc()).limit(limit).all()
    
    # Optional: You could ping K8s here to check real status of pods, 
    # but for speed we just return DB state.
    
    if not simulations:
        logger.info("No simulations found in database.")
        # return http status 204 No Content
        return {"status": "no_content"}
    else:
        logger.info(f"Retrieved {len(simulations)} simulations from database.")
        return [
            SimulationListItem(
                simulation_id=sim.simulation_id,
                status=sim.status,
            created_at=sim.created_at.isoformat(),
                duration_minutes=sim.duration_minutes
            )
            for sim in simulations
        ]
@app.get("/simulations/{sim_id}", tags=["Get Simulation Details"])
async def get_simulation(sim_id: str, db: Session = Depends(get_db)):
    """Get details and logs from Kubernetes"""
    simulation = db.query(Simulation).filter(Simulation.simulation_id == sim_id).first()
    if not simulation:
        raise HTTPException(404, "Simulation not found")

    pod_name = simulation.container_id
    pod_status = "unknown"
    logs = []

    # Query Kubernetes for real-time status
    try:
        pod = v1.read_namespaced_pod(name=pod_name, namespace=NAMESPACE)
        pod_status = pod.status.phase # Running, Succeeded, Failed, Pending
        
        # Get Logs
        log_response = v1.read_namespaced_pod_log(name=pod_name, namespace=NAMESPACE, tail_lines=50)
        logs = log_response.split('\n')
        
    except client.exceptions.ApiException as e:
        if e.status == 404:
            pod_status = "Deleted/Expired"
        else:
            pod_status = "K8s Error"
            logger.error(f"Error reading pod {pod_name}: {e}")

    return {
        "simulation_id": simulation.simulation_id,
        "pod_name": pod_name,
        "db_status": simulation.status,
        "k8s_status": pod_status,
        "created_at": simulation.created_at.isoformat(),
        "config": json.loads(simulation.config_json or "{}"),
        "logs": logs
    }

@app.delete("/simulations/{sim_id}", tags=["Stop Simulation"])
async def stop_simulation(sim_id: str, db: Session = Depends(get_db)):
    """Manually stop the pod"""
    simulation = db.query(Simulation).filter(Simulation.simulation_id == sim_id).first()
    if not simulation:
        raise HTTPException(404, "Simulation not found")

    pod_name = simulation.container_id

    try:
        v1.delete_namespaced_pod(
            name=pod_name, 
            namespace=NAMESPACE, 
            body=client.V1DeleteOptions(grace_period_seconds=0)
        )
        
        simulation.status = "stopped"
        simulation.stopped_at = datetime.utcnow()
        db.commit()
        
        return {"status": "success", "message": f"Pod {pod_name} deleted."}
        
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return {"status": "warning", "message": "Pod was already gone."}
        raise HTTPException(500, f"Failed to delete pod: {e.reason}")

@app.get("/health", tags=["Health Check"])
async def health(db: Session = Depends(get_db)):
    """Check K8s connection and DB"""
    k8s_status = "disconnected"
    db_status = "disconnected"

    # Check K8s
    try:
        v1.list_namespaced_pod(namespace=NAMESPACE, limit=1)
        k8s_status = "connected"
    except Exception as e:
        logger.error(f"Health Check K8s failed: {e}")

    # Check DB
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Health Check DB failed: {e}")

    return {
        "status": "healthy" if k8s_status == "connected" and db_status == "connected" else "degraded",
        "kubernetes": k8s_status,
        "database": db_status
    }