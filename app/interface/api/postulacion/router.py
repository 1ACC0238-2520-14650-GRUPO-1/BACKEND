from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.application.puesto.command_handlers import (
    CrearPuestoHandler, CrearPuestoCommand, ActualizarPuestoHandler, CambiarEstadoPuestoHandler, CambiarEstadoPuestoCommand
)
from app.application.puesto.query_handlers import (
    ObtenerPuestoQueryHandler, ObtenerPuestoQuery,
    ListarPuestosQueryHandler, ListarPuestosQuery
)
from app.infrastructure.puesto.repositories import PuestoRepositoryImpl

from .schemas import (
    PuestoCreate, PuestoUpdate, PuestoResponse, RequisitoResponse,
    EstadoPuestoUpdate, EstadoPuestoEnum, TipoContratoEnum
)

router = APIRouter(prefix="/puesto", tags=["Puesto"])

@router.post("/", response_model=PuestoResponse, status_code=status.HTTP_201_CREATED)
async def crear_puesto(puesto: PuestoCreate):
    """
    Crea un nuevo puesto de trabajo con la información proporcionada.
    
    - **empresa_id**: ID de la empresa que crea el puesto
    - **titulo**: Título del puesto de trabajo
    - **descripcion**: Descripción detallada del puesto
    - **ubicacion**: Ubicación geográfica del puesto
    - **salario_min**: Salario mínimo ofrecido (opcional)
    - **salario_max**: Salario máximo ofrecido (opcional)
    - **moneda**: Moneda del salario (por defecto MXN)
    - **tipo_contrato**: Tipo de contrato ofrecido (tiempo_completo, medio_tiempo, etc.)
    - **requisitos**: Lista de requisitos para el puesto (opcional)
    """
    try:
        puesto_repository = PuestoRepositoryImpl()
        handler = CrearPuestoHandler(puesto_repository)
        
        # Preparar requisitos en formato dict
        requisitos = []
        if puesto.requisitos:
            for req in puesto.requisitos:
                requisitos.append({
                    "tipo": req.tipo,
                    "descripcion": req.descripcion,
                    "es_obligatorio": req.es_obligatorio
                })
        
        # Crear comando
        command = CrearPuestoCommand(
            empresa_id=UUID(puesto.empresa_id),
            titulo=puesto.titulo,
            descripcion=puesto.descripcion,
            ubicacion=puesto.ubicacion,
            salario_min=puesto.salario_min,
            salario_max=puesto.salario_max,
            moneda=puesto.moneda,
            tipo_contrato=puesto.tipo_contrato,
            requisitos=requisitos if requisitos else None
        )
        resultado = handler.handle(command)
        
        # Transformar respuesta a PuestoResponse
        respuesta = PuestoResponse(
            puesto_id=resultado.get("puesto_id", ""),
            empresa_id=resultado.get("empresa_id", puesto.empresa_id),
            titulo=resultado.get("titulo", puesto.titulo),
            descripcion=resultado.get("descripcion", puesto.descripcion),
            ubicacion=resultado.get("ubicacion", puesto.ubicacion),
            salario_min=resultado.get("salario_min"),
            salario_max=resultado.get("salario_max"),
            moneda=resultado.get("moneda", "MXN"),
            tipo_contrato=resultado.get("tipo_contrato", "tiempo_completo"),
            fecha_publicacion=datetime.fromisoformat(resultado.get("fecha_publicacion", datetime.now().isoformat())),
            fecha_cierre=datetime.fromisoformat(resultado.get("fecha_cierre", datetime.now().isoformat())) if resultado.get("fecha_cierre") else None,
            estado=resultado.get("estado", "abierto"),
            requisitos=[RequisitoResponse(**req) for req in resultado.get("requisitos", [])]
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{puesto_id}", response_model=PuestoResponse)
async def obtener_puesto(puesto_id: str = Path(..., title="ID del puesto")):
    """
    Obtiene la información detallada de un puesto por su ID.
    
    - **puesto_id**: ID del puesto a consultar
    """
    try:
        puesto_repository = PuestoRepositoryImpl()
        handler = ObtenerPuestoQueryHandler(puesto_repository)
        query = ObtenerPuestoQuery(puesto_id=UUID(puesto_id))
        resultado = handler.handle(query)
        if resultado is None:
            raise ValueError("No se encontró el puesto")
        
        # Transformar resultado a PuestoResponse
        respuesta = PuestoResponse(
            puesto_id=resultado.get("puesto_id", puesto_id),
            empresa_id=resultado.get("empresa_id", ""),
            titulo=resultado.get("titulo", ""),
            descripcion=resultado.get("descripcion", ""),
            ubicacion=resultado.get("ubicacion", ""),
            salario_min=resultado.get("salario_min"),
            salario_max=resultado.get("salario_max"),
            moneda=resultado.get("moneda", "MXN"),
            tipo_contrato=resultado.get("tipo_contrato", "tiempo_completo"),
            fecha_publicacion=datetime.fromisoformat(resultado.get("fecha_publicacion", datetime.now().isoformat())),
            fecha_cierre=datetime.fromisoformat(resultado.get("fecha_cierre")) if resultado.get("fecha_cierre") else None,
            estado=resultado.get("estado", EstadoPuestoEnum.ABIERTO.value),
            requisitos=resultado.get("requisitos", [])
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Puesto con ID {puesto_id} no encontrado"
        )


@router.get("/", response_model=List[PuestoResponse])
async def listar_puestos(
    empresa_id: Optional[str] = Query(None, title="ID de la empresa"),
    estado: Optional[EstadoPuestoEnum] = Query(None, title="Estado del puesto (abierto/cerrado)")
):
    """
    Lista todos los puestos disponibles con filtros opcionales.
    
    - **empresa_id**: Filtrar por ID de empresa (opcional)
    - **estado**: Filtrar por estado del puesto (abierto/cerrado) (opcional)
    """
    try:
        puesto_repository = PuestoRepositoryImpl()
        handler = ListarPuestosQueryHandler(puesto_repository)
        query = ListarPuestosQuery(
            empresa_id=UUID(empresa_id) if empresa_id else None,
            estado=estado
        )
        resultados = handler.handle(query)
        
        # Transformar resultados a PuestoResponse
        respuestas = []
        for resultado in resultados:
            respuesta = PuestoResponse(
                puesto_id=resultado.get("puesto_id", ""),
                empresa_id=resultado.get("empresa_id", ""),
                titulo=resultado.get("titulo", ""),
                descripcion=resultado.get("descripcion", ""),
                ubicacion=resultado.get("ubicacion", ""),
                salario_min=resultado.get("salario_min"),
                salario_max=resultado.get("salario_max"),
                moneda=resultado.get("moneda", "MXN"),
                tipo_contrato=resultado.get("tipo_contrato", "tiempo_completo"),
                fecha_publicacion=datetime.fromisoformat(resultado.get("fecha_publicacion", datetime.now().isoformat())),
                fecha_cierre=datetime.fromisoformat(resultado.get("fecha_cierre")) if resultado.get("fecha_cierre") else None,
                estado=resultado.get("estado", EstadoPuestoEnum.ABIERTO.value),
                requisitos=resultado.get("requisitos", [])
            )
            respuestas.append(respuesta)
        return respuestas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{puesto_id}", response_model=PuestoResponse)
async def actualizar_puesto(
    puesto_update: PuestoUpdate,
    puesto_id: str = Path(..., title="ID del puesto")
):
    """
    Actualiza la información de un puesto existente.
    
    - **puesto_id**: ID del puesto a actualizar
    - **titulo**: Nuevo título del puesto (opcional)
    - **descripcion**: Nueva descripción del puesto (opcional)
    - **ubicacion**: Nueva ubicación del puesto (opcional)
    - **salario_min**: Nuevo salario mínimo (opcional)
    - **salario_max**: Nuevo salario máximo (opcional)
    - **moneda**: Nueva moneda del salario (opcional)
    - **tipo_contrato**: Nuevo tipo de contrato (opcional)
    - **requisitos**: Nueva lista de requisitos (opcional)
    """
    try:
        puesto_repository = PuestoRepositoryImpl()
        
        # Obtener el puesto actual
        handler_get = ObtenerPuestoQueryHandler(puesto_repository)
        query_get = ObtenerPuestoQuery(puesto_id=UUID(puesto_id))
        puesto_actual = handler_get.handle(query_get)
        if not puesto_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Puesto con ID {puesto_id} no encontrado"
            )
        
        # Actualizar
        handler = ActualizarPuestoHandler(puesto_repository)
        requisitos = None
        if puesto_update.requisitos is not None:
            requisitos = [req.dict() if hasattr(req, 'dict') else req for req in puesto_update.requisitos]
            
        resultado = handler.handle(
            puesto_id=UUID(puesto_id),
            titulo=puesto_update.titulo,
            descripcion=puesto_update.descripcion,
            ubicacion=puesto_update.ubicacion,
            salario_min=puesto_update.salario_min,
            salario_max=puesto_update.salario_max,
            moneda=puesto_update.moneda,
            tipo_contrato=puesto_update.tipo_contrato.value if isinstance(puesto_update.tipo_contrato, TipoContratoEnum) else puesto_update.tipo_contrato if puesto_update.tipo_contrato else None,
            requisitos=requisitos
        )
        
        # Retornar puesto actualizado
        respuesta = PuestoResponse(
            puesto_id=puesto_actual.get("puesto_id", puesto_id),
            empresa_id=puesto_actual.get("empresa_id", ""),
            titulo=puesto_update.titulo or puesto_actual.get("titulo", ""),
            descripcion=puesto_update.descripcion or puesto_actual.get("descripcion", ""),
            ubicacion=puesto_update.ubicacion or puesto_actual.get("ubicacion", ""),
            salario_min=puesto_update.salario_min if puesto_update.salario_min is not None else puesto_actual.get("salario_min"),
            salario_max=puesto_update.salario_max if puesto_update.salario_max is not None else puesto_actual.get("salario_max"),
            moneda=puesto_update.moneda or puesto_actual.get("moneda", "MXN"),
            tipo_contrato=(puesto_update.tipo_contrato.value if isinstance(puesto_update.tipo_contrato, TipoContratoEnum) else puesto_update.tipo_contrato) or puesto_actual.get("tipo_contrato", "tiempo_completo"),
            fecha_publicacion=datetime.fromisoformat(puesto_actual.get("fecha_publicacion", datetime.now().isoformat())),
            fecha_cierre=datetime.fromisoformat(puesto_actual.get("fecha_cierre")) if puesto_actual.get("fecha_cierre") else None,
            estado=puesto_actual.get("estado", EstadoPuestoEnum.ABIERTO.value),
            requisitos=requisitos or puesto_actual.get("requisitos", [])
        )
        return respuesta
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{puesto_id}/estado", response_model=PuestoResponse)
async def cambiar_estado_puesto(
    estado_update: EstadoPuestoUpdate,
    puesto_id: str = Path(..., title="ID del puesto")
):
    """
    Cambia el estado de un puesto entre abierto y cerrado.
    
    - **puesto_id**: ID del puesto a cambiar
    - **nuevo_estado**: Nuevo estado del puesto (abierto/cerrado)
    """
    try:
        puesto_repository = PuestoRepositoryImpl()
        
        # Obtener el puesto actual
        handler_get = ObtenerPuestoQueryHandler(puesto_repository)
        query_get = ObtenerPuestoQuery(puesto_id=UUID(puesto_id))
        puesto_actual = handler_get.handle(query_get)
        if not puesto_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Puesto con ID {puesto_id} no encontrado"
            )
        
        # Cambiar estado
        handler = CambiarEstadoPuestoHandler(puesto_repository)
        command = CambiarEstadoPuestoCommand(
            puesto_id=UUID(puesto_id),
            nuevo_estado=estado_update.nuevo_estado
        )
        resultado = handler.handle(command)
        
        # Retornar puesto con estado actualizado
        respuesta = PuestoResponse(
            puesto_id=puesto_actual.get("puesto_id", puesto_id),
            empresa_id=puesto_actual.get("empresa_id", ""),
            titulo=puesto_actual.get("titulo", ""),
            descripcion=puesto_actual.get("descripcion", ""),
            ubicacion=puesto_actual.get("ubicacion", ""),
            salario_min=puesto_actual.get("salario_min"),
            salario_max=puesto_actual.get("salario_max"),
            moneda=puesto_actual.get("moneda", "MXN"),
            tipo_contrato=puesto_actual.get("tipo_contrato", "tiempo_completo"),
            fecha_publicacion=datetime.fromisoformat(puesto_actual.get("fecha_publicacion", datetime.now().isoformat())),
            fecha_cierre=datetime.fromisoformat(puesto_actual.get("fecha_cierre")) if puesto_actual.get("fecha_cierre") else None,
            estado=estado_update.nuevo_estado.value,
            requisitos=puesto_actual.get("requisitos", [])
        )
        return respuesta
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
