from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from database import get_db
from services.k8s_service import get_k8s_service, K8sService

router = APIRouter(tags=["Health Check"])


@router.get("/health")
async def health(
    db: Session = Depends(get_db),
    k8s: K8sService = Depends(get_k8s_service)
):
    """Check K8s connection and DB - PUBLIC endpoint for K8s probes."""
    k8s_status = "connected" if k8s.check_connection() else "disconnected"

    db_status = "disconnected"
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        pass

    return {
        "status": "healthy" if k8s_status == "connected" and db_status == "connected" else "degraded",
        "kubernetes": k8s_status,
        "database": db_status
    }
