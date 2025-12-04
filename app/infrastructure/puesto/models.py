from sqlalchemy import Column, String, Integer, Float, DateTime
from uuid import uuid4
from datetime import datetime

from app.infrastructure.database.connection import Base


class PuestoModel(Base):
    """Modelo de la tabla de puestos"""
    __tablename__ = "puestos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(300), nullable=False)
    empresa = Column(String(300), nullable=False)
    descripcion = Column(String(5000), nullable=False)
    ubicacion = Column(String(300), nullable=True)
    salario_min = Column(Float, nullable=True)
    salario_max = Column(Float, nullable=True)
    moneda = Column(String(10), nullable=False, default="MXN")
    tipo_contrato = Column(String(50), nullable=False, default="tiempo_completo")
    fecha_publicacion = Column(DateTime, nullable=False, default=datetime.now)
    fecha_cierre = Column(DateTime, nullable=True)
    estado = Column(String(50), nullable=False, default="abierto")


class PuestoMapeo(Base):
    """Tabla auxiliar para mapear UUIDs de dominio a IDs de BD"""
    __tablename__ = "puesto_mapeo"
    
    uuid_id = Column(String(36), primary_key=True)
    bd_id = Column(Integer, nullable=False)
