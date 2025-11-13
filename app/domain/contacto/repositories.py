from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.contacto.entities import ContactoAggregate


class ContactoRepository(ABC):
    """
    Define las operaciones de persistencia para los contactos de postulación.
    Este es el contrato que debe implementarse en la capa de infraestructura.
    """
    
    @abstractmethod
    def guardar(self, contacto: ContactoAggregate) -> UUID:
        """Guarda o actualiza un contacto y devuelve su ID"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, contacto_id: UUID) -> Optional[ContactoAggregate]:
        """Recupera un contacto por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_postulacion(self, postulacion_id: UUID) -> List[ContactoAggregate]:
        """Recupera todos los contactos asociados a una postulación"""
        pass