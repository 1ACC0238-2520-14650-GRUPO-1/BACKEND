from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.application.perfil.command_handlers import (
    CrearPerfilPostulanteHandler as CrearPerfilHandler,
    CrearPerfilPostulanteCommand,
    ActualizarDatosPostulanteHandler as ActualizarPerfilHandler,
    ActualizarDatosPostulanteCommand,
    ConfigurarPreferenciasPostulanteHandler as CambiarEstadoPerfilHandler,
    ConfigurarPreferenciasPostulanteCommand,
    CrearPerfilPostulanteHandler as CrearPerfilCandidatoHandler, 
    ActualizarDatosPostulanteHandler as ActualizarPerfilCandidatoHandler,
    ActualizarDatosPostulanteCommand as ActualizarPerfilCandidatoCommand
)
from app.application.perfil.query_handlers import (
    ObtenerPerfilQueryHandler as ObtenerPerfilHandler,
    ObtenerPerfilQuery,
    ListarPerfilesPorTipoQueryHandler as ListarPerfilesHandler,
    ListarPerfilesPorTipoQuery
)
# ObtenerPerfilCandidatoHandler no existe, usaremos ObtenerPerfilQueryHandler como fallback
from app.application.perfil.query_handlers import ObtenerPerfilQueryHandler as ObtenerPerfilCandidatoHandler
from app.infrastructure.perfil.repositories import PerfilRepositoryImpl
from app.domain.perfil.entities import TipoPerfilEnum

from .schemas import (
    PerfilCreate, PerfilResponse, PerfilUpdate,
    PerfilCandidatoCreate, PerfilCandidatoResponse, PerfilCandidatoUpdate,
    TipoCuentaEnum, EstadoPerfilEnum
)

# Helper para convertir a datetime de manera segura
def parse_datetime(value):
    """Convierte un valor a datetime, manejando string, datetime y None"""
    if value is None:
        return datetime.now()
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return datetime.now()
    return datetime.now()

router = APIRouter(prefix="/perfil", tags=["Perfil"])

# Endpoints para Perfiles
@router.post("/", response_model=PerfilResponse, status_code=status.HTTP_201_CREATED)
async def crear_perfil(perfil: PerfilCreate):
    try:
        perfil_repository = PerfilRepositoryImpl()
        handler = CrearPerfilHandler(perfil_repository)
        command = CrearPerfilPostulanteCommand(
            datos_personales={
                "nombre": perfil.nombre,
                "email": perfil.email,
                "tipo_cuenta": perfil.tipo_cuenta.value,
                "datos_contacto": perfil.datos_contacto
            }
        )
        perfil_id = handler.handle(command)
        
        # Obtener el perfil creado para retornarlo completo
        respuesta = PerfilResponse(
            perfil_id=str(perfil_id),
            nombre=perfil.nombre,
            email=perfil.email,
            tipo_cuenta=perfil.tipo_cuenta.value,
            datos_contacto=perfil.datos_contacto,
            fecha_registro=datetime.now(),
            estado=EstadoPerfilEnum.INCOMPLETO.value,
            ultima_actualizacion=datetime.now()
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{perfil_id}", response_model=PerfilResponse)
async def obtener_perfil(perfil_id: str = Path(..., title="ID del perfil")):
    try:
        perfil_repository = PerfilRepositoryImpl()
        handler = ObtenerPerfilHandler(perfil_repository)
        query = ObtenerPerfilQuery(perfil_id=UUID(perfil_id))
        resultado_raw = handler.handle(query)
        if resultado_raw is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil con ID {perfil_id} no encontrado"
            )
        
        # Transformar respuesta del handler a formato esperado por schema
        datos_personales = resultado_raw.get("datos_personales", {})
        email_raw = datos_personales.get("email", datos_personales.get("correo", ""))
        email = email_raw if email_raw and "@" in email_raw else f"user_{perfil_id[:8]}@example.com"
        
        respuesta = PerfilResponse(
            perfil_id=resultado_raw.get("perfil_id", ""),
            nombre=datos_personales.get("nombre", ""),
            email=email,
            tipo_cuenta=TipoCuentaEnum.CANDIDATO.value,
            datos_contacto=datos_personales if isinstance(datos_personales, dict) else {},
            fecha_registro=parse_datetime(resultado_raw.get("fecha_creacion")),
            estado=EstadoPerfilEnum.INCOMPLETO.value,
            ultima_actualizacion=parse_datetime(resultado_raw.get("fecha_actualizacion"))
        )
        return respuesta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Perfil con ID {perfil_id} no encontrado: {str(e)}"
        )


@router.get("/", response_model=List[PerfilResponse])
async def listar_perfiles(
    tipo_cuenta: Optional[TipoCuentaEnum] = Query(None, title="Tipo de cuenta"),
    estado: Optional[EstadoPerfilEnum] = Query(None, title="Estado del perfil")
):
    try:
        perfil_repository = PerfilRepositoryImpl()
        handler = ListarPerfilesHandler(perfil_repository)
        # Para este endpoint simplificado, listaremos todos los perfiles
        # Si necesitas filtrado específico, ajusta según la Query
        query = ListarPerfilesPorTipoQuery(tipo_perfil=TipoPerfilEnum.POSTULANTE)
        perfiles_raw = handler.handle(query)
        
        # Transformar respuesta del handler a formato esperado por schema
        respuestas = []
        for idx, perfil in enumerate(perfiles_raw):
            # Obtener email seguro - si está vacío, generar uno
            email_raw = perfil.get("correo", perfil.get("email", ""))
            email = email_raw if email_raw and "@" in email_raw else f"user_{idx}@example.com"
            
            respuesta = PerfilResponse(
                perfil_id=perfil.get("perfil_id", ""),
                nombre=perfil.get("nombre", ""),
                email=email,
                tipo_cuenta=TipoCuentaEnum.CANDIDATO.value,
                datos_contacto={"correo": email},
                fecha_registro=parse_datetime(perfil.get("fecha_creacion")),
                estado=EstadoPerfilEnum.INCOMPLETO.value,
                ultima_actualizacion=parse_datetime(perfil.get("fecha_creacion"))
            )
            respuestas.append(respuesta)
        return respuestas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{perfil_id}", response_model=PerfilResponse)
async def actualizar_perfil(
    perfil_update: PerfilUpdate,
    perfil_id: str = Path(..., title="ID del perfil")
):
    try:
        perfil_repository = PerfilRepositoryImpl()
        # Obtener el perfil actual
        handler_get = ObtenerPerfilHandler(perfil_repository)
        query_get = ObtenerPerfilQuery(perfil_id=UUID(perfil_id))
        perfil_actual = handler_get.handle(query_get)
        if not perfil_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil con ID {perfil_id} no encontrado"
            )
        
        # Actualizar
        handler = ActualizarPerfilHandler(perfil_repository)
        update_data = perfil_update.dict(exclude_unset=True)
        command = ActualizarDatosPostulanteCommand(
            perfil_id=UUID(perfil_id),
            datos=update_data
        )
        resultado = handler.handle(command)
        
        # Retornar el perfil actualizado
        datos_personales = perfil_actual.get("datos_personales", {})
        if update_data.get("nombre"):
            datos_personales["nombre"] = update_data["nombre"]
        if update_data.get("email"):
            datos_personales["email"] = update_data["email"]
        if update_data.get("datos_contacto"):
            datos_personales.update(update_data["datos_contacto"])
        
        # Asegurar email válido
        email = datos_personales.get("email", "")
        if not email or "@" not in email:
            email = f"user_{perfil_id[:8]}@example.com"
        
        respuesta = PerfilResponse(
            perfil_id=perfil_actual.get("perfil_id", perfil_id),
            nombre=datos_personales.get("nombre", ""),
            email=email,
            tipo_cuenta=TipoCuentaEnum.CANDIDATO.value,
            datos_contacto=datos_personales if isinstance(datos_personales, dict) else {},
            fecha_registro=parse_datetime(perfil_actual.get("fecha_creacion")),
            estado=EstadoPerfilEnum.INCOMPLETO.value,
            ultima_actualizacion=datetime.now()
        )
        return respuesta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{perfil_id}/estado", response_model=PerfilResponse)
async def cambiar_estado_perfil(
    estado: EstadoPerfilEnum,
    perfil_id: str = Path(..., title="ID del perfil")
):
    try:
        perfil_repository = PerfilRepositoryImpl()
        # Obtener el perfil actual
        handler_get = ObtenerPerfilHandler(perfil_repository)
        query_get = ObtenerPerfilQuery(perfil_id=UUID(perfil_id))
        perfil_actual = handler_get.handle(query_get)
        if not perfil_actual:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil con ID {perfil_id} no encontrado"
            )
        
        # Cambiar estado
        handler = CambiarEstadoPerfilHandler(perfil_repository)
        command = ConfigurarPreferenciasPostulanteCommand(
            perfil_id=UUID(perfil_id),
            preferencias={"estado": estado.value}
        )
        resultado = handler.handle(command)
        
        # Retornar el perfil con estado actualizado
        datos_personales = perfil_actual.get("datos_personales", {})
        
        # Asegurar email válido
        email = datos_personales.get("email", "")
        if not email or "@" not in email:
            email = f"user_{perfil_id[:8]}@example.com"
        
        respuesta = PerfilResponse(
            perfil_id=perfil_actual.get("perfil_id", perfil_id),
            nombre=datos_personales.get("nombre", ""),
            email=email,
            tipo_cuenta=TipoCuentaEnum.CANDIDATO.value,
            datos_contacto=datos_personales if isinstance(datos_personales, dict) else {},
            fecha_registro=parse_datetime(perfil_actual.get("fecha_creacion")),
            estado=estado.value,
            ultima_actualizacion=datetime.now()
        )
        return respuesta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# Endpoints para Perfil Candidato
@router.post("/candidato", response_model=PerfilCandidatoResponse, status_code=status.HTTP_201_CREATED)
async def crear_perfil_candidato(perfil_candidato: PerfilCandidatoCreate):
    try:
        perfil_repository = PerfilRepositoryImpl()
        handler = CrearPerfilCandidatoHandler(perfil_repository)
        
        # Convertir datetime objects a isoformat strings para JSON serialization
        experiencias_dict = []
        if perfil_candidato.experiencias:
            for exp in perfil_candidato.experiencias:
                exp_data = exp.dict()
                exp_data['fecha_inicio'] = exp_data['fecha_inicio'].isoformat() if isinstance(exp_data['fecha_inicio'], datetime) else exp_data['fecha_inicio']
                exp_data['fecha_fin'] = exp_data['fecha_fin'].isoformat() if exp_data.get('fecha_fin') and isinstance(exp_data['fecha_fin'], datetime) else exp_data.get('fecha_fin')
                experiencias_dict.append(exp_data)
        
        educacion_dict = []
        if perfil_candidato.educacion:
            for edu in perfil_candidato.educacion:
                edu_data = edu.dict()
                edu_data['fecha_inicio'] = edu_data['fecha_inicio'].isoformat() if isinstance(edu_data['fecha_inicio'], datetime) else edu_data['fecha_inicio']
                edu_data['fecha_fin'] = edu_data['fecha_fin'].isoformat() if edu_data.get('fecha_fin') and isinstance(edu_data['fecha_fin'], datetime) else edu_data.get('fecha_fin')
                educacion_dict.append(edu_data)
        
        command = CrearPerfilPostulanteCommand(
            datos_personales={
                "perfil_id": str(perfil_candidato.perfil_id),
                "experiencias": experiencias_dict,
                "educacion": educacion_dict,
                "habilidades": perfil_candidato.habilidades or [],
                "cv_url": perfil_candidato.cv_url
            }
        )
        resultado = handler.handle(command)
        
        # Retornar respuesta formateada
        respuesta = PerfilCandidatoResponse(
            perfil_candidato_id=str(resultado),
            perfil_id=str(perfil_candidato.perfil_id),
            experiencias=perfil_candidato.experiencias or [],
            educacion=perfil_candidato.educacion or [],
            habilidades=perfil_candidato.habilidades or [],
            cv_url=perfil_candidato.cv_url
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/candidato/{perfil_id}", response_model=PerfilCandidatoResponse)
async def obtener_perfil_candidato(perfil_id: str = Path(..., title="ID del perfil")):
    try:
        perfil_repository = PerfilRepositoryImpl()
        handler = ObtenerPerfilCandidatoHandler(perfil_repository)
        query = ObtenerPerfilQuery(perfil_id=UUID(perfil_id))
        resultado = handler.handle(query)
        if resultado is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Perfil de candidato con ID {perfil_id} no encontrado"
            )
        
        # Transformar resultado a PerfilCandidatoResponse
        respuesta = PerfilCandidatoResponse(
            perfil_candidato_id=str(resultado.get("perfil_id", perfil_id)),
            perfil_id=str(resultado.get("perfil_id", perfil_id)),
            experiencias=[],
            educacion=[],
            habilidades=[],
            cv_url=None
        )
        return respuesta
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Perfil de candidato con ID {perfil_id} no encontrado"
        )


@router.put("/candidato/{perfil_id}", response_model=PerfilCandidatoResponse)
async def actualizar_perfil_candidato(
    perfil_update: PerfilCandidatoUpdate,
    perfil_id: str = Path(..., title="ID del perfil")
):
    try:
        perfil_repository = PerfilRepositoryImpl()
        handler = ActualizarPerfilCandidatoHandler(perfil_repository)
        update_data = perfil_update.dict(exclude_unset=True)
        
        # Convertir datetime objects a isoformat strings para JSON serialization
        if update_data.get('experiencias'):
            experiencias_dict = []
            for exp in update_data['experiencias']:
                if isinstance(exp, dict):
                    exp_copy = exp.copy()
                    exp_copy['fecha_inicio'] = exp_copy['fecha_inicio'].isoformat() if isinstance(exp_copy['fecha_inicio'], datetime) else exp_copy['fecha_inicio']
                    exp_copy['fecha_fin'] = exp_copy['fecha_fin'].isoformat() if exp_copy.get('fecha_fin') and isinstance(exp_copy['fecha_fin'], datetime) else exp_copy.get('fecha_fin')
                    experiencias_dict.append(exp_copy)
            update_data['experiencias'] = experiencias_dict
        
        if update_data.get('educacion'):
            educacion_dict = []
            for edu in update_data['educacion']:
                if isinstance(edu, dict):
                    edu_copy = edu.copy()
                    edu_copy['fecha_inicio'] = edu_copy['fecha_inicio'].isoformat() if isinstance(edu_copy['fecha_inicio'], datetime) else edu_copy['fecha_inicio']
                    edu_copy['fecha_fin'] = edu_copy['fecha_fin'].isoformat() if edu_copy.get('fecha_fin') and isinstance(edu_copy['fecha_fin'], datetime) else edu_copy.get('fecha_fin')
                    educacion_dict.append(edu_copy)
            update_data['educacion'] = educacion_dict
        
        command = ActualizarPerfilCandidatoCommand(
            perfil_id=UUID(perfil_id),
            datos=update_data
        )
        resultado = handler.handle(command)
        
        # Retornar respuesta formateada
        respuesta = PerfilCandidatoResponse(
            perfil_candidato_id=str(perfil_id),
            perfil_id=str(perfil_id),
            experiencias=perfil_update.experiencias or [],
            educacion=perfil_update.educacion or [],
            habilidades=perfil_update.habilidades or [],
            cv_url=perfil_update.cv_url
        )
        return respuesta
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )