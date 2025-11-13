from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from app.domain.perfil.entities import (
    Perfil, PerfilAggregate, Preferencia, TipoPerfilEnum
)
from app.domain.perfil.repositories import PerfilRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.perfil.models import (
    PerfilModel, PreferenciaModel, HistorialCambioModel
)


class PerfilRepositoryImpl(PerfilRepository):
    """
    Implementación del repositorio de perfiles con SQLAlchemy
    """
    
    def __init__(self):
        pass
    
    def guardar(self, perfil_aggregate: PerfilAggregate) -> UUID:
        """Guarda o actualiza un perfil y devuelve su ID"""
        db = SessionLocal()
        try:
            perfil = perfil_aggregate.perfil
            perfil_id = perfil.perfil_id
            
            # Verificar si ya existe el perfil
            perfil_db = db.query(PerfilModel).filter(
                PerfilModel.id == str(perfil_id)
            ).first()
            
            if not perfil_db:
                # Crear nuevo perfil
                perfil_db = PerfilModel(
                    id=str(perfil_id),
                    tipo_perfil=perfil.tipo_perfil,
                    datos_personales=perfil.datos_personales,
                    rol_asignado=perfil.rol_asignado,
                    fecha_creacion=perfil.fecha_creacion,
                    fecha_actualizacion=perfil.fecha_actualizacion
                )
                db.add(perfil_db)
            else:
                # Actualizar perfil existente
                perfil_db.datos_personales = perfil.datos_personales
                perfil_db.rol_asignado = perfil.rol_asignado
                perfil_db.fecha_actualizacion = perfil.fecha_actualizacion
            
            # Eliminar preferencias existentes para reemplazarlas
            db.query(PreferenciaModel).filter(
                PreferenciaModel.perfil_id == str(perfil_id)
            ).delete()
            
            # Guardar preferencias
            for preferencia in perfil_aggregate.lista_preferencias:
                preferencia_db = PreferenciaModel(
                    id=str(preferencia.id_preferencia),
                    perfil_id=str(perfil_id),
                    tipo_preferencia=preferencia.tipo_preferencia,
                    valor=preferencia.valor,
                    fecha_configuracion=preferencia.fecha_configuracion
                )
                db.add(preferencia_db)
            
            # Guardar historial de cambios
            for cambio in perfil_aggregate.historial_cambios:
                historial_db = HistorialCambioModel(
                    id=str(uuid4()),
                    perfil_id=str(perfil_id),
                    tipo_cambio=cambio["tipo_cambio"],
                    fecha=cambio["fecha"],
                    detalles=cambio["detalles"]
                )
                db.add(historial_db)
            
            db.commit()
            return perfil_id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def obtener_por_id(self, perfil_id: UUID) -> Optional[PerfilAggregate]:
        """Recupera un perfil por su ID"""
        db = SessionLocal()
        try:
            # Consultar el perfil
            perfil_db = db.query(PerfilModel).filter(
                PerfilModel.id == str(perfil_id)
            ).first()
            
            if not perfil_db:
                return None
            
            # Asegurar que fecha_creacion es un datetime
            fecha_creacion = perfil_db.fecha_creacion
            if isinstance(fecha_creacion, str):
                fecha_creacion = datetime.fromisoformat(fecha_creacion)
            
            # Asegurar que fecha_actualizacion es un datetime o None
            fecha_actualizacion = perfil_db.fecha_actualizacion
            if isinstance(fecha_actualizacion, str):
                fecha_actualizacion = datetime.fromisoformat(fecha_actualizacion)
            
            # Crear entidad Perfil
            perfil = Perfil(
                perfil_id=UUID(perfil_db.id),
                tipo_perfil=perfil_db.tipo_perfil,
                datos_personales=perfil_db.datos_personales or {},
                rol_asignado=perfil_db.rol_asignado,
                fecha_creacion=fecha_creacion,
                fecha_actualizacion=fecha_actualizacion
            )
            
            # Recuperar preferencias (con lazy loading forzado)
            lista_preferencias = []
            try:
                for pref_db in perfil_db.preferencias:
                    preferencia = Preferencia(
                        id_preferencia=UUID(pref_db.id),
                        tipo_preferencia=pref_db.tipo_preferencia,
                        valor=pref_db.valor,
                        fecha_configuracion=pref_db.fecha_configuracion
                    )
                    lista_preferencias.append(preferencia)
            except Exception as e:
                # Si hay error cargando preferencias, continuar sin ellas
                print(f"Error cargando preferencias: {e}")
                lista_preferencias = []
            
            # Recuperar historial de cambios (con lazy loading forzado)
            historial_cambios = []
            try:
                for cambio_db in perfil_db.historial_cambios:
                    cambio = {
                        "tipo_cambio": cambio_db.tipo_cambio,
                        "fecha": cambio_db.fecha,
                        "detalles": cambio_db.detalles
                    }
                    historial_cambios.append(cambio)
            except Exception as e:
                # Si hay error cargando historial, continuar sin él
                print(f"Error cargando historial: {e}")
                historial_cambios = []
            
            # Crear agregado
            perfil_aggregate = PerfilAggregate(
                perfil=perfil,
                lista_preferencias=lista_preferencias,
                historial_cambios=historial_cambios
            )
            
            return perfil_aggregate
            
        finally:
            db.close()
    
    def obtener_por_tipo(self, tipo_perfil: TipoPerfilEnum) -> List[PerfilAggregate]:
        """Recupera todos los perfiles de un tipo específico"""
        db = SessionLocal()
        try:
            # Consultar los perfiles por tipo
            perfiles_db = db.query(PerfilModel).filter(
                PerfilModel.tipo_perfil == tipo_perfil
            ).all()
            
            resultado = []
            for perfil_db in perfiles_db:
                # Obtener cada perfil completo
                perfil_aggregate = self.obtener_por_id(UUID(perfil_db.id))
                if perfil_aggregate:
                    resultado.append(perfil_aggregate)
            
            return resultado
            
        finally:
            db.close()
    
    def agregar_documento(self, perfil_id: UUID, documento: dict) -> bool:
        """
        Agrega un documento al perfil del postulante
        US18: Subir documentos al perfil
        """
        perfil_aggregate = self.obtener_por_id(perfil_id)
        if not perfil_aggregate:
            return False
            
        # Verificar si los documentos existen en los datos personales
        if 'documentos' not in perfil_aggregate.perfil.datos_personales:
            perfil_aggregate.perfil.datos_personales['documentos'] = []
            
        # Agregar documento
        perfil_aggregate.perfil.datos_personales['documentos'].append(documento)
        
        # Registrar cambio en historial
        perfil_aggregate.historial_cambios.append({
            "tipo_cambio": "documento_agregado",
            "fecha": datetime.now().isoformat(),
            "detalles": f"Se agregó el documento: {documento.get('nombre', 'Sin nombre')}"
        })
        
        # Guardar cambios
        self.guardar(perfil_aggregate)
        return True
    
    def eliminar_documento(self, perfil_id: UUID, documento_id: str) -> bool:
        """
        Elimina un documento del perfil del postulante
        US19: Eliminar documento del perfil
        """
        perfil_aggregate = self.obtener_por_id(perfil_id)
        if not perfil_aggregate:
            return False
            
        # Verificar si hay documentos
        if 'documentos' not in perfil_aggregate.perfil.datos_personales:
            return False
            
        # Buscar y eliminar documento
        documentos = perfil_aggregate.perfil.datos_personales['documentos']
        documento_eliminado = None
        
        for i, doc in enumerate(documentos):
            if doc.get('id') == documento_id:
                documento_eliminado = documentos.pop(i)
                break
                
        if not documento_eliminado:
            return False
            
        # Registrar cambio en historial
        perfil_aggregate.historial_cambios.append({
            "tipo_cambio": "documento_eliminado",
            "fecha": datetime.now().isoformat(),
            "detalles": f"Se eliminó el documento: {documento_eliminado.get('nombre', 'Sin nombre')}"
        })
        
        # Guardar cambios
        self.guardar(perfil_aggregate)
        return True
    
    def obtener_documentos(self, perfil_id: UUID) -> List[dict]:
        """
        Obtiene todos los documentos del perfil del postulante
        US20: Visualizar documentos guardados en el perfil
        """
        perfil_aggregate = self.obtener_por_id(perfil_id)
        if not perfil_aggregate:
            return []
            
        # Obtener documentos
        if 'documentos' not in perfil_aggregate.perfil.datos_personales:
            return []
            
        return perfil_aggregate.perfil.datos_personales['documentos']
    
    def completar_perfil_basico(self, perfil_id: UUID, datos_basicos: dict) -> bool:
        """
        Completa el perfil básico del postulante
        US12: Completar perfil básico del postulante
        """
        perfil_aggregate = self.obtener_por_id(perfil_id)
        if not perfil_aggregate:
            return False
            
        # Actualizar datos personales
        perfil_aggregate.perfil.datos_personales.update(datos_basicos)
        perfil_aggregate.perfil.fecha_actualizacion = datetime.now()
        
        # Registrar cambio en historial
        perfil_aggregate.historial_cambios.append({
            "tipo_cambio": "perfil_actualizado",
            "fecha": datetime.now().isoformat(),
            "detalles": "Actualización del perfil básico"
        })
        
        # Guardar cambios
        self.guardar(perfil_aggregate)
        return True