from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from app.domain.common import AggregateRoot


class TipoPerfilEnum(str, Enum):
    """Valores posibles para el tipo de perfil"""
    POSTULANTE = "postulante"
    EMPRESA = "empresa"


@dataclass(frozen=True)
class Preferencia:
    """Value Object que representa las configuraciones personalizadas del usuario"""
    id_preferencia: UUID = field(default_factory=uuid4)
    tipo_preferencia: str = ""
    valor: str = ""
    fecha_configuracion: datetime = field(default_factory=datetime.now)
    
    def validar_preferencia(self) -> bool:
        """
        Valida que la preferencia tenga un tipo y valor válidos
        """
        return (self.tipo_preferencia and self.tipo_preferencia.strip() != "" and 
                self.valor and self.valor.strip() != "")
    
    def actualizar_preferencia(self, nuevo_valor: str) -> 'Preferencia':
        """
        Crea una nueva preferencia con el valor actualizado (inmutabilidad)
        """
        return Preferencia(
            id_preferencia=self.id_preferencia,
            tipo_preferencia=self.tipo_preferencia,
            valor=nuevo_valor,
            fecha_configuracion=datetime.now()
        )


@dataclass
class Perfil:
    """Entity que representa el perfil de un usuario"""
    perfil_id: UUID = field(default_factory=uuid4)
    tipo_perfil: TipoPerfilEnum = TipoPerfilEnum.POSTULANTE
    datos_personales: Dict[str, Any] = field(default_factory=dict)
    rol_asignado: Optional[str] = None
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_actualizacion: Optional[datetime] = None
    
    def crear_perfil(self, datos: Dict[str, Any]) -> None:
        """Inicializa el perfil con los datos proporcionados"""
        self.datos_personales = datos.copy()
    
    def actualizar_datos(self, datos: Dict[str, Any]) -> None:
        """Actualiza los datos del perfil"""
        self.datos_personales.update(datos)
        self.fecha_actualizacion = datetime.now()
    
    def asignar_rol(self, rol: str) -> None:
        """Asigna un rol al perfil"""
        self.rol_asignado = rol
        self.fecha_actualizacion = datetime.now()
    
    def configurar_preferencias(self, preferencias: Dict[str, str]) -> None:
        """
        Este método será implementado en el agregado
        """
        pass


