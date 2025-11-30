from fastapi import APIRouter, Depends, HTTPException, status, Path, Query, Body
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime

from app.application.metrica.command_handlers import (
    RecalcularMetricasCommand, RecalcularMetricasHandler
)
from app.application.metrica.query_handlers import (
    ConsultarResumenMetricasQuery, ConsultarResumenMetricasHandler,
    ListarLogrosQuery, ListarLogrosHandler,
    ContadorOfertasQuery, ContadorOfertasQueryHandler,
    ContadorEntrevistasQuery, ContadorEntrevistasQueryHandler,
    ContadorRechazosQuery, ContadorRechazosQueryHandler
)
from app.infrastructure.metrica.repositories import MetricaRepositoryImpl

from .schemas import (
    MetricaResumenResponse,
    LogroResponse,
    ContadorResponse
)

router = APIRouter(prefix="/metricas", tags=["Métricas"])

# Endpoints para consulta de métricas (calculadas en tiempo real)
@router.get("/resumen/{cuenta_id}", response_model=MetricaResumenResponse)
async def obtener_resumen_metricas(cuenta_id: UUID = Path(..., title="ID del cuenta")):
    """
    Obtiene un resumen de todas las métricas para una cuenta  específica.
    Las métricas se calculan en tiempo real basadas en el estado actual de las postulaciones.
    """
    try:
        metrica_repository = MetricaRepositoryImpl()
        handler = ConsultarResumenMetricasHandler(metrica_repository)
        query = ConsultarResumenMetricasQuery(cuenta_id=cuenta_id)
        
        resultado = handler.handle(query)
        if not resultado:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontraron métricas para el cuenta {cuenta_id}"
            )
        return resultado
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/logros/{cuenta_id}", response_model=List[LogroResponse])
async def listar_logros(cuenta_id: UUID = Path(..., title="ID del cuenta")):
    """
    Lista todos los logros conseguidos por una cuenta específica.
    Los logros se calculan en tiempo real basados en el historial de postulaciones.
    """
    try:
        metrica_repository = MetricaRepositoryImpl()
        handler = ListarLogrosHandler(metrica_repository)
        query = ListarLogrosQuery(cuenta_id=cuenta_id)
        
        return handler.handle(query)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/recalcular/{cuenta_id}", response_model=MetricaResumenResponse)
async def recalcular_metricas(cuenta_id: UUID = Path(..., title="ID de la cuenta" )):
    """
    Fuerza un recálculo de todas las métricas para un cuenta específico.
    Las métricas se calculan en tiempo real basadas en el estado actual de las postulaciones.
    """
    try:
        metrica_repository = MetricaRepositoryImpl()
        handler = RecalcularMetricasHandler(metrica_repository)
        command = RecalcularMetricasCommand(cuenta_id=cuenta_id)
        
        return handler.handle(command)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/contadores/ofertas/{postulante_id}", response_model=ContadorResponse)
async def obtener_contador_ofertas(postulante_id: UUID = Path(..., title="ID del postulante")):
    """
    Obtiene el contador de ofertas para un postulante específico.
    US23: Contador de ofertas alcanzadas
    """
    try:
        metrica_repository = MetricaRepositoryImpl()
        handler = ContadorOfertasQueryHandler(metrica_repository)
        query = ContadorOfertasQuery(postulante_id=postulante_id)
        
        result = handler.handle(query)
        return {
            "postulante_id": result["postulante_id"],
            "total": result["total_ofertas"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/contadores/entrevistas/{postulante_id}", response_model=ContadorResponse)
async def obtener_contador_entrevistas(postulante_id: UUID = Path(..., title="ID del postulante")):
    """
    Obtiene el contador de entrevistas para un postulante específico.
    US22: Contador de entrevistas obtenidas
    """
    try:
        metrica_repository = MetricaRepositoryImpl()
        handler = ContadorEntrevistasQueryHandler(metrica_repository)
        query = ContadorEntrevistasQuery(postulante_id=postulante_id)
        
        result = handler.handle(query)
        return {
            "postulante_id": result["postulante_id"],
            "total": result["total_entrevistas"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/contadores/rechazos/{postulante_id}", response_model=ContadorResponse)
async def obtener_contador_rechazos(postulante_id: UUID = Path(..., title="ID del postulante")):
    """
    Obtiene el contador de rechazos para un postulante específico.
    US24: Contador de rechazos acumulados
    """
    try:
        metrica_repository = MetricaRepositoryImpl()
        handler = ContadorRechazosQueryHandler(metrica_repository)
        query = ContadorRechazosQuery(postulante_id=postulante_id)
        
        result = handler.handle(query)
        return {
            "postulante_id": result["postulante_id"],
            "total": result["total_rechazos"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )