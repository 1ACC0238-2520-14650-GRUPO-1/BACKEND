from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.metrica.entities import MetricaAggregate


class MetricaRepository(ABC):
    """
    Define las operaciones de persistencia para las métricas de postulantes.
    Este es el contrato que debe implementarse en la capa de infraestructura.
    """
    
    @abstractmethod
    def guardar(self, metrica_aggregate: MetricaAggregate) -> UUID:
        """Guarda o actualiza una métrica y devuelve el ID del perfil asociado"""
        pass
    
    @abstractmethod
    def obtener_por_postulante(self, postulante_id: UUID) -> Optional[MetricaAggregate]:
        """Recupera las métricas de un postulante por su ID"""
        pass