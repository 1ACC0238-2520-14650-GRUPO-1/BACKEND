from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import func, case, and_

from app.domain.metrica.entities import (
    MetricaRegistro, Logro, MetricaAggregate
)
from app.domain.metrica.repositories import MetricaRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.postulacion.models import PostulacionModel


class MetricaRepositoryImpl(MetricaRepository):
    """
    Implementación del repositorio de métricas con SQLAlchemy
    Esta implementación no almacena datos, sino que calcula métricas en tiempo real
    basándose en los datos de postulaciones. Funciona como una capa de proyección
    que calcula métricas bajo demanda a partir del estado actual de las postulaciones.
    """
    
    def __init__(self):
        """Inicializador del repositorio de métricas"""
        # No necesitamos inicializar ningún modelo ya que calculamos en tiempo real
        pass
    
    def obtener_por_postulante(self, postulante_id: UUID) -> Optional[MetricaAggregate]:
        """Calcula las métricas de un postulante en tiempo real basado en sus postulaciones"""
        db = SessionLocal()
        try:
            # Contar el total de postulaciones
            total_postulaciones = db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id)
            ).scalar() or 0
            
            # No hay postulaciones, retornar métricas en ceros
            if total_postulaciones == 0:
                return MetricaAggregate(
                    metrica_registro=MetricaRegistro(
                        perfil_id=postulante_id,
                        total_postulaciones=0,
                        total_entrevistas=0,
                        total_exitos=0,
                        total_rechazos=0,
                        tasa_exito=0.0
                    ),
                    lista_logros=[]
                )
            
            # Contar entrevistas
            total_entrevistas = db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id),
                PostulacionModel.estado == "entrevista"
            ).scalar() or 0
            
            # Contar ofertas (éxitos)
            total_exitos = db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id),
                PostulacionModel.estado == "oferta"
            ).scalar() or 0
            
            # Contar rechazos
            total_rechazos = db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id),
                PostulacionModel.estado.in_(["rechazado", "rechazo"])
            ).scalar() or 0
            
            # Calcular tasa de éxito (ofertas sobre total de postulaciones)
            tasa_exito = (total_exitos / total_postulaciones) * 100 if total_postulaciones > 0 else 0.0
            
            # Crear métricas
            metrica_registro = MetricaRegistro(
                perfil_id=postulante_id,
                total_postulaciones=total_postulaciones,
                total_entrevistas=total_entrevistas,
                total_exitos=total_exitos,
                total_rechazos=total_rechazos,
                tasa_exito=tasa_exito
            )
            
            # Determinar logros basados en métricas
            lista_logros = self._calcular_logros(
                postulante_id, 
                total_postulaciones, 
                total_entrevistas, 
                total_exitos,
                total_rechazos
            )
            
            return MetricaAggregate(
                metrica_registro=metrica_registro,
                lista_logros=lista_logros
            )
            
        finally:
            db.close()
    
    def _calcular_logros(self, 
                         postulante_id: UUID, 
                         total_postulaciones: int, 
                         total_entrevistas: int,
                         total_exitos: int,
                         total_rechazos: int) -> List[Logro]:
        """Calcula los logros basados en las métricas"""
        logros = []
        
        # Ejemplos de logros según hitos alcanzados
        if total_postulaciones >= 10:
            logros.append(Logro(
                nombre_logro="Postulante Activo",
                umbral=10,
                fecha_obtencion=datetime.now()
            ))
            
        if total_entrevistas >= 5:
            logros.append(Logro(
                nombre_logro="Entrevistado Frecuente",
                umbral=5,
                fecha_obtencion=datetime.now()
            ))
            
        if total_exitos >= 1:
            logros.append(Logro(
                nombre_logro="Primera Oferta",
                umbral=1,
                fecha_obtencion=datetime.now()
            ))
            
        if total_exitos >= 3:
            logros.append(Logro(
                nombre_logro="Candidato Destacado",
                umbral=3,
                fecha_obtencion=datetime.now()
            ))
            
        return logros
    
    def obtener_contador_ofertas(self, postulante_id: UUID) -> int:
        """
        Devuelve el contador de ofertas alcanzadas para un postulante
        US23: Contador de ofertas alcanzadas
        """
        db = SessionLocal()
        try:
            # Contar ofertas directamente desde la base de datos
            return db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id),
                PostulacionModel.estado == "oferta"
            ).scalar() or 0
        finally:
            db.close()
    
    def obtener_contador_entrevistas(self, postulante_id: UUID) -> int:
        """
        Devuelve el contador de entrevistas obtenidas para un postulante
        US22: Contador de entrevistas obtenidas
        """
        db = SessionLocal()
        try:
            # Contar entrevistas directamente desde la base de datos
            return db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id),
                PostulacionModel.estado == "entrevista"
            ).scalar() or 0
        finally:
            db.close()
    
    def obtener_contador_rechazos(self, postulante_id: UUID) -> int:
        """
        Devuelve el contador de rechazos acumulados para un postulante
        US24: Contador de rechazos acumulados
        """
        db = SessionLocal()
        try:
            # Contar rechazos directamente desde la base de datos
            return db.query(func.count(PostulacionModel.id)).filter(
                PostulacionModel.perfil_id == str(postulante_id),
                PostulacionModel.estado.in_(["rechazado", "rechazo"])
            ).scalar() or 0
        finally:
            db.close()
    
    def guardar(self, metrica_aggregate: MetricaAggregate) -> UUID:
        """
        Método mantenido por compatibilidad con la interfaz pero no realiza ninguna operación
        de almacenamiento. Las métricas se calculan en tiempo real y no se almacenan.
        
        Al ser un bounded context de solo lectura, no hay necesidad de persistir el estado
        ya que se deriva completamente de otros bounded contexts (postulación).
        """
        return metrica_aggregate.metrica_registro.perfil_id