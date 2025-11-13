from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum


# Enums para schemas
class EstadoPuestoEnum(str, Enum):
    ABIERTO = "abierto"
    CERRADO = "cerrado"


class TipoContratoEnum(str, Enum):
    TIEMPO_COMPLETO = "tiempo_completo"
    MEDIO_TIEMPO = "medio_tiempo"
    TEMPORAL = "temporal"
    FREELANCE = "freelance"
    PRACTICAS = "practicas"


# Schemas para Requisito
class RequisitoCreate(BaseModel):
    tipo: str = Field(..., example="experiencia", description="Tipo de requisito")
    descripcion: str = Field(..., example="3 años de experiencia en desarrollo web", description="Descripción del requisito")
    es_obligatorio: bool = Field(True, description="Indica si el requisito es obligatorio")


class RequisitoResponse(BaseModel):
    tipo: str
    descripcion: str
    es_obligatorio: bool


# Schemas para Puesto
class PuestoCreate(BaseModel):
    empresa_id: str = Field(..., example="550e8400-e29b-41d4-a716-446655440000", description="ID de la empresa que crea el puesto")
    titulo: str = Field(..., example="Desarrollador Full Stack", description="Título del puesto")
    descripcion: str = Field(..., example="Puesto para desarrollador con experiencia en React y Node.js", description="Descripción del puesto")
    ubicacion: str = Field(..., example="Ciudad de México", description="Ubicación del puesto")
    salario_min: Optional[float] = Field(None, example=20000, description="Salario mínimo ofrecido")
    salario_max: Optional[float] = Field(None, example=30000, description="Salario máximo ofrecido")
    moneda: str = Field("MXN", example="MXN", description="Moneda del salario")
    tipo_contrato: TipoContratoEnum = Field(TipoContratoEnum.TIEMPO_COMPLETO, description="Tipo de contrato ofrecido")
    requisitos: List[RequisitoCreate] = Field([], description="Lista de requisitos para el puesto")


class PuestoUpdate(BaseModel):
    titulo: Optional[str] = Field(None, example="Desarrollador Full Stack Senior", description="Título del puesto")
    descripcion: Optional[str] = Field(None, example="Puesto actualizado para desarrollador con experiencia en React y Node.js", description="Descripción del puesto")
    ubicacion: Optional[str] = Field(None, example="Guadalajara", description="Ubicación del puesto")
    salario_min: Optional[float] = Field(None, example=25000, description="Salario mínimo ofrecido")
    salario_max: Optional[float] = Field(None, example=35000, description="Salario máximo ofrecido")
    moneda: Optional[str] = Field(None, example="MXN", description="Moneda del salario")
    tipo_contrato: Optional[TipoContratoEnum] = Field(None, description="Tipo de contrato ofrecido")
    requisitos: Optional[List[RequisitoCreate]] = Field(None, description="Lista actualizada de requisitos para el puesto")


class PuestoResponse(BaseModel):
    puesto_id: str
    empresa_id: str
    titulo: str
    descripcion: str
    ubicacion: str
    salario_min: Optional[float]
    salario_max: Optional[float]
    moneda: str
    tipo_contrato: str
    fecha_publicacion: datetime
    fecha_cierre: Optional[datetime]
    estado: str
    requisitos: List[RequisitoResponse]


class EstadoPuestoUpdate(BaseModel):
    nuevo_estado: EstadoPuestoEnum = Field(..., example="cerrado", description="Nuevo estado del puesto (abierto/cerrado)")

    @validator('nuevo_estado')
    def validate_estado(cls, v):
        if v not in [EstadoPuestoEnum.ABIERTO, EstadoPuestoEnum.CERRADO]:
            raise ValueError('El estado debe ser "abierto" o "cerrado"')
        return v