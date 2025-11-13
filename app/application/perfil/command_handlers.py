from dataclasses import dataclass
from typing import Any, Dict, Optional
from uuid import UUID

from app.domain.common import Command, CommandHandler
from app.domain.perfil.entities import (
    Perfil, PerfilAggregate, TipoPerfilEnum
)
from app.domain.perfil.repositories import PerfilRepository


@dataclass
class CrearPerfilPostulanteCommand(Command):
    """Comando para crear un nuevo perfil de postulante"""
    datos_personales: Dict[str, Any]


class CrearPerfilPostulanteHandler(CommandHandler):
    """
    Manejador del comando para crear un perfil de postulante
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: CrearPerfilPostulanteCommand) -> UUID:
        """
        Maneja el comando de creación de perfil de postulante
        """
        # Crear entidad Perfil
        perfil = Perfil(
            tipo_perfil=TipoPerfilEnum.POSTULANTE
        )
        
        # Crear agregado
        perfil_aggregate = PerfilAggregate(perfil=perfil)
        
        # Aplicar creación con los datos proporcionados
        perfil_aggregate.aplicar_creacion_perfil(command.datos_personales)
        
        # Guardar en repositorio
        perfil_id = self.perfil_repository.guardar(perfil_aggregate)
        
        return perfil_id


@dataclass
class ActualizarDatosPostulanteCommand(Command):
    """Comando para actualizar datos de un postulante"""
    perfil_id: UUID
    datos: Dict[str, Any]


class ActualizarDatosPostulanteHandler(CommandHandler):
    """
    Manejador del comando para actualizar datos de un postulante
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: ActualizarDatosPostulanteCommand) -> bool:
        """
        Maneja el comando de actualización de datos
        """
        # Recuperar el perfil
        perfil_aggregate = self.perfil_repository.obtener_por_id(command.perfil_id)
        
        if not perfil_aggregate or perfil_aggregate.perfil.tipo_perfil != TipoPerfilEnum.POSTULANTE:
            raise ValueError(f"No existe un perfil de postulante con ID {command.perfil_id}")
        
        # Aplicar actualización de datos
        perfil_aggregate.aplicar_actualizacion_datos(command.datos)
        
        # Guardar cambios
        self.perfil_repository.guardar(perfil_aggregate)
        
        return True


@dataclass
class ConfigurarPreferenciasPostulanteCommand(Command):
    """Comando para configurar preferencias de un postulante"""
    perfil_id: UUID
    preferencias: Dict[str, str]


class ConfigurarPreferenciasPostulanteHandler(CommandHandler):
    """
    Manejador del comando para configurar preferencias de un postulante
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: ConfigurarPreferenciasPostulanteCommand) -> bool:
        """
        Maneja el comando de configuración de preferencias
        """
        # Recuperar el perfil
        perfil_aggregate = self.perfil_repository.obtener_por_id(command.perfil_id)
        
        if not perfil_aggregate or perfil_aggregate.perfil.tipo_perfil != TipoPerfilEnum.POSTULANTE:
            raise ValueError(f"No existe un perfil de postulante con ID {command.perfil_id}")
        
        # Aplicar configuración de preferencias
        perfil_aggregate.aplicar_configuracion_preferencias(command.preferencias)
        
        # Guardar cambios
        self.perfil_repository.guardar(perfil_aggregate)
        
        return True


@dataclass
class ActualizarFotoPostulanteCommand(Command):
    """Comando para actualizar la foto de un postulante"""
    perfil_id: UUID
    ruta_foto: str


class ActualizarFotoPostulanteHandler(CommandHandler):
    """
    Manejador del comando para actualizar la foto de un postulante
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: ActualizarFotoPostulanteCommand) -> bool:
        """
        Maneja el comando de actualización de foto
        """
        # Recuperar el perfil
        perfil_aggregate = self.perfil_repository.obtener_por_id(command.perfil_id)
        
        if not perfil_aggregate or perfil_aggregate.perfil.tipo_perfil != TipoPerfilEnum.POSTULANTE:
            raise ValueError(f"No existe un perfil de postulante con ID {command.perfil_id}")
        
        # Aplicar cambio de foto
        perfil_aggregate.aplicar_cambio_foto(command.ruta_foto)
        
        # Guardar cambios
        self.perfil_repository.guardar(perfil_aggregate)
        
        return True


@dataclass
class CrearPerfilEmpresaCommand(Command):
    """Comando para crear un nuevo perfil de empresa"""
    datos_empresa: Dict[str, Any]


