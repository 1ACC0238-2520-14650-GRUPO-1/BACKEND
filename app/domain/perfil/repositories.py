from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.perfil.entities import PerfilAggregate, TipoPerfilEnum


class PerfilRepository(ABC):
    """
    Define las operaciones de persistencia para los perfiles.
    Este es el contrato que debe implementarse en la capa de infraestructura.
    """
    
    @abstractmethod
    def guardar(self, perfil_aggregate: PerfilAggregate) -> UUID:
        """Guarda o actualiza un perfil y devuelve su ID"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, perfil_id: UUID) -> Optional[PerfilAggregate]:
        """Recupera un perfil por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_tipo(self, tipo_perfil: TipoPerfilEnum) -> List[PerfilAggregate]:
        """Recupera todos los perfiles de un tipo específico"""
        pass