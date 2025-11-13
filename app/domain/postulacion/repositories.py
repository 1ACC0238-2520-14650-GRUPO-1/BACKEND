from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.postulacion.entities import Postulacion, PuestoPostulacion, PostulacionAggregate


class PostulacionRepository(ABC):
    """
    Define las operaciones de persistencia para las postulaciones.
    Este es el contrato que debe implementarse en la capa de infraestructura.
    """
    
    @abstractmethod
    def guardar(self, postulacion: PostulacionAggregate) -> UUID:
        """Guarda o actualiza una postulación y devuelve su ID"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, postulacion_id: UUID) -> Optional[PostulacionAggregate]:
        """Recupera una postulación por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_candidato(self, candidato_id: UUID) -> List[PostulacionAggregate]:
        """Recupera todas las postulaciones de un candidato"""
        pass
    
    @abstractmethod
    def obtener_por_puesto(self, puesto_id: UUID) -> List[PostulacionAggregate]:
        """Recupera todas las postulaciones a un puesto específico"""
        pass


class PuestoPostulacionRepository(ABC):
    """
    Define las operaciones de persistencia para los puestos de postulación.
    Este es el contrato que debe implementarse en la capa de infraestructura.
    """
    
    @abstractmethod
    def guardar(self, puesto: PuestoPostulacion) -> UUID:
        """Guarda o actualiza un puesto y devuelve su ID"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, puesto_id: UUID) -> Optional[PuestoPostulacion]:
        """Recupera un puesto por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_empresa(self, empresa_id: UUID) -> List[PuestoPostulacion]:
        """Recupera todos los puestos de una empresa"""
        pass