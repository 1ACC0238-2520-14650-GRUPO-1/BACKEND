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
from app.infrastructure.postulacion.repositories import PostulacionRepositoryImpl
from app.infrastructure.puesto.repositories import PuestoRepositoryImpl

from .schemas import (
    PostulacionCreate, PostulacionResponse, EstadoUpdate, EstadoPostulacionEnum
)

router = APIRouter(prefix="/postulacion", tags=["Postulación"])

# Endpoints para Postulaciones
@router.post("/", response_model=PostulacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_postulacion(postulacion: PostulacionCreate):
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
        
        # Retornar respuesta formateada
        respuesta = PostulacionResponse(
            postulacion_id=str(resultado),
            candidato_id=postulacion.candidato_id,
            puesto_id=postulacion.puesto_id,
            fecha_postulacion=datetime.now(),
            estado=EstadoPostulacionEnum.PENDIENTE.value,
            documentos_adjuntos=postulacion.documentos_adjuntos or [],
            hitos=[]
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{postulacion_id}", response_model=PostulacionResponse)
async def obtener_postulacion(postulacion_id: str = Path(..., title="ID de la postulación")):
    try:
        postulacion_repository = PostulacionRepositoryImpl()
        handler = ObtenerPostulacionQueryHandler(postulacion_repository)
        query = ObtenerPostulacionQuery(postulacion_id=UUID(postulacion_id))
        resultado = handler.handle(query)
        if resultado is None:
            raise ValueError("No se encontró la postulación")
        
        # Transformar resultado a PostulacionResponse
        respuesta = PostulacionResponse(
            postulacion_id=resultado.get("postulacion_id", postulacion_id),
            candidato_id=resultado.get("candidato_id", ""),
            puesto_id=resultado.get("puesto_id", ""),
            fecha_postulacion=datetime.fromisoformat(resultado.get("fecha_postulacion", datetime.now().isoformat())),
            estado=resultado.get("estado", EstadoPostulacionEnum.PENDIENTE.value),
            documentos_adjuntos=resultado.get("documentos_adjuntos", []),
            hitos=resultado.get("hitos", [])
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Postulación con ID {postulacion_id} no encontrada"
        )


@router.get("/", response_model=List[PostulacionResponse])
async def listar_postulaciones(
    candidato_id: Optional[str] = Query(None, title="ID del candidato"),
    puesto_id: Optional[str] = Query(None, title="ID del puesto"),
    estado: Optional[EstadoPostulacionEnum] = Query(None, title="Estado de la postulación")
):
    try:
        # Por ahora solo implementamos el filtrado por candidato
        if candidato_id:
            postulacion_repository = PostulacionRepositoryImpl()
            handler = ListarPostulacionesCandidatoQueryHandler(postulacion_repository)
            query = ListarPostulacionesCandidatoQuery(candidato_id=UUID(candidato_id))
            resultados = handler.handle(query)
            
            # Transformar resultados a PostulacionResponse
            respuestas = []
            for resultado in resultados:
                respuesta = PostulacionResponse(
                    postulacion_id=resultado.get("postulacion_id", ""),
                    candidato_id=resultado.get("candidato_id", candidato_id),
                    puesto_id=resultado.get("puesto_id", ""),
                    fecha_postulacion=datetime.fromisoformat(resultado.get("fecha_postulacion", datetime.now().isoformat())),
                    estado=resultado.get("estado", EstadoPostulacionEnum.PENDIENTE.value),
                    documentos_adjuntos=resultado.get("documentos_adjuntos", []),
                    hitos=[]
                )
                respuestas.append(respuesta)
            return respuestas
        else:
            # Para los demás filtros, implementación temporal
            return []
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{postulacion_id}/estado", response_model=PostulacionResponse)
async def actualizar_estado_postulacion(
    estado_update: EstadoUpdate,
    postulacion_id: str = Path(..., title="ID de la postulación")
):
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
        
        # Retornar postulación actualizada
        respuesta = PostulacionResponse(
            postulacion_id=postulacion_actual.get("postulacion_id", postulacion_id),
            candidato_id=postulacion_actual.get("candidato_id", ""),
            puesto_id=postulacion_actual.get("puesto_id", ""),
            fecha_postulacion=datetime.fromisoformat(postulacion_actual.get("fecha_postulacion", datetime.now().isoformat())),
            estado=estado_update.nuevo_estado,
            documentos_adjuntos=postulacion_actual.get("documentos_adjuntos", []),
            hitos=postulacion_actual.get("hitos", [])
        )
        return respuesta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Los endpoints de Puestos se han movido a su propio bounded context
# Ahora se encuentran en app/interface/api/puesto/router.py