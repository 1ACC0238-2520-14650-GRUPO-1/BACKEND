from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from uuid import UUID

from app.application.iam.command_handlers import (
    CrearCuentaHandler, CrearCuentaCommand,
    LoginHandler, LoginCommand,
    GenerarTokenHandler, GenerarTokenCommand,
    VerificarCuentaHandler, VerificarCuentaCommand,
    CambiarPasswordHandler, CambiarPasswordCommand
)
from app.application.iam.query_handlers import (
    ObtenerCuentaQueryHandler, ObtenerCuentaQuery,
    ObtenerCuentaPorEmailQueryHandler, ObtenerCuentaPorEmailQuery,
    VerificarTokenQueryHandler, VerificarTokenQuery
)
from app.infrastructure.iam.repositories import CuentaRepositoryImpl
from app.infrastructure.iam.security import TokenManager

from .schemas import (
    CrearCuentaRequest, LoginRequest, VerificarCuentaRequest,
    RefreshTokenRequest, CambiarPasswordRequest,
    TokenResponse, CuentaResponse, VerificacionResponse,
    MensajeResponse, TokenVerificationResponse
)

router = APIRouter(prefix="/iam", tags=["IAM"])


@router.post("/registrar", response_model=CuentaResponse, status_code=status.HTTP_201_CREATED)
async def registrar_cuenta(request: CrearCuentaRequest):
    """
    Registra una nueva cuenta de usuario.
    - **email**: Email único del usuario
    - **password**: Contraseña (mín. 8 caracteres, mayúscula, minúscula, número, carácter especial)
    - **tipo_cuenta**: Tipo de cuenta (candidato, empresa, admin) - por defecto 'candidato'
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = CrearCuentaHandler(repository)
        
        command = CrearCuentaCommand(
            nombre_completo=request.nombre_completo,
            email=request.email,
            password=request.password,
            carrera=request.carrera,
            telefono=request.telefono,
            ciudad=request.ciudad,
            rol=request.rol
        )
        
        cuenta_id = handler.handle(command)
        
        # Obtener la cuenta creada para devolver los datos completos
        query_handler = ObtenerCuentaQueryHandler(repository)
        cuenta_data = query_handler.handle(ObtenerCuentaQuery(cuenta_id=UUID(cuenta_id['cuenta_id'])))
        
        return CuentaResponse(
            cuenta_id=cuenta_data['cuenta_id'],
            nombre_completo=cuenta_data['nombre_completo'],
            email=cuenta_data['email'],
            carrera=cuenta_data['carrera'],
            telefono=cuenta_data['telefono'],
            ciudad=cuenta_data['ciudad'],
            rol=cuenta_data['rol'],
            estado=cuenta_data['estado'],
            fecha_creacion=cuenta_data['fecha_creacion'],
            fecha_actualizacion=cuenta_data['fecha_actualizacion'],
            fecha_primer_acceso=cuenta_data['fecha_primer_acceso']
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al registrar cuenta: {str(e)}"
        )


@router.post("/login", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def login(request: LoginRequest):
    """
    Realiza login del usuario y devuelve tokens JWT.
    
    - **email**: Email del usuario
    - **password**: Contraseña del usuario
    
    Retorna access_token y refresh_token para futuras autenticaciones.
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = LoginHandler(repository)
        
        command = LoginCommand(
            email=request.email,
            password=request.password
        )
        
        resultado = handler.handle(command)
        
        return TokenResponse(
            access_token=resultado['access_token'],
            refresh_token=resultado['refresh_token'],
            token_type=resultado['token_type'],
            cuenta_id=resultado['cuenta_id'],
            email=resultado['email'],
            rol=resultado['rol']
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error en login: {str(e)}"
        )


