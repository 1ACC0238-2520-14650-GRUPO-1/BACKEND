from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from jose import jwt, JWTError
import bcrypt

from app.config import settings


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
        """Genera el hash de una contraseña usando bcrypt"""
        # Ensure password is a string
        if not isinstance(password, str):
            password = str(password)
        
        # Ensure password is not already hashed (bcrypt hashes start with $2b$ or $2y$)
        if password.startswith('$2b$') or password.startswith('$2y$') or password.startswith('$2a$'):
            raise ValueError("Password appears to be already hashed")
        
        # Encode to bytes and truncate to 72 bytes (bcrypt limit)
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Hash using bcrypt with rounds=12
        salt = bcrypt.gensalt(rounds=12)
        hash_password = bcrypt.hashpw(password_bytes, salt)
        
        # Return as string
        return hash_password.decode('utf-8')
    
    @staticmethod
    def verificar_password(password: str, hash_password: str) -> bool:
        """Verifica una contraseña contra su hash"""
        if not isinstance(password, str):
            password = str(password)
        
        if not isinstance(hash_password, str):
            hash_password = str(hash_password)
        
        # Encode password to bytes
        password_bytes = password.encode('utf-8')
        
        # Truncate to 72 bytes if needed
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Encode hash_password to bytes if needed
        hash_bytes = hash_password.encode('utf-8') if isinstance(hash_password, str) else hash_password
        
        # Verify
        return bcrypt.checkpw(password_bytes, hash_bytes)
    
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
