from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.domain.common import Query, QueryHandler, EventHandler
from app.domain.postulacion.entities import PostulacionAggregate, PuestoPostulacion, PostulacionCreada, EstadoPostulacionActualizado
from app.domain.postulacion.repositories import PostulacionRepository, PuestoPostulacionRepository


@dataclass
class ObtenerPostulacionQuery(Query):
    """Query para obtener una postulación por ID"""
    postulacion_id: UUID


class ObtenerPostulacionQueryHandler(QueryHandler):
    """
    Manejador de consulta para obtener una postulación por ID
    """
    
    def __init__(self, postulacion_repository: PostulacionRepository):
        self.postulacion_repository = postulacion_repository
    
    def handle(self, query: ObtenerPostulacionQuery) -> Optional[Dict[str, Any]]:
        """
        Maneja la consulta de postulación por ID
        """
        postulacion_aggregate = self.postulacion_repository.obtener_por_id(query.postulacion_id)
        
        if not postulacion_aggregate:
            return None
        
        # Construir respuesta con los datos relevantes
        postulacion = postulacion_aggregate.postulacion
        return {
            "postulacion_id": str(postulacion.postulacion_id),
            "candidato_id": str(postulacion.candidato_id),
            "puesto_id": str(postulacion.puesto_id),
            "fecha_postulacion": postulacion.fecha_postulacion.isoformat(),
            "estado": postulacion.estado.valor.value,
            "documentos_adjuntos": postulacion.documentos_adjuntos,
            "hitos": [
                {
                    "hito_id": str(hito.hito_id),
                    "fecha": hito.fecha.isoformat(),
                    "descripcion": hito.descripcion
                }
                for hito in postulacion_aggregate.linea_de_tiempo.lista_hitos
            ]
        }


@dataclass
class ListarPostulacionesCandidatoQuery(Query):
    """Query para listar postulaciones de un candidato"""
    candidato_id: UUID