@router.post("/verificar-cuenta", response_model=VerificacionResponse, status_code=status.HTTP_200_OK)
async def verificar_cuenta(request: VerificarCuentaRequest):
    """
    Verifica una cuenta usando el código de verificación enviado al email.
    
    - **cuenta_id**: ID de la cuenta a verificar
    - **codigo_verificacion**: Código enviado al email del usuario
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = VerificarCuentaHandler(repository)
        
        command = VerificarCuentaCommand(
            cuenta_id=UUID(request.cuenta_id),
            codigo_verificacion=request.codigo_verificacion
        )
        
        handler.handle(command)
        
        # Obtener cuenta actualizada
        query_handler = ObtenerCuentaQueryHandler(repository)
        query = ObtenerCuentaQuery(cuenta_id=UUID(request.cuenta_id))
        cuenta_data = query_handler.handle(query)
        
        return VerificacionResponse(
            mensaje="Cuenta verificada exitosamente",
            cuenta_id=cuenta_data['cuenta_id'],
            estado=cuenta_data['estado']
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al verificar cuenta: {str(e)}"
        )


@router.post("/refresh-token", response_model=TokenResponse, status_code=status.HTTP_200_OK)
async def refresh_token(request: RefreshTokenRequest):
    """
    Obtiene un nuevo access_token usando el refresh_token.
    
    - **refresh_token**: Token de refresco obtenido en el login
    """
    try:
        # Verificar el refresh token
        payload = TokenManager.verificar_token(request.refresh_token)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de refresco inválido o expirado"
            )
        
        if payload.get("tipo") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tipo de token incorrecto"
            )
        
        # Obtener la cuenta
        repository = CuentaRepositoryImpl()
        query_handler = ObtenerCuentaQueryHandler(repository)
        query = ObtenerCuentaQuery(cuenta_id=UUID(payload.get("sub")))
        cuenta_data = query_handler.handle(query)
        
        if not cuenta_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cuenta no encontrada"
            )
        
        # Generar nuevo access token
        nuevo_access_token = TokenManager.crear_access_token({
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "rol": cuenta_data.get("rol"),
            "tipo": "access"
        })
        
        return TokenResponse(
            access_token=nuevo_access_token,
            token_type="bearer",
            cuenta_id=payload.get("sub"),
            email=payload.get("email"),
            rol=cuenta_data.get("rol")
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al refrescar token: {str(e)}"
        )


@router.post("/cambiar-password", response_model=MensajeResponse, status_code=status.HTTP_200_OK)
async def cambiar_password(
    request: CambiarPasswordRequest,
    cuenta_id: str
):
    """
    Cambia la contraseña del usuario autenticado.
    
    - **password_actual**: Contraseña actual
    - **password_nuevo**: Nueva contraseña
    - **cuenta_id**: ID de la cuenta (desde header o parámetro)
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = CambiarPasswordHandler(repository)
        
        command = CambiarPasswordCommand(
            cuenta_id=UUID(cuenta_id),
            password_actual=request.password_actual,
            password_nuevo=request.password_nuevo
        )
        
        handler.handle(command)
        
        return MensajeResponse(
            mensaje="Contraseña actualizada exitosamente",
            exito=True
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al cambiar contraseña: {str(e)}"
        )


@router.get("/cuenta/{cuenta_id}", response_model=CuentaResponse, status_code=status.HTTP_200_OK)
async def obtener_cuenta(cuenta_id: str):
    """
    Obtiene la información de una cuenta.
    
    - **cuenta_id**: ID de la cuenta
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = ObtenerCuentaQueryHandler(repository)
        
        query = ObtenerCuentaQuery(cuenta_id=UUID(cuenta_id))
        cuenta_data = handler.handle(query)
        
        if not cuenta_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuenta no encontrada: {cuenta_id}"
            )
        
        return CuentaResponse(**cuenta_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener cuenta: {str(e)}"
        )


@router.get("/cuenta/email/{email}", response_model=CuentaResponse, status_code=status.HTTP_200_OK)
async def obtener_cuenta_por_email(email: str):
    """
    Obtiene la información de una cuenta por email.
    
    - **email**: Email del usuario
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = ObtenerCuentaPorEmailQueryHandler(repository)
        
        query = ObtenerCuentaPorEmailQuery(email=email)
        cuenta_data = handler.handle(query)
        
        if not cuenta_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cuenta no encontrada para el email: {email}"
            )
        
        return CuentaResponse(**cuenta_data)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al obtener cuenta: {str(e)}"
        )





@router.post("/verificar-token", response_model=TokenVerificationResponse, status_code=status.HTTP_200_OK)
async def verificar_token_endpoint(request: RefreshTokenRequest):
    """
    Verifica si un token JWT es válido.
    
    - **refresh_token**: Token a verificar (puede ser access_token o refresh_token)
    """
    try:
        repository = CuentaRepositoryImpl()
        handler = VerificarTokenQueryHandler(repository)
        
        query = VerificarTokenQuery(token=request.refresh_token)
        resultado = handler.handle(query)
        
        if not resultado:
            return TokenVerificationResponse(valido=False)
        
        return TokenVerificationResponse(**resultado)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error al verificar token: {str(e)}"
        )
