from typing import List, Optional
from uuid import UUID

from app.domain.puesto.entities import PuestoAggregate
from app.domain.puesto.repositories import PuestoRepository
from app.infrastructure.database.connection import SessionLocal
from app.infrastructure.puesto.models import PuestoModel, PuestoMapeo


class PuestoRepositoryImpl(PuestoRepository):
    """
    Implementación del repositorio de puestos con SQLAlchemy
    La BD actual solo tiene columnas: id (INTEGER), titulo, empresa, descripcion, estado
    Usamos una tabla de mapeo para enlazar UUIDs del dominio a IDs de BD
    """
    
    def __init__(self):
        pass
    
    def guardar(self, puesto_aggregate: PuestoAggregate) -> UUID:
        """Guarda o actualiza un puesto y devuelve su ID"""
        db = SessionLocal()
        try:
            puesto = puesto_aggregate.puesto
            puesto_id = puesto.puesto_id
            empresa_id_str = str(puesto.empresa_id)
            puesto_id_str = str(puesto_id)
            
            # Buscar el mapeo existente
            mapeo_existente = db.query(PuestoMapeo).filter(
                PuestoMapeo.uuid_id == puesto_id_str
            ).first()
            
            if mapeo_existente:
                # UPDATE: El puesto ya existe, solo actualizar sus datos
                puesto_db = db.query(PuestoModel).filter(
                    PuestoModel.id == mapeo_existente.bd_id
                ).first()
                if puesto_db:
                    puesto_db.titulo = puesto.titulo
                    puesto_db.empresa = empresa_id_str
                    puesto_db.descripcion = puesto.descripcion
                    puesto_db.estado = puesto.estado
                    db.commit()
            else:
                # INSERT: Nuevo puesto
                puesto_db = PuestoModel(
                    titulo=puesto.titulo,
                    empresa=empresa_id_str,
                    descripcion=puesto.descripcion,
                    estado=puesto.estado or "abierto"
                )
                db.add(puesto_db)
                db.flush()  # Obtener el ID autogenerado
                
                # Guardar mapeo
                mapeo = PuestoMapeo(
                    uuid_id=puesto_id_str,
                    bd_id=puesto_db.id
                )
                db.add(mapeo)
                db.commit()
            
            return puesto_id
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
    
    def obtener_por_id(self, puesto_id: UUID) -> Optional[PuestoAggregate]:
        """Recupera un puesto por su ID"""
        db = SessionLocal()
        try:
            puesto_id_str = str(puesto_id)
            
            # Buscar el mapeo
            mapeo = db.query(PuestoMapeo).filter(
                PuestoMapeo.uuid_id == puesto_id_str
            ).first()
            
            if not mapeo:
                return None
            
            # Buscar el puesto por bd_id
            puesto_db = db.query(PuestoModel).filter(
                PuestoModel.id == mapeo.bd_id
            ).first()
            
            if not puesto_db:
                return None
            
            from app.domain.puesto.entities import Puesto
            
            try:
                empresa_id = UUID(puesto_db.empresa)
            except:
                empresa_id = UUID('00000000-0000-0000-0000-000000000000')
            
            puesto = Puesto(
                puesto_id=puesto_id,
                empresa_id=empresa_id,
                titulo=puesto_db.titulo,
                descripcion=puesto_db.descripcion,
                ubicacion="",
                salario_min=0.0,
                salario_max=0.0,
                moneda="",
                tipo_contrato="",
                estado=puesto_db.estado
            )
            
            puesto_aggregate = PuestoAggregate(puesto=puesto)
            return puesto_aggregate
            
        finally:
            db.close()
    
    def listar_por_empresa(self, empresa_id: UUID) -> List[PuestoAggregate]:
        """Lista los puestos de una empresa específica"""
        db = SessionLocal()
        try:
            empresa_id_str = str(empresa_id)
            puestos_db = db.query(PuestoModel).filter(
                PuestoModel.empresa == empresa_id_str
            ).all()
            
            resultado = []
            for puesto_db in puestos_db:
                try:
                    # Obtener el UUID del mapeo
                    mapeo = db.query(PuestoMapeo).filter(
                        PuestoMapeo.bd_id == puesto_db.id
                    ).first()
                    if mapeo:
                        puesto_agg = self.obtener_por_id(UUID(mapeo.uuid_id))
                        if puesto_agg:
                            resultado.append(puesto_agg)
                except:
                    pass
            
            return resultado
            
        finally:
            db.close()
    
    def listar_por_estado(self, estado: str) -> List[PuestoAggregate]:
        """Lista los puestos según su estado"""
        db = SessionLocal()
        try:
            puestos_db = db.query(PuestoModel).filter(
                PuestoModel.estado == estado
            ).all()
            
            resultado = []
            for puesto_db in puestos_db:
                try:
                    mapeo = db.query(PuestoMapeo).filter(
                        PuestoMapeo.bd_id == puesto_db.id
                    ).first()
                    if mapeo:
                        puesto_agg = self.obtener_por_id(UUID(mapeo.uuid_id))
                        if puesto_agg:
                            resultado.append(puesto_agg)
                except:
                    pass
            
            return resultado
            
        finally:
            db.close()
    
    def listar_todos(self) -> List[PuestoAggregate]:
        """Lista todos los puestos"""
        db = SessionLocal()
        try:
            puestos_db = db.query(PuestoModel).all()
            
            resultado = []
            for puesto_db in puestos_db:
                try:
                    mapeo = db.query(PuestoMapeo).filter(
                        PuestoMapeo.bd_id == puesto_db.id
                    ).first()
                    if mapeo:
                        puesto_agg = self.obtener_por_id(UUID(mapeo.uuid_id))
                        if puesto_agg:
                            resultado.append(puesto_agg)
                except:
                    pass
            
            return resultado
            
        finally:
            db.close()
    
    def eliminar(self, puesto_id: UUID) -> bool:
        """Elimina un puesto por su ID"""
        db = SessionLocal()
        try:
            puesto_id_str = str(puesto_id)
            
            # Buscar el mapeo
            mapeo = db.query(PuestoMapeo).filter(
                PuestoMapeo.uuid_id == puesto_id_str
            ).first()
            
            if not mapeo:
                return False
            
            # Eliminar de BD
            puesto_db = db.query(PuestoModel).filter(
                PuestoModel.id == mapeo.bd_id
            ).first()
            
            if puesto_db:
                db.delete(puesto_db)
            
            # Eliminar mapeo
            db.delete(mapeo)
            db.commit()
            
            return True
            
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()