class ListarPostulacionesCandidatoQueryHandler(QueryHandler):
    """
    Manejador de consulta para listar postulaciones de un candidato
    """
    
    def __init__(self, postulacion_repository: PostulacionRepository):
        self.postulacion_repository = postulacion_repository
    
    def handle(self, query: ListarPostulacionesCandidatoQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta de postulaciones por candidato
        """
        postulaciones = self.postulacion_repository.obtener_por_candidato(query.candidato_id)
        
        # Construir respuesta con los datos de cada postulación
        return [
            {
                "postulacion_id": str(agg.postulacion.postulacion_id),
                "candidato_id": str(agg.postulacion.candidato_id),
                "puesto_id": str(agg.postulacion.puesto_id),
                "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                "estado": agg.postulacion.estado.valor.value,
                "documentos_adjuntos": agg.postulacion.documentos_adjuntos,
                "hitos": [
                    {
                        "hito_id": str(hito.hito_id),
                        "fecha": hito.fecha.isoformat(),
                        "descripcion": hito.descripcion
                    }
                    for hito in agg.linea_de_tiempo.lista_hitos
                ]
            }
            for agg in postulaciones
        ]


@dataclass
class ObtenerPuestoQuery(Query):
    """Query para obtener detalles de un puesto"""
    puesto_id: UUID


class ObtenerPuestoQueryHandler(QueryHandler):
    """
    Manejador de consulta para obtener detalles de un puesto
    """
    
    def __init__(self, puesto_repository: PuestoPostulacionRepository):
        self.puesto_repository = puesto_repository
    
    def handle(self, query: ObtenerPuestoQuery) -> Optional[Dict[str, Any]]:
        """
        Maneja la consulta de puesto por ID
        """
        puesto = self.puesto_repository.obtener_por_id(query.puesto_id)
        
        if not puesto:
            return None
        
        # Construir respuesta
        return {
            "puesto_id": str(puesto.puesto_id),
            "empresa_id": str(puesto.empresa_id),
            "titulo": puesto.titulo,
            "descripcion": puesto.descripcion,
            "requisitos": puesto.requisitos,
            "fecha_inicio": puesto.fecha_inicio.isoformat(),
            "fecha_fin": puesto.fecha_fin.isoformat() if puesto.fecha_fin else None,
            "estado_publicacion": puesto.estado_publicacion.value
        }


class PostulacionCreadaHandler(EventHandler):
    """
    Manejador de eventos para PostulacionCreada
    """
    
    def handle(self, event: PostulacionCreada) -> None:
        """
        Maneja el evento de postulación creada
        Este handler puede notificar a otros bounded contexts como métricas
        """
        # Aquí se implementaría la lógica para notificar a otros bounded contexts
        # Por ejemplo, enviar un evento al servicio de métricas
        pass


class EstadoPostulacionActualizadoHandler(EventHandler):
    """
    Manejador de eventos para EstadoPostulacionActualizado
    """
    
    def handle(self, event: EstadoPostulacionActualizado) -> None:
        """
        Maneja el evento de estado de postulación actualizado
        
        Nota: No se requiere actualizar métricas explícitamente, ya que 
        el repositorio de métricas calcula los valores en tiempo real
        basándose en el estado actual de las postulaciones.
        """
        # La implementación está vacía porque las métricas se calculan
        # bajo demanda cuando son solicitadas. No es necesario almacenar
        # o actualizar ningún contador de forma explícita.
        pass


@dataclass
class ObtenerHistorialCompletoQuery(Query):
    """
    Query para obtener historial completo de postulaciones
    US25: Ver historial completo de postulaciones
    """
    candidato_id: UUID


class ObtenerHistorialCompletoQueryHandler(QueryHandler):
    """
    Manejador para obtener historial completo de postulaciones de un candidato
    """
    
    def __init__(self, postulacion_repository: PostulacionRepository):
        self.postulacion_repository = postulacion_repository
    
    def handle(self, query: ObtenerHistorialCompletoQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta del historial completo
        """
        postulaciones = self.postulacion_repository.obtener_historial_completo(query.candidato_id)
        
        # Construir respuesta con los datos detallados de cada postulación
        return [
            {
                "postulacion_id": str(agg.postulacion.postulacion_id),
                "puesto_id": str(agg.postulacion.puesto_id),
                "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                "estado": agg.postulacion.estado.valor.value,
                "documentos_adjuntos": agg.postulacion.documentos_adjuntos,
                "hitos": [
                    {
                        "fecha": hito.fecha.isoformat(),
                        "descripcion": hito.descripcion
                    }
                    for hito in agg.linea_de_tiempo.lista_hitos
                ]
            }
            for agg in postulaciones
        ]


@dataclass
class BuscarPostulacionesQuery(Query):
    """
    Query para buscar postulaciones por empresa o puesto
    US26: Buscar postulaciones por empresa o puesto
    """
    candidato_id: UUID
    termino_busqueda: str


class BuscarPostulacionesQueryHandler(QueryHandler):
    """
    Manejador para buscar postulaciones por término de búsqueda
    """
    
    def __init__(self, postulacion_repository: PostulacionRepository):
        self.postulacion_repository = postulacion_repository
    
    def handle(self, query: BuscarPostulacionesQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta de búsqueda
        """
        postulaciones = self.postulacion_repository.buscar_por_empresa_o_puesto(
            query.candidato_id, 
            query.termino_busqueda
        )
        
        # Construir respuesta con los datos de cada postulación
        return [
            {
                "postulacion_id": str(agg.postulacion.postulacion_id),
                "puesto_id": str(agg.postulacion.puesto_id),
                "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                "estado": agg.postulacion.estado.valor.value
            }
            for agg in postulaciones
        ]


@dataclass
class FiltrarPostulacionesQuery(Query):
    """
    Query para filtrar postulaciones por estado
    US27: Filtrar por estado de postulación
    """
    candidato_id: UUID
    estado: str


class FiltrarPostulacionesQueryHandler(QueryHandler):
    """
    Manejador para filtrar postulaciones por estado
    """
    
    def __init__(self, postulacion_repository: PostulacionRepository):
        self.postulacion_repository = postulacion_repository
    
    def handle(self, query: FiltrarPostulacionesQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta de filtrado
        """
        postulaciones = self.postulacion_repository.filtrar_por_estado(
            query.candidato_id, 
            query.estado
        )
        
        # Construir respuesta con los datos de cada postulación
        return [
            {
                "postulacion_id": str(agg.postulacion.postulacion_id),
                "puesto_id": str(agg.postulacion.puesto_id),
                "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                "estado": agg.postulacion.estado.valor.value
            }
            for agg in postulaciones
        ]


@dataclass
class OrdenarPostulacionesQuery(Query):
    """
    Query para ordenar postulaciones por fecha o resultado
    US28: Ordenar postulaciones por fecha o resultado
    """
    candidato_id: UUID
    criterio: str  # "fecha" o "estado"
    descendente: bool = False


class OrdenarPostulacionesQueryHandler(QueryHandler):
    """
    Manejador para ordenar postulaciones
    """
    
    def __init__(self, postulacion_repository: PostulacionRepository):
        self.postulacion_repository = postulacion_repository
    
    def handle(self, query: OrdenarPostulacionesQuery) -> List[Dict[str, Any]]:
        """
        Maneja la consulta de ordenación
        """
        postulaciones = self.postulacion_repository.ordenar_postulaciones(
            query.candidato_id, 
            query.criterio,
            query.descendente
        )
        
        # Construir respuesta con los datos de cada postulación
        return [
            {
                "postulacion_id": str(agg.postulacion.postulacion_id),
                "puesto_id": str(agg.postulacion.puesto_id),
                "fecha_postulacion": agg.postulacion.fecha_postulacion.isoformat(),
                "estado": agg.postulacion.estado.valor.value
            }
            for agg in postulaciones
        ]
