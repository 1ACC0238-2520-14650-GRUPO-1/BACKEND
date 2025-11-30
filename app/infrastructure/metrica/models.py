from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from uuid import uuid4

from app.infrastructure.database.connection import Base

# NOTA: Estos modelos se mantienen por compatibilidad con el esquema de base de datos,
# pero ya no se utilizan activamente. Las métricas ahora se calculan en tiempo real
# a partir del estado de las postulaciones y no se almacenan en la base de datos.


class MetricaRegistroModel(Base):
    """Modelo de la tabla de métricas de postulantes"""
    __tablename__ = "metricas_registro"
    
    cuenta_id = Column(String(36), primary_key=True)
    total_postulaciones = Column(Integer, nullable=False, default=0)
    total_entrevistas = Column(Integer, nullable=False, default=0)
    total_exitos = Column(Integer, nullable=False, default=0)
    total_rechazos = Column(Integer, nullable=False, default=0)
    tasa_exito = Column(Float, nullable=False, default=0.0)
    
    # Relaciones
    logros = relationship("LogroModel", back_populates="metrica", cascade="all, delete-orphan")


class LogroModel(Base):
    """Modelo de la tabla de logros de gamificación"""
    __tablename__ = "logros"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    cuenta_id = Column(String(36), ForeignKey("metricas_registro.cuenta_id"), nullable=False)
    nombre_logro = Column(String(100), nullable=False)
    umbral = Column(Integer, nullable=False)
    fecha_obtencion = Column(DateTime, nullable=False)
    
    # Relaciones
    metrica = relationship("MetricaRegistroModel", back_populates="logros")