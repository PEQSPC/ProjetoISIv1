import json
import uuid
from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db, Simulation, User
from schemas import SimulationConfig, SimulationResponse, SimulationListItem, SimulationDetailResponse
from services.k8s_service import get_k8s_service, K8sService
from auth import get_current_user_from_token, oauth2_scheme

router = APIRouter(prefix="/simulations", tags=["Simulations"])


# === Dependency ===
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token."""
    return get_current_user_from_token(token, db)


# === Endpoints ===

@router.post("", response_model=SimulationResponse, status_code=201)
async def create_simulation(
    config: SimulationConfig,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    k8s: K8sService = Depends(get_k8s_service)
):
    """Creates a new Kubernetes Pod running the simulator."""
    sim_id = str(uuid.uuid4())[:8]
    pod_name = f"sim-{sim_id}"

    # Prepare the config JSON string
    simulator_config_dict = config.dict(exclude={'duration_minutes'})
    simulator_config_json = json.dumps(simulator_config_dict)

    # Calculate timestamps
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=config.duration_minutes)

    try:
        # Create Pod in Kubernetes
        k8s.create_pod(
            pod_name=pod_name,
            sim_id=sim_id,
            config_json=simulator_config_json,
            duration_minutes=config.duration_minutes
        )

        # Save to Database
        db_simulation = Simulation(
            simulation_id=sim_id,
            container_id=pod_name,
            config_json=simulator_config_json,
            status="running",
            duration_minutes=config.duration_minutes,
            created_at=created_at,
            expires_at=expires_at,
            user_id=current_user.id
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
            mqtt_topic_hint="Check config for prefixes",
            config=simulator_config_dict
        )

    except Exception as e:
        raise HTTPException(500, f"Failed to start simulation: {str(e)}")


@router.get("", response_model=List[SimulationListItem])
async def list_simulations(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List simulations - admins see all, users see only their own."""
    query = db.query(Simulation).order_by(Simulation.created_at.desc())

    # Role-based filtering
    if current_user.role != "admin":
        query = query.filter(Simulation.user_id == current_user.id)

    simulations = query.limit(limit).all()

    return [
        SimulationListItem(
            simulation_id=sim.simulation_id,
            status=sim.status,
            created_at=sim.created_at.isoformat(),
            duration_minutes=sim.duration_minutes
        )
        for sim in simulations
    ]


@router.get("/{sim_id}", response_model=SimulationDetailResponse)
async def get_simulation(
    sim_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    k8s: K8sService = Depends(get_k8s_service)
):
    """Get details and logs from Kubernetes - owner or admin only."""
    simulation = db.query(Simulation).filter(Simulation.simulation_id == sim_id).first()
    if not simulation:
        raise HTTPException(404, "Simulation not found")

    # Authorization check
    if current_user.role != "admin" and simulation.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to view this simulation")

    pod_name = simulation.container_id
    pod_status, logs = k8s.get_pod_status(pod_name)

    return SimulationDetailResponse(
        simulation_id=simulation.simulation_id,
        pod_name=pod_name,
        db_status=simulation.status,
        k8s_status=pod_status,
        created_at=simulation.created_at.isoformat(),
        config=json.loads(simulation.config_json or "{}"),
        logs=logs
    )


@router.delete("/{sim_id}")
async def stop_simulation(
    sim_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    k8s: K8sService = Depends(get_k8s_service)
):
    """Manually stop the pod - owner or admin only."""
    simulation = db.query(Simulation).filter(Simulation.simulation_id == sim_id).first()
    if not simulation:
        raise HTTPException(404, "Simulation not found")

    # Authorization check
    if current_user.role != "admin" and simulation.user_id != current_user.id:
        raise HTTPException(403, "Not authorized to stop this simulation")

    pod_name = simulation.container_id

    try:
        deleted = k8s.delete_pod(pod_name)

        simulation.status = "stopped"
        simulation.stopped_at = datetime.utcnow()
        db.commit()

        if deleted:
            return {"status": "success", "message": f"Pod {pod_name} deleted."}
        else:
            return {"status": "warning", "message": "Pod was already gone."}

    except Exception as e:
        raise HTTPException(500, f"Failed to delete pod: {str(e)}")
