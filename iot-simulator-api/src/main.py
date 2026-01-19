from contextlib import asynccontextmanager
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, simulations_router, health_router

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("[STARTUP] API Initialized.")
    yield
    logger.info("[SHUTDOWN] API Stopping.")


# === Application ===
app = FastAPI(
    title="IoT Simulator API (K8s Edition)",
    description="API for creating ephemeral IoT simulation pods in Kubernetes",
    version="2.0.0",
    lifespan=lifespan
)

# === Middleware ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restringir em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Routers ===
app.include_router(auth_router)
app.include_router(simulations_router)
app.include_router(health_router)


# === Root Endpoint ===
@app.get("/", tags=["Root"])
async def read_root():
    """Welcome endpoint with API info."""
    return {
        "message": "Welcome to the IoT Simulator API (K8s Edition)",
        "docs": "/docs",
        "version": "2.0.0"
    }
