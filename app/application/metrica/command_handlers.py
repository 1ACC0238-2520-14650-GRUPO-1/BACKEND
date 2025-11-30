from dataclasses import dataclass
from typing import Dict, Any
from uuid import UUID

from app.domain.common import Command, CommandHandler, EventHandler
from app.domain.metrica.entities import MetricaAggregate, MetricaRegistro
from app.domain.metrica.repositories import MetricaRepository
from app.domain.iam.entities import CuentaAggregate

@dataclass
class RecalcularMetricasCommand(Command):
    """Comando para recalcular las métricas de un postulante"""
    cuenta_id: UUID


class RecalcularMetricasHandler(CommandHandler):
    """
    Manejador del comando para recalcular métricas
    """
    
    def __init__(self, metrica_repository: MetricaRepository):
        self.metrica_repository = metrica_repository
    
    def handle(self, command: RecalcularMetricasCommand) -> Dict[str, Any]:
        """
        Maneja el comando para recalcular métricas
        
        Nota: Este manejador ahora recalcula las métricas directamente desde el estado actual 
        de las postulaciones, en lugar de actualizar un registro almacenado. Las métricas
        son calculadas en tiempo real y no se persisten como estado.
        """
        # Obtener el agregado de métricas calculado en tiempo real
        metrica_aggregate = self.metrica_repository.obtener_por_postulante(command.cuenta_id)
        
        if not metrica_aggregate:
            # Si no hay postulaciones para esta cuenta, devolver valores por defecto
            return {
                "cuenta_id": str(command.cuenta_id),
                "total_postulaciones": 0,
                "total_entrevistas": 0,
                "total_exitos": 0,
                "total_rechazos": 0,
                "tasa_exito": 0.0
            }
        
        # Devolver las métricas calculadas
        return {
            "cuenta_id": str(metrica_aggregate.metrica_registro.cuenta_id),
            "total_postulaciones": metrica_aggregate.metrica_registro.total_postulaciones,
            "total_entrevistas": metrica_aggregate.metrica_registro.total_entrevistas,
            "total_exitos": metrica_aggregate.metrica_registro.total_exitos,
            "total_rechazos": metrica_aggregate.metrica_registro.total_rechazos,
            "tasa_exito": metrica_aggregate.metrica_registro.tasa_exito
        }


# Manejadores de eventos del bounded context de Postulación
@dataclass
class PostulacionCreada:
    """Evento que se emite cuando se crea una nueva postulación"""
    postulacion_id: UUID
    candidato_id: UUID


class OnPostulacionCreadaHandler(EventHandler):
    """
    Manejador del evento PostulacionCreada para actualizar métricas
    """
    
    def __init__(self, metrica_repository: MetricaRepository):
        self.metrica_repository = metrica_repository
    
    def handle(self, event: PostulacionCreada) -> None:
        """
        Maneja el evento de postulación creada
        
        Nota: Con el nuevo enfoque de métricas calculadas en tiempo real, este handler
        no necesita realizar ninguna acción, ya que las métricas se calculan bajo demanda
        cuando son consultadas. Se mantiene por compatibilidad con la arquitectura de eventos.
        """
        # Las métricas ahora se calculan en tiempo real bajo demanda, 
        # no hay necesidad de actualizar ningún registro almacenado


@dataclass
class EstadoPostulacionActualizado:
    """Evento que se emite cuando cambia el estado de una postulación"""
    postulacion_id: UUID
    candidato_id: UUID
    estado_anterior: str
    estado_nuevo: str


class OnEstadoPostulacionActualizadoHandler(EventHandler):
    """
    Manejador del evento EstadoPostulacionActualizado para actualizar métricas
    """
    
    def __init__(self, metrica_repository: MetricaRepository):
        self.metrica_repository = metrica_repository
    
    def handle(self, event: EstadoPostulacionActualizado) -> None:
        """
        Maneja el evento de actualización de estado
        
        Nota: Con el nuevo enfoque de métricas calculadas en tiempo real, este handler
        no necesita realizar ninguna acción, ya que los cambios de estado se reflejan 
        automáticamente cuando se consultan las métricas. Se mantiene por compatibilidad
        con la arquitectura de eventos.
        """
        # Las métricas ahora se calculan en tiempo real basadas en el estado actual
        # de las postulaciones, por lo que no necesitamos mantener ningún registro
        # de métricas actualizado


@dataclass
class PostulacionEliminada:
    """Evento que se emite cuando se elimina una postulación"""
    postulacion_id: UUID
    candidato_id: UUID


class OnPostulacionEliminadaHandler(EventHandler):
    """
    Manejador del evento PostulacionEliminada para actualizar métricas
    """
    
    def __init__(self, metrica_repository: MetricaRepository):
        self.metrica_repository = metrica_repository
    
    def handle(self, event: PostulacionEliminada) -> None:
        """
        Maneja el evento de postulación eliminada
        
        Nota: Con el nuevo enfoque de métricas calculadas en tiempo real, este handler
        no necesita realizar ninguna acción, ya que la eliminación de la postulación
        se refleja automáticamente cuando se consultan las métricas. Se mantiene por
        compatibilidad con la arquitectura de eventos.
        """
        # Las métricas ahora se calculan en tiempo real, por lo que la eliminación
        # de una postulación se refleja automáticamente al calcular métricas