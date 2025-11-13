from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .entities import PuestoAggregate


class PuestoRepository(ABC):
    """Interfaz del repositorio para puestos"""
    
    @abstractmethod
    def guardar(self, puesto_aggregate: PuestoAggregate) -> UUID:
        """Guarda un puesto y retorna su ID"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, puesto_id: UUID) -> Optional[PuestoAggregate]:
        """Obtiene un puesto por su ID"""
        pass
    
    @abstractmethod
    def listar_por_empresa(self, empresa_id: UUID) -> List[PuestoAggregate]:
        """Lista los puestos de una empresa específica"""
        pass
    
    @abstractmethod
    def listar_por_estado(self, estado: str) -> List[PuestoAggregate]:
        """Lista los puestos según su estado (abierto/cerrado)"""
        pass
    
    @abstractmethod
    def listar_todos(self) -> List[PuestoAggregate]:
        """Lista todos los puestos"""
        pass
    
    @abstractmethod
    def eliminar(self, puesto_id: UUID) -> bool:
        """Elimina un puesto por su ID"""
        pass