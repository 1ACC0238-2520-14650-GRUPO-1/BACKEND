from typing import Dict, List, Optional, Any
from pydantic import BaseModel, EmailStr
from datetime import datetime
from enum import Enum
from uuid import UUID


# Enums para schemas
class TipoCuentaEnum(str, Enum):
    CANDIDATO = "candidato"
    EMPRESA = "empresa"
    ADMIN = "admin"


class EstadoPerfilEnum(str, Enum):
    INCOMPLETO = "incompleto"
    COMPLETO = "completo"
    VERIFICADO = "verificado"
    BLOQUEADO = "bloqueado"


# Schemas para Perfil
class PerfilCreate(BaseModel):
    nombre: str
    email: EmailStr
    tipo_cuenta: TipoCuentaEnum
    datos_contacto: Dict[str, Any]


class PerfilResponse(BaseModel):
    perfil_id: str
    nombre: str
    email: Optional[EmailStr] = None
    tipo_cuenta: str
    datos_contacto: Dict[str, Any]
    fecha_registro: datetime
    estado: str
    ultima_actualizacion: datetime


class PerfilUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    datos_contacto: Optional[Dict[str, Any]] = None


# Schemas para PerfilCandidato
class ExperienciaLaboral(BaseModel):
    empresa: str
    puesto: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None


class Educacion(BaseModel):
    institucion: str
    titulo: str
    fecha_inicio: datetime
    fecha_fin: Optional[datetime] = None
    descripcion: Optional[str] = None


class PerfilCandidatoCreate(BaseModel):
    perfil_id: str
    experiencias: Optional[List[ExperienciaLaboral]] = None
    educacion: Optional[List[Educacion]] = None
    habilidades: Optional[List[str]] = None
    cv_url: Optional[str] = None


class PerfilCandidatoResponse(BaseModel):
    perfil_candidato_id: str
    perfil_id: str
    experiencias: List[ExperienciaLaboral]
    educacion: List[Educacion]
    habilidades: List[str]
    cv_url: Optional[str] = None


class PerfilCandidatoUpdate(BaseModel):
    experiencias: Optional[List[ExperienciaLaboral]] = None
    educacion: Optional[List[Educacion]] = None
    habilidades: Optional[List[str]] = None
    cv_url: Optional[str] = None