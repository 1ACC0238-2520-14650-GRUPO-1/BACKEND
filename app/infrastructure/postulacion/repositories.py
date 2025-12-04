from typing import List, Optional
from uuid import UUID
from datetime import datetime

from app.domain.postulacion.entities import (
    Postulacion, PostulacionAggregate,
    EstadoPostulacion, LineaDeTiempo, Hito
)
from app.domain.postulacion.repositories import PostulacionRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.postulacion.models import PostulacionModel, HitoModel


class PostulacionRepositoryImpl(PostulacionRepository):
    """Repositorio simplificado de postulaciones"""
    
    def guardar(self, postulacion_aggregate: PostulacionAggregate) -> UUID:
        """Guarda una postulación y devuelve su ID"""
        db = SessionLocal()
        try:
            post = postulacion_aggregate.postulacion
            post_id = post.postulacion_id
            
            # Crear nueva postulación - pasar el valor string del enum
            post_db = PostulacionModel(
                postulacion_id=str(post.postulacion_id),
                cuenta_id=str(post.candidato_id),
                puesto_id=str(post.puesto_id),
                fecha_postulacion=post.fecha_postulacion,
                estado=post.estado.valor.value,
                resultado=None
            )
            db.add(post_db)
            db.flush()
            
            # Guardar hitos
            for hito in postulacion_aggregate.linea_de_tiempo.lista_hitos:
                hito_db = HitoModel(
                    postulacion_id=post_db.id,
                    fecha=hito.fecha,
                    descripcion=hito.descripcion
                )
                db.add(hito_db)
            
            db.commit()
            return post_id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def obtener_por_id(self, postulacion_id: UUID) -> Optional[PostulacionAggregate]:
        """Obtiene una postulación por ID"""
        db = SessionLocal()
        try:
            # Buscar por postulacion_id (UUID)
            post_db = db.query(PostulacionModel).filter(
                PostulacionModel.postulacion_id == str(postulacion_id)
            ).first()
            
            if not post_db:
                return None
            
            post = Postulacion(
                postulacion_id=UUID(post_db.postulacion_id) if post_db.postulacion_id else postulacion_id,
                candidato_id=UUID(post_db.cuenta_id),
                puesto_id=UUID(post_db.puesto_id) if post_db.puesto_id else UUID('00000000-0000-0000-0000-000000000001'),
                fecha_postulacion=post_db.fecha_postulacion,
                estado=EstadoPostulacion(post_db.estado),
                documentos_adjuntos=[]
            )
            
            linea_tiempo = LineaDeTiempo()
            for hito_db in post_db.hitos:
                hito = Hito(
                    hito_id=UUID(f'00000000-0000-0000-0000-{hito_db.id:012d}'),
                    fecha=hito_db.fecha,
                    descripcion=hito_db.descripcion
                )
                linea_tiempo.lista_hitos.append(hito)
            
            return PostulacionAggregate(
                postulacion=post,
                estado=post.estado,
                linea_de_tiempo=linea_tiempo
            )
        finally:
            db.close()
    
    def obtener_por_candidato(self, candidato_id: UUID) -> List[PostulacionAggregate]:
        """Obtiene todas las postulaciones de un candidato"""
        db = SessionLocal()
        try:
            posts_db = db.query(PostulacionModel).filter(
                PostulacionModel.cuenta_id == str(candidato_id)
            ).all()
            
            resultado = []
            for post_db in posts_db:
                post = Postulacion(
                    postulacion_id=UUID(post_db.postulacion_id) if post_db.postulacion_id else UUID('00000000-0000-0000-0000-000000000001'),
                    candidato_id=UUID(post_db.cuenta_id),
                    puesto_id=UUID(post_db.puesto_id) if post_db.puesto_id else UUID('00000000-0000-0000-0000-000000000001'),
                    fecha_postulacion=post_db.fecha_postulacion,
                    estado=EstadoPostulacion(post_db.estado),
                    documentos_adjuntos=[]
                )
                
                linea_tiempo = LineaDeTiempo()
                for hito_db in post_db.hitos:
                    hito = Hito(
                        hito_id=UUID(f'00000000-0000-0000-0000-{hito_db.id:012d}'),
                        fecha=hito_db.fecha,
                        descripcion=hito_db.descripcion
                    )
                    linea_tiempo.lista_hitos.append(hito)
                
                resultado.append(PostulacionAggregate(
                    postulacion=post,
                    estado=post.estado,
                    linea_de_tiempo=linea_tiempo
                ))
            
            return resultado
        finally:
            db.close()
    
    def obtener_por_puesto(self, puesto_id: UUID) -> List[PostulacionAggregate]:
        """Obtiene todas las postulaciones para un puesto"""
        db = SessionLocal()
        try:
            # Placeholder: devolver lista vacía
            return []
        finally:
            db.close()
    
    def actualizar_estado_postulacion(self, postulacion_id: UUID, nuevo_estado: str, descripcion: str) -> bool:
        """Actualiza estado de postulación"""
        db = SessionLocal()
        try:
            from app.domain.postulacion.entities import EstadoPostulacionEnum
            # Buscar la postulación por su UUID
            post_db = db.query(PostulacionModel).filter(
                PostulacionModel.postulacion_id == str(postulacion_id)
            ).first()
            if not post_db:
                return False
            
            # Convertir string a enum y pasar su value
            post_db.estado = EstadoPostulacionEnum(nuevo_estado).value
            
            hito = HitoModel(
                postulacion_id=post_db.id,
                fecha=datetime.now(),
                descripcion=descripcion
            )
            db.add(hito)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            return False
        finally:
            db.close()
