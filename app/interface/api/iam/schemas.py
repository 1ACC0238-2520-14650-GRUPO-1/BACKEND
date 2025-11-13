from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import uuid


# Esquemas de solicitud
class CrearCuentaRequest(BaseModel):
    """Solicitud para crear una nueva cuenta"""
    email: EmailStr
    password: str
    rol: Optional[str] = "postulante"
    perfil_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))


class LoginRequest(BaseModel):
    """Solicitud para login"""
    email: EmailStr
    password: str


class VerificarCuentaRequest(BaseModel):
    """Solicitud para verificar cuenta"""
    cuenta_id: str
    codigo_verificacion: str


class RefreshTokenRequest(BaseModel):
    """Solicitud para refrescar token"""
    refresh_token: str


class CambiarPasswordRequest(BaseModel):
    """Solicitud para cambiar contraseña"""
    password_actual: str
    password_nuevo: str


# Esquemas de respuesta
class TokenResponse(BaseModel):
    """Respuesta con token"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    cuenta_id: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None


class CuentaResponse(BaseModel):
    """Respuesta con datos de cuenta"""
    cuenta_id: str
    perfil_id: str
    email: str
    rol: str
    estado: str
    fecha_creacion: datetime
    fecha_actualizacion: Optional[datetime] = None
    fecha_primer_acceso: Optional[datetime] = None


class VerificacionResponse(BaseModel):
    """Respuesta de verificación"""
    mensaje: str
    cuenta_id: str
    estado: str


class MensajeResponse(BaseModel):
    """Respuesta simple con mensaje"""
    mensaje: str
    exito: bool = True


class TokenVerificationResponse(BaseModel):
    """Respuesta de verificación de token"""
    valido: bool
    sub: Optional[str] = None
    email: Optional[str] = None
    rol: Optional[str] = None
    tipo: Optional[str] = None
