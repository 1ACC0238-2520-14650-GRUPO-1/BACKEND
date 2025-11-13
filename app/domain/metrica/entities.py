from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from app.domain.common import AggregateRoot


@dataclass
class MetricaRegistro:
    """Entity que guarda las métricas del usuario"""
    perfil_id: UUID
    total_postulaciones: int = 0
    total_entrevistas: int = 0
    total_exitos: int = 0
    total_rechazos: int = 0
    tasa_exito: float = 0.0
    
    def aumentar_postulaciones(self) -> None:
        """Incrementa el contador de postulaciones"""
        self.total_postulaciones += 1
        self._recalcular_tasa_exito()
    
    def aumentar_entrevistas(self) -> None:
        """Incrementa el contador de entrevistas"""
        self.total_entrevistas += 1
    
    def aumentar_ofertas(self) -> None:
        """Incrementa el contador de ofertas exitosas"""
        self.total_exitos += 1
        self._recalcular_tasa_exito()
    
    def aumentar_rechazos(self) -> None:
        """Incrementa el contador de rechazos"""
        self.total_rechazos += 1
        self._recalcular_tasa_exito()
    
    def _recalcular_tasa_exito(self) -> None:
        """Recalcula la tasa de éxito basada en postulaciones y ofertas"""
        if self.total_postulaciones > 0:
            self.tasa_exito = (self.total_exitos / self.total_postulaciones) * 100
        else:
            self.tasa_exito = 0.0


@dataclass(frozen=True)
class Logro:
    """Value Object que representa un logro de gamificación"""
    id_logro: UUID = field(default_factory=uuid4)
    nombre_logro: str = ""
    umbral: int = 0
    fecha_obtencion: datetime = field(default_factory=datetime.now)
    
    def verificar_logro(self, total_postulaciones: int, total_entrevistas: int, total_exitos: int) -> bool:
        """
        Verifica si se alcanzó el umbral necesario para el logro según su tipo
        """
        # Ejemplo: si este es un logro de "5 postulaciones"
        if "postulaciones" in self.nombre_logro.lower() and total_postulaciones >= self.umbral:
            return True
        
        # Ejemplo: si este es un logro de "3 entrevistas"
        elif "entrevista" in self.nombre_logro.lower() and total_entrevistas >= self.umbral:
            return True
        
        # Ejemplo: si este es un logro de "2 ofertas"
        elif "oferta" in self.nombre_logro.lower() and total_exitos >= self.umbral:
            return True
        
        return False


@dataclass
class MetricaAggregate(AggregateRoot):
    """
    Aggregate que agrupa la entidad MetricaRegistro y su lista de Logros
    """
    metrica_registro: MetricaRegistro
    lista_logros: List[Logro] = field(default_factory=list)
    
    def aplicar_postulacion_creada(self) -> None:
        """
        Incrementa el contador de postulaciones y evalúa logros
        """
        self.metrica_registro.aumentar_postulaciones()
        self.add_event(MetricaActualizada(
            self.metrica_registro.perfil_id,
            "postulacion_creada"
        ))
    
    def aplicar_estado_actualizado(self, estado_anterior: str, estado_nuevo: str) -> None:
        """
        Actualiza contadores según la transición de estado de una postulación
        """
        # Si pasó a entrevista
        if estado_nuevo == "entrevista" and estado_anterior != "entrevista":
            self.metrica_registro.aumentar_entrevistas()
            self.add_event(MetricaActualizada(
                self.metrica_registro.perfil_id,
                "entrevista_conseguida"
            ))
        
        # Si pasó a oferta
        elif estado_nuevo == "oferta" and estado_anterior != "oferta":
            self.metrica_registro.aumentar_ofertas()
            self.add_event(MetricaActualizada(
                self.metrica_registro.perfil_id,
                "oferta_conseguida"
            ))
        
        # Si pasó a rechazo
        elif estado_nuevo == "rechazo" and estado_anterior != "rechazo":
            self.metrica_registro.aumentar_rechazos()
            self.add_event(MetricaActualizada(
                self.metrica_registro.perfil_id,
                "postulacion_rechazada"
            ))
    
    def aplicar_postulacion_eliminada(self) -> None:
        """
        Ajusta contadores cuando se elimina una postulación
        """
        # Decrementar postulaciones
        if self.metrica_registro.total_postulaciones > 0:
            self.metrica_registro.total_postulaciones -= 1
            self.metrica_registro._recalcular_tasa_exito()
            self.add_event(MetricaActualizada(
                self.metrica_registro.perfil_id,
                "postulacion_eliminada"
            ))
    
    def evaluar_logros(self, lista_reglas: List[dict]) -> List[Logro]:
        """
        Evalúa y otorga logros según las reglas y el estado actual de las métricas
        """
        nuevos_logros = []
        
        for regla in lista_reglas:
            # Verificar si ya tiene este logro
            if any(logro.nombre_logro == regla["nombre"] for logro in self.lista_logros):
                continue
            
            # Crear logro temporal para verificar
            logro_temp = Logro(
                nombre_logro=regla["nombre"],
                umbral=regla["umbral"]
            )
            
            # Verificar si cumple requisitos
            if logro_temp.verificar_logro(
                self.metrica_registro.total_postulaciones,
                self.metrica_registro.total_entrevistas,
                self.metrica_registro.total_exitos
            ):
                # Agregar a la lista de logros
                self.lista_logros.append(logro_temp)
                nuevos_logros.append(logro_temp)
                
                # Emitir evento de logro conseguido
                self.add_event(LogroConseguido(
                    self.metrica_registro.perfil_id,
                    logro_temp.nombre_logro
                ))
        
        return nuevos_logros


# Eventos de dominio
@dataclass
class MetricaActualizada:
    """Evento que se emite cuando se actualiza una métrica"""
    perfil_id: UUID
    tipo_actualizacion: str


@dataclass
class LogroConseguido:
    """Evento que se emite cuando un postulante consigue un logro"""
    perfil_id: UUID
    nombre_logro: str