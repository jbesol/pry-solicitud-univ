"""Entidades persistentes (modelo orientado a objetos mapeado a la BD relacional)."""
from app.models.entities import (
    Categoria,
    Movimiento,
    Notificacion,
    Observacion,
    Parametro,
    Rol,
    Solicitud,
    Usuario,
)

__all__ = [
    "Rol",
    "Usuario",
    "Categoria",
    "Solicitud",
    "Observacion",
    "Movimiento",
    "Notificacion",
    "Parametro",
]
