from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

# Configuración de hash de contraseñas - usando argon2
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenManager:
    """Gestor de tokens JWT"""
    
    @staticmethod
    def crear_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crea un token de acceso"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def crear_refresh_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Crea un token de refresco"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            # Los refresh tokens duran 7 días
            expire = datetime.utcnow() + timedelta(days=7)
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt
    
    @staticmethod
    def verificar_token(token: str) -> Optional[Dict[str, Any]]:
        """Verifica y decodifica un token"""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def crear_token_verificacion_email(email: str) -> str:
        """Crea un token temporal para verificación de email"""
        data = {
            "email": email,
            "tipo": "email_verification"
        }
        
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(hours=24)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt


class PasswordManager:
    """Gestor de contraseñas"""
    
    @staticmethod
    def hashear_password(password: str) -> str:
        """Genera el hash de una contraseña"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verificar_password(password: str, hash_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        return pwd_context.verify(password, hash_password)
    
    @staticmethod
    def es_password_fuerte(password: str) -> bool:
        """Verifica si una contraseña cumple requisitos mínimos de seguridad"""
        # Mínimo 8 caracteres
        if len(password) < 8:
            return False
        
        # Al menos una mayúscula
        if not any(c.isupper() for c in password):
            return False
        
        # Al menos una minúscula
        if not any(c.islower() for c in password):
            return False
        
        # Al menos un número
        if not any(c.isdigit() for c in password):
            return False
        
        # Al menos un carácter especial
        caracteres_especiales = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in caracteres_especiales for c in password):
            return False
        
        return True
