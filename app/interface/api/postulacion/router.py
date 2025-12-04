from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.application.postulacion.command_handlers import (
    PostularHandler, PostularCommand,
    ActualizarEstadoPostulacionHandler, ActualizarEstadoCommand
)
from app.application.postulacion.query_handlers import (
    ObtenerPostulacionQueryHandler, ObtenerPostulacionQuery,
    ListarPostulacionesCandidatoQueryHandler, ListarPostulacionesCandidatoQuery
)
from app.application.postulacion.postulacion_service import PostulacionService
from app.infrastructure.postulacion.repositories import PostulacionRepositoryImpl
from app.infrastructure.puesto.repositories import PuestoRepositoryImpl

from .schemas import (
    PostulacionCreate, PostulacionResponse, PostulacionEnriquecidaResponse,
    EstadoUpdate, EstadoPostulacionEnum
)

router = APIRouter(prefix="/postulacion", tags=["Postulación"])
postulacion_service = PostulacionService()


# Endpoints para Postulaciones
@router.post("/", response_model=PostulacionEnriquecidaResponse, status_code=status.HTTP_201_CREATED)
async def crear_postulacion(postulacion: PostulacionCreate):
    """
    Crea una nueva postulación y devuelve datos enriquecidos
    """
    try:
        postulacion_repository = PostulacionRepositoryImpl()
        puesto_repository = PuestoRepositoryImpl()
        handler = PostularHandler(postulacion_repository, puesto_repository)
        command = PostularCommand(
            candidato_id=UUID(postulacion.candidato_id),
            puesto_id=UUID(postulacion.puesto_id),
            documentos_adjuntos=postulacion.documentos_adjuntos or []
        )
        resultado = handler.handle(command)
        
        # Construir respuesta básica
        respuesta_basica = {
            "postulacion_id": str(resultado),
            "candidato_id": postulacion.candidato_id,
            "puesto_id": postulacion.puesto_id,
            "fecha_postulacion": datetime.now(),
            "estado": EstadoPostulacionEnum.PENDIENTE.value,
            "documentos_adjuntos": postulacion.documentos_adjuntos or [],
            "hitos": []
        }
        
        # Enriquecer con datos relacionados
        respuesta_enriquecida = postulacion_service.enriquecer_postulacion(respuesta_basica)
        
        return respuesta_basica
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{postulacion_id}", response_model=PostulacionEnriquecidaResponse)
async def obtener_postulacion(postulacion_id: str = Path(..., title="ID de la postulación")):
    """
    Obtiene una postulación con datos enriquecidos de candidato, puesto y empresa
    """
    try:
        postulacion_repository = PostulacionRepositoryImpl()
        handler = ObtenerPostulacionQueryHandler(postulacion_repository)
        query = ObtenerPostulacionQuery(postulacion_id=UUID(postulacion_id))
        resultado = handler.handle(query)
        if resultado is None:
            raise ValueError("No se encontró la postulación")
        
        # Enriquecer con datos relacionados
        respuesta_enriquecida = postulacion_service.enriquecer_postulacion(resultado)
        
        return respuesta_enriquecida
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con ID {postulacion_id} no encontrada"
        )


