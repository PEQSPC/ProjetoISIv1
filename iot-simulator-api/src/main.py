from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth_router, simulations_router, health_router

# Configure Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# CORS Configuration
# In production: ALLOWED_ORIGINS="https://iot-simulator.local,https://yourdomain.com"
# In development: ALLOWED_ORIGINS="http://localhost:5173,http://localhost:3000"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")


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
logger.info(f"[CORS] Allowed origins: {ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
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