@dataclass
class PerfilAggregate(AggregateRoot):
    """
    Aggregate que sirve como raíz de consistencia para todo lo relacionado al perfil
    """
    perfil: Perfil
    lista_preferencias: List[Preferencia] = field(default_factory=list)
    historial_cambios: List[Dict[str, Any]] = field(default_factory=list)
    
    def aplicar_creacion_perfil(self, datos: Dict[str, Any]) -> None:
        """
        Aplica la creación de un perfil y registra el cambio
        """
        self.perfil.crear_perfil(datos)
        
        self._registrar_cambio("creacion", {
            "fecha": self.perfil.fecha_creacion,
            "tipo_perfil": self.perfil.tipo_perfil.value
        })
        
        self.add_event(PerfilCreado(
            self.perfil.perfil_id,
            self.perfil.tipo_perfil
        ))
    
    def aplicar_actualizacion_datos(self, datos: Dict[str, Any]) -> None:
        """
        Aplica la actualización de datos y registra el cambio
        """
        self.perfil.actualizar_datos(datos)
        
        self._registrar_cambio("actualizacion_datos", {
            "fecha": self.perfil.fecha_actualizacion,
            "campos": list(datos.keys())
        })
        
        self.add_event(DatosPerfilActualizados(
            self.perfil.perfil_id,
            list(datos.keys())
        ))
    
    def aplicar_cambio_foto(self, ruta_foto: str) -> None:
        """
        Aplica el cambio de foto y registra el cambio
        """
        self.perfil.actualizar_datos({"foto": ruta_foto})
        
        self._registrar_cambio("cambio_foto", {
            "fecha": self.perfil.fecha_actualizacion,
            "ruta_foto": ruta_foto
        })
        
        self.add_event(FotoPerfilActualizada(
            self.perfil.perfil_id,
            ruta_foto
        ))
    
    def aplicar_configuracion_preferencias(self, preferencias: Dict[str, str]) -> None:
        """
        Aplica la configuración de preferencias y registra el cambio
        """
        nuevas_preferencias = []
        tipos_actualizados = []
        
        for tipo, valor in preferencias.items():
            # Buscar si ya existe esta preferencia para actualizarla
            encontrado = False
            for i, pref in enumerate(self.lista_preferencias):
                if pref.tipo_preferencia == tipo:
                    # Actualizar preferencia existente
                    self.lista_preferencias[i] = pref.actualizar_preferencia(valor)
                    encontrado = True
                    tipos_actualizados.append(tipo)
                    break
            
            # Si no existe, crear nueva preferencia
            if not encontrado:
                nueva_pref = Preferencia(
                    tipo_preferencia=tipo,
                    valor=valor
                )
                
                if nueva_pref.validar_preferencia():
                    nuevas_preferencias.append(nueva_pref)
                    tipos_actualizados.append(tipo)
        
        # Agregar nuevas preferencias a la lista
        self.lista_preferencias.extend(nuevas_preferencias)
        
        self._registrar_cambio("configuracion_preferencias", {
            "fecha": datetime.now(),
            "preferencias_actualizadas": tipos_actualizados
        })
        
        self.add_event(PreferenciasActualizadas(
            self.perfil.perfil_id,
            tipos_actualizados
        ))
    
    def aplicar_actualizacion_empresa(self, datos_empresa: Dict[str, Any]) -> None:
        """
        Aplica actualizaciones específicas para perfiles de empresa
        """
        if self.perfil.tipo_perfil != TipoPerfilEnum.EMPRESA:
            return
        
        self.perfil.actualizar_datos(datos_empresa)
        
        self._registrar_cambio("actualizacion_empresa", {
            "fecha": self.perfil.fecha_actualizacion,
            "campos": list(datos_empresa.keys())
        })
        
        self.add_event(DatosEmpresaActualizados(
            self.perfil.perfil_id,
            list(datos_empresa.keys())
        ))
    
    def _convertir_datetime_a_string(self, obj: Any) -> Any:
        """
        Convierte recursivamente objetos datetime a strings ISO en diccionarios y listas
        """
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self._convertir_datetime_a_string(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._convertir_datetime_a_string(item) for item in obj]
        else:
            return obj
    
    def _registrar_cambio(self, tipo_cambio: str, detalles: Dict[str, Any]) -> None:
        """
        Registra un cambio en el historial del perfil
        """
        # Convertir datetime a string ISO en detalles
        detalles_serializable = self._convertir_datetime_a_string(detalles)
        
        self.historial_cambios.append({
            "tipo_cambio": tipo_cambio,
            "fecha": datetime.now().isoformat(),
            "detalles": detalles_serializable
        })


# Eventos de dominio
@dataclass
class PerfilCreado:
    """Evento que se emite cuando se crea un nuevo perfil"""
    perfil_id: UUID
    tipo_perfil: TipoPerfilEnum


@dataclass
class DatosPerfilActualizados:
    """Evento que se emite cuando se actualizan los datos del perfil"""
    perfil_id: UUID
    campos_actualizados: List[str]


@dataclass
class FotoPerfilActualizada:
    """Evento que se emite cuando se actualiza la foto del perfil"""
    perfil_id: UUID
    ruta_foto: str


@dataclass
class PreferenciasActualizadas:
    """Evento que se emite cuando se actualizan las preferencias"""
    perfil_id: UUID
    tipos_actualizados: List[str]


@dataclass
class DatosEmpresaActualizados:
    """Evento que se emite cuando se actualizan los datos de una empresa"""
    perfil_id: UUID
    campos_actualizados: List[str]