@router.get("/", response_model=List[PostulacionEnriquecidaResponse])
async def listar_postulaciones(
    candidato_id: Optional[str] = Query(None, title="ID del candidato"),
    puesto_id: Optional[str] = Query(None, title="ID del puesto"),
    estado: Optional[EstadoPostulacionEnum] = Query(None, title="Estado de la postulación"),
    enriquecer: bool = Query(True, title="Incluir datos enriquecidos")
):
    """
    Lista postulaciones con opción de enriquecimiento de datos
    
    - **candidato_id**: Filtrar por ID del candidato
    - **puesto_id**: Filtrar por ID del puesto
    - **estado**: Filtrar por estado de la postulación
    - **enriquecer**: Si es True (default), incluye datos de candidato, puesto y empresa
    """
    try:
        # Si se proporciona puesto_id, listar por puesto
        if puesto_id:
            postulacion_repository = PostulacionRepositoryImpl()
            resultados = postulacion_repository.obtener_por_puesto(UUID(puesto_id))

            # Enriquecer resultados si se solicita
            if enriquecer:
                respuestas = postulacion_service.enriquecer_postulaciones([
                    {
                        "postulacion_id": str(agg.postulacion.postulacion_id),
                        "candidato_id": str(agg.postulacion.candidato_id),
                        "puesto_id": str(agg.postulacion.puesto_id),
                        "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                        "estado": agg.postulacion.estado.valor.value,
                        "documentos_adjuntos": agg.postulacion.documentos_adjuntos
                    }
                    for agg in resultados
                ])
            else:
                respuestas = [
                    {
                        "postulacion_id": str(agg.postulacion.postulacion_id),
                        "candidato_id": str(agg.postulacion.candidato_id),
                        "puesto_id": str(agg.postulacion.puesto_id),
                        "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                        "estado": agg.postulacion.estado.valor.value,
                        "documentos_adjuntos": agg.postulacion.documentos_adjuntos,
                        "hitos": []
                    }
                    for agg in resultados
                ]

            return respuestas

        # Por ahora solo implementamos el filtrado por candidato
        if candidato_id:
            postulacion_repository = PostulacionRepositoryImpl()
            handler = ListarPostulacionesCandidatoQueryHandler(postulacion_repository)
            query = ListarPostulacionesCandidatoQuery(candidato_id=UUID(candidato_id))
            resultados = handler.handle(query)
            
            # Enriquecer resultados si se solicita
            if enriquecer:
                respuestas = postulacion_service.enriquecer_postulaciones(resultados)
            else:
                respuestas = [
                    {
                        "postulacion_id": resultado.get("postulacion_id", ""),
                        "candidato_id": resultado.get("candidato_id", candidato_id),
                        "puesto_id": resultado.get("puesto_id", ""),
                        "fecha_postulacion": datetime.fromisoformat(resultado.get("fecha_postulacion", datetime.now().isoformat())),
                        "estado": resultado.get("estado", EstadoPostulacionEnum.PENDIENTE.value),
                        "documentos_adjuntos": resultado.get("documentos_adjuntos", []),
                        "hitos": []
                    }
                    for resultado in resultados
                ]
            
            return respuestas
        else:
            # Para los demás filtros, implementación temporal
            return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{postulacion_id}/estado", response_model=PostulacionEnriquecidaResponse)
async def actualizar_estado_postulacion(
    estado_update: EstadoUpdate,
    postulacion_id: str = Path(..., title="ID de la postulación")
):
    """
    Actualiza el estado de una postulación y devuelve datos enriquecidos
    """
    try:
        postulacion_repository = PostulacionRepositoryImpl()
        
        # Obtener la postulación actual
        handler_get = ObtenerPostulacionQueryHandler(postulacion_repository)
        query_get = ObtenerPostulacionQuery(postulacion_id=UUID(postulacion_id))
        postulacion_actual = handler_get.handle(query_get)
        if not postulacion_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Postulación con ID {postulacion_id} no encontrada"
            )
        
        # Actualizar estado
        handler = ActualizarEstadoPostulacionHandler(postulacion_repository)
        command = ActualizarEstadoCommand(
            postulacion_id=UUID(postulacion_id),
            nuevo_estado=estado_update.nuevo_estado
        )
        resultado = handler.handle(command)
        
        # Construir respuesta actualizada
        respuesta = {
            "postulacion_id": postulacion_actual.get("postulacion_id", postulacion_id),
            "candidato_id": postulacion_actual.get("candidato_id", ""),
            "puesto_id": postulacion_actual.get("puesto_id", ""),
            "fecha_postulacion": datetime.fromisoformat(postulacion_actual.get("fecha_postulacion", datetime.now().isoformat())),
            "estado": estado_update.nuevo_estado,
            "documentos_adjuntos": postulacion_actual.get("documentos_adjuntos", []),
            "hitos": postulacion_actual.get("hitos", [])
        }
        
        # Enriquecer con datos relacionados
        respuesta_enriquecida = postulacion_service.enriquecer_postulacion(respuesta)
        
        return respuesta_enriquecida
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
