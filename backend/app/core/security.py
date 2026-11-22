"""Utilidades de seguridad: hash de contraseñas (bcrypt) y tokens JWT."""
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import get_settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int, rol: str) -> str:
    s = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=s.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "rol": rol, "exp": expire}
    return jwt.encode(payload, s.JWT_SECRET_KEY, algorithm=s.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    s = get_settings()
    return jwt.decode(token, s.JWT_SECRET_KEY, algorithms=[s.JWT_ALGORITHM])


def utcnow() -> datetime:
    """Fecha/hora actual en UTC (sin tzinfo, para ser portable entre PostgreSQL y SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
