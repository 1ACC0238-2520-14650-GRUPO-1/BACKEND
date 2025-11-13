from sqlalchemy import Column, String, DateTime, ForeignKey, Text, JSON, Enum as SQLAEnum
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.infrastructure.database.connection import Base
from app.domain.perfil.entities import TipoPerfilEnum


class PerfilModel(Base):
    """Modelo de la tabla de perfiles"""
    __tablename__ = "perfiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    tipo_perfil = Column(SQLAEnum(TipoPerfilEnum), nullable=False)
    datos_personales = Column(JSON, nullable=False, default={})
    rol_asignado = Column(String(50), nullable=True)
    fecha_creacion = Column(DateTime, nullable=False)
    fecha_actualizacion = Column(DateTime, nullable=True)
    
    # Relaciones
    preferencias = relationship("PreferenciaModel", back_populates="perfil", cascade="all, delete-orphan")
    historial_cambios = relationship("HistorialCambioModel", back_populates="perfil", cascade="all, delete-orphan")


class PreferenciaModel(Base):
    """Modelo de la tabla de preferencias de perfil"""
    __tablename__ = "preferencias"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    perfil_id = Column(String(36), ForeignKey("perfiles.id"), nullable=False)
    tipo_preferencia = Column(String(100), nullable=False)
    valor = Column(Text, nullable=False)
    fecha_configuracion = Column(DateTime, nullable=False)
    
    # Relaciones
    perfil = relationship("PerfilModel", back_populates="preferencias")


class HistorialCambioModel(Base):
    """Modelo de la tabla de historial de cambios de perfil"""
    __tablename__ = "historial_cambios"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    perfil_id = Column(String(36), ForeignKey("perfiles.id"), nullable=False)
    tipo_cambio = Column(String(50), nullable=False)
    fecha = Column(DateTime, nullable=False)
    detalles = Column(JSON, nullable=False)
    
    # Relaciones
    perfil = relationship("PerfilModel", back_populates="historial_cambios")