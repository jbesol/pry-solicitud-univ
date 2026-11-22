"""Dependencias de FastAPI (inyección de dependencias): sesión de BD, usuario autenticado
y control de acceso por rol (RF01)."""
from collections.abc import Callable

import jwt
from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthError, ForbiddenError
from app.core.security import decode_access_token
from app.domain.enums import RolCodigo
from app.models import Usuario

bearer = HTTPBearer(auto_error=False)


def get_current_user(
    cred: HTTPAuthorizationCredentials | None = Depends(bearer),
    db: Session = Depends(get_db),
) -> Usuario:
    if cred is None:
        raise AuthError("Debe iniciar sesión.")
    try:
        payload = decode_access_token(cred.credentials)
    except jwt.ExpiredSignatureError:
        raise AuthError("La sesión expiró. Inicie sesión nuevamente.")
    except jwt.PyJWTError:
        raise AuthError("Token inválido.")
    usuario = db.get(Usuario, int(payload["sub"]))
    if not usuario or not usuario.activo:
        raise AuthError("Usuario no válido o inactivo.")
    return usuario


def require_roles(*roles: RolCodigo) -> Callable[..., Usuario]:
    """Uso: usuario = Depends(require_roles(RolCodigo.ADMINISTRADOR))"""

    def checker(usuario: Usuario = Depends(get_current_user)) -> Usuario:
        if usuario.rol.codigo not in roles:
            raise ForbiddenError("No tiene permisos para esta operación.")
        return usuario

    return checker


solo_admin = require_roles(RolCodigo.ADMINISTRADOR)
staff = require_roles(RolCodigo.ADMINISTRADOR, RolCodigo.SUPERVISOR)
