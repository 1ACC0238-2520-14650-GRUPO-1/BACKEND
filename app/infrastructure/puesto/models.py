from sqlalchemy import Column, String, Integer
from uuid import uuid4

from app.infrastructure.database.connection import Base


class PuestoModel(Base):
    """Modelo de la tabla de puestos"""
    __tablename__ = "puestos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(300), nullable=False)
    empresa = Column(String(300), nullable=False)
    descripcion = Column(String(5000), nullable=False)
    estado = Column(String(50), nullable=False, default="abierto")


class PuestoMapeo(Base):
    """Tabla auxiliar para mapear UUIDs de dominio a IDs de BD"""
    __tablename__ = "puesto_mapeo"
    
    uuid_id = Column(String(36), primary_key=True)
    bd_id = Column(Integer, nullable=False)