class CrearPerfilEmpresaHandler(CommandHandler):
    """
    Manejador del comando para crear un perfil de empresa
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: CrearPerfilEmpresaCommand) -> UUID:
        """
        Maneja el comando de creación de perfil de empresa
        """
        # Crear entidad Perfil
        perfil = Perfil(
            tipo_perfil=TipoPerfilEnum.EMPRESA
        )
        
        # Crear agregado
        perfil_aggregate = PerfilAggregate(perfil=perfil)
        
        # Aplicar creación con los datos proporcionados
        perfil_aggregate.aplicar_creacion_perfil(command.datos_empresa)
        
        # Guardar en repositorio
        perfil_id = self.perfil_repository.guardar(perfil_aggregate)
        
        return perfil_id


@dataclass
class ActualizarDatosEmpresaCommand(Command):
    """Comando para actualizar datos de una empresa"""
    perfil_id: UUID
    datos: Dict[str, Any]


class ActualizarDatosEmpresaHandler(CommandHandler):
    """
    Manejador del comando para actualizar datos de una empresa
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: ActualizarDatosEmpresaCommand) -> bool:
        """
        Maneja el comando de actualización de datos de empresa
        """
        # Recuperar el perfil
        perfil_aggregate = self.perfil_repository.obtener_por_id(command.perfil_id)
        
        if not perfil_aggregate or perfil_aggregate.perfil.tipo_perfil != TipoPerfilEnum.EMPRESA:
            raise ValueError(f"No existe un perfil de empresa con ID {command.perfil_id}")
        
        # Aplicar actualización de datos específica para empresa
        perfil_aggregate.aplicar_actualizacion_empresa(command.datos)
        
        # Guardar cambios
        self.perfil_repository.guardar(perfil_aggregate)
        
        return True


@dataclass
class ActualizarLogoEmpresaCommand(Command):
    """Comando para actualizar el logo de una empresa"""
    perfil_id: UUID
    ruta_logo: str


class ActualizarLogoEmpresaHandler(CommandHandler):
    """
    Manejador del comando para actualizar el logo de una empresa
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: ActualizarLogoEmpresaCommand) -> bool:
        """
        Maneja el comando de actualización de logo
        """
        # Recuperar el perfil
        perfil_aggregate = self.perfil_repository.obtener_por_id(command.perfil_id)
        
        if not perfil_aggregate or perfil_aggregate.perfil.tipo_perfil != TipoPerfilEnum.EMPRESA:
            raise ValueError(f"No existe un perfil de empresa con ID {command.perfil_id}")
        
        # Aplicar cambio de logo (usando el mismo método que para foto)
        perfil_aggregate.aplicar_cambio_foto(command.ruta_logo)
        
        # Guardar cambios
        self.perfil_repository.guardar(perfil_aggregate)
        
        return True


@dataclass
class AgregarDocumentoCommand(Command):
    """
    Comando para agregar un documento al perfil del postulante
    US18: Subir documentos al perfil
    """
    perfil_id: UUID
    documento: dict  # Contiene nombre, tipo, url, etc.


class AgregarDocumentoHandler(CommandHandler):
    """
    Manejador para agregar un documento al perfil
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: AgregarDocumentoCommand) -> bool:
        """
        Maneja el comando de agregar documento
        """
        return self.perfil_repository.agregar_documento(command.perfil_id, command.documento)


@dataclass
class EliminarDocumentoCommand(Command):
    """
    Comando para eliminar un documento del perfil
    US19: Eliminar documento del perfil
    """
    perfil_id: UUID
    documento_id: str


class EliminarDocumentoHandler(CommandHandler):
    """
    Manejador para eliminar un documento del perfil
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: EliminarDocumentoCommand) -> bool:
        """
        Maneja el comando de eliminar documento
        """
        return self.perfil_repository.eliminar_documento(command.perfil_id, command.documento_id)


@dataclass
class CompletarPerfilBasicoCommand(Command):
    """
    Comando para completar el perfil básico del postulante
    US12: Completar perfil básico del postulante
    """
    perfil_id: UUID
    datos_basicos: dict


class CompletarPerfilBasicoHandler(CommandHandler):
    """
    Manejador para completar el perfil básico del postulante
    """
    
    def __init__(self, perfil_repository: PerfilRepository):
        self.perfil_repository = perfil_repository
    
    def handle(self, command: CompletarPerfilBasicoCommand) -> bool:
        """
        Maneja el comando de completar perfil básico
        """
        return self.perfil_repository.completar_perfil_basico(command.perfil_id, command.datos_basicos)