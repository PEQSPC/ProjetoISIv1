from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Ensure the 'db' folder exists, otherwise sqlite fails
if not os.path.exists("./db"):
    os.makedirs("./db")

SQLALCHEMY_DATABASE_URL = "sqlite:///./db/simulations.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Simulation(Base):
    __tablename__ = "simulations"
    
    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String, unique=True, index=True, nullable=False)
    
    # In K8s, this will store the Pod Name (e.g., "sim-abc-123")
    container_id = Column(String, nullable=True)
    
    
    config_path = Column(String, nullable=True)
    
    config_json = Column(Text, nullable=False)  # JSON stored as text
    status = Column(String, default="running")
    created_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    def __repr__(self):
        return f"<Simulation {self.simulation_id} - {self.status}>"

# Create tables
Base.metadata.create_all(bind=engine)

# Dependency to get session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()