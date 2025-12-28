from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./simulations.db"

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
    container_id = Column(String, nullable=True)
    config_path = Column(String, nullable=False)
    config_json = Column(Text, nullable=False)  # JSON como texto
    status = Column(String, default="running")  # running, stopped, failed, expired
    created_at = Column(DateTime, default=datetime.utcnow)
    stopped_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    
    def __repr__(self):
        return f"<Simulation {self.simulation_id} - {self.status}>"

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Dependency para obter sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()