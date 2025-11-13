from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.domain.common import Query, QueryHandler
from app.domain.perfil.entities import TipoPerfilEnum
from app.domain.perfil.repositories import PerfilRepository


@dataclass
class ObtenerPerfilQuery(Query):
    """Query para obtener un perfil por ID"""
    perfil_id: UUID


class ObtenerPerfilQueryHandler(QueryHandler):
    """
    Manejador de consulta para obtener un perfil por ID
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, query: ObtenerPerfilQuery) -> Optional[Dict[str, Any]]:
        """
        Maneja la consulta de perfil por ID
        """
        # Recuperar el perfil
        perfil_aggregate = self.perfil_repository.obtener_por_id(query.perfil_id)
        
        if not perfil_aggregate:
            return None
        
        perfil = perfil_aggregate.perfil
        
        # Helper para convertir datetime a string si es necesario
        def to_isoformat(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            return dt.isoformat()
        
        # Construir respuesta base
        resultado = {
            "perfil_id": str(perfil.perfil_id),
            "tipo_perfil": perfil.tipo_perfil.value,
            "datos_personales": perfil.datos_personales,
            "rol_asignado": perfil.rol_asignado,
            "fecha_creacion": to_isoformat(perfil.fecha_creacion),
            "fecha_actualizacion": to_isoformat(perfil.fecha_actualizacion),
            "preferencias": [
                {
                    "tipo": pref.tipo_preferencia,
                    "valor": pref.valor,
                    "fecha_configuracion": to_isoformat(pref.fecha_configuracion)
                }
                for pref in perfil_aggregate.lista_preferencias
            ]
        }
        
        return resultado


@dataclass
class ListarPerfilesPorTipoQuery(Query):
    """Query para listar perfiles por tipo"""
    tipo_perfil: TipoPerfilEnum


class ListarPerfilesPorTipoQueryHandler(QueryHandler):
    """
    Manejador de consulta para listar perfiles por tipo
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, query: ListarPerfilesPorTipoQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta de perfiles por tipo
        """
        # Recuperar los perfiles por tipo
        perfiles = self.perfil_repository.obtener_por_tipo(query.tipo_perfil)
        
        # Helper para convertir datetime a string si es necesario
        def to_isoformat(dt):
            if dt is None:
                return None
            if isinstance(dt, str):
                return dt
            return dt.isoformat()
        
        # Construir respuesta resumida
        return [
            {
                "perfil_id": str(agg.perfil.perfil_id),
                "tipo_perfil": agg.perfil.tipo_perfil.value,
                "nombre": agg.perfil.datos_personales.get("nombre", ""),
                "apellido": agg.perfil.datos_personales.get("apellido", ""),
                "correo": agg.perfil.datos_personales.get("correo", ""),
                "foto": agg.perfil.datos_personales.get("foto", None),
                "fecha_creacion": to_isoformat(agg.perfil.fecha_creacion)
            }
            for agg in perfiles
        ]


@dataclass
class ObtenerDocumentosPerfilQuery(Query):
    """
    Query para obtener los documentos guardados en el perfil
    US20: Visualizar documentos guardados en el perfil
    """
    perfil_id: UUID


class ObtenerDocumentosPerfilQueryHandler(QueryHandler):
    """
    Manejador para obtener documentos guardados en el perfil
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, query: ObtenerDocumentosPerfilQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta de documentos del perfil
        """
        return self.perfil_repository.obtener_documentos(query.perfil_id)