from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.iam.entities import CuentaAggregate


class CuentaRepository(ABC):
    """
    Define las operaciones de persistencia para las cuentas IAM.
    Este es el contrato que debe implementarse en la capa de infraestructura.
    """
    
    @abstractmethod
    def guardar(self, cuenta_aggregate: CuentaAggregate) -> UUID:
        """Guarda o actualiza una cuenta y devuelve su ID"""
        pass
    
    @abstractmethod
    def obtener_por_id(self, cuenta_id: UUID) -> Optional[CuentaAggregate]:
        """Recupera una cuenta por su ID"""
        pass
    
    @abstractmethod
    def obtener_por_email(self, email: str) -> Optional[CuentaAggregate]:
        """Recupera una cuenta por su email"""
        pass
    
    @abstractmethod
    def verificar_email_existe(self, email: str) -> bool:
        """Verifica si un email ya está registrado"""
        pass
    
    @abstractmethod
    def listar_todas(self) -> List[CuentaAggregate]:
        """Lista todas las cuentas"""
        pass
