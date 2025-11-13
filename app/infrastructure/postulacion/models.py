from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum as SQLAEnum, JSON
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.infrastructure.database.connection import Base
from app.domain.postulacion.entities import EstadoPostulacionEnum


class PostulacionModel(Base):
    """Modelo simplificado de la tabla de postulaciones"""
    __tablename__ = "postulaciones"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    perfil_id = Column(String(36), nullable=False)  # UUID del perfil
    puesto_id = Column(Integer, nullable=False)  # Foreign key a puestos.id
    fecha_postulacion = Column(DateTime, nullable=False)
    estado = Column(SQLAEnum(EstadoPostulacionEnum, native_enum=False), nullable=False)
    resultado = Column(String(100), nullable=True)
    
    # Relaciones
    hitos = relationship("HitoModel", back_populates="postulacion", cascade="all, delete-orphan")


class HitoModel(Base):
    """Modelo simplificado de hitos"""
    __tablename__ = "hitos"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    postulacion_id = Column(Integer, ForeignKey("postulaciones.id"), nullable=False)
    fecha = Column(DateTime, nullable=False)
    descripcion = Column(Text, nullable=False)
    
    # Relaciones
    postulacion = relationship("PostulacionModel", back_populates="hitos")