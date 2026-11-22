"""Acceso a datos — Patrón de diseño REPOSITORY.

Los servicios no escriben SQL: piden datos a repositorios. Así la lógica de negocio
queda aislada de la tecnología de persistencia y puede probarse con otra BD (SQLite).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Generic, TypeVar

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.domain.enums import EstadoSolicitud, Prioridad, RolCodigo
from app.models import Categoria, Notificacion, Parametro, Rol, Solicitud, Usuario

T = TypeVar("T")


class BaseRepository(Generic[T]):
    model: type[T]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id_) -> T | None:
        return self.db.get(self.model, id_)

    def add(self, obj: T) -> T:
        self.db.add(obj)
        self.db.flush()
        return obj

    def list_all(self) -> list[T]:
        return list(self.db.scalars(select(self.model)))


class RolRepository(BaseRepository[Rol]):
    model = Rol

    def por_codigo(self, codigo: RolCodigo) -> Rol | None:
        return self.db.scalar(select(Rol).where(Rol.codigo == codigo))


class UsuarioRepository(BaseRepository[Usuario]):
    model = Usuario

    def por_email(self, email: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(func.lower(Usuario.email) == email.lower()))

    def por_documento(self, documento: str) -> Usuario | None:
        return self.db.scalar(select(Usuario).where(Usuario.documento == documento))

    def buscar(self, q: str | None = None, rol: RolCodigo | None = None, activo: bool | None = None) -> list[Usuario]:
        stmt = select(Usuario).join(Usuario.rol).order_by(Usuario.apellidos, Usuario.nombres)
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Usuario.nombres).like(like),
                    func.lower(Usuario.apellidos).like(like),
                    func.lower(Usuario.email).like(like),
                    Usuario.documento.like(like),
                )
            )
        if rol:
            stmt = stmt.where(Rol.codigo == rol)
        if activo is not None:
            stmt = stmt.where(Usuario.activo == activo)
        return list(self.db.scalars(stmt).unique())

    def con_roles(self, *roles: RolCodigo) -> list[Usuario]:
        stmt = select(Usuario).join(Usuario.rol).where(Rol.codigo.in_(roles), Usuario.activo.is_(True))
        return list(self.db.scalars(stmt).unique())


class CategoriaRepository(BaseRepository[Categoria]):
    model = Categoria

    def por_nombre(self, nombre: str) -> Categoria | None:
        return self.db.scalar(select(Categoria).where(func.lower(Categoria.nombre) == nombre.lower()))

    def listar(self, solo_activas: bool = False) -> list[Categoria]:
        stmt = select(Categoria).order_by(Categoria.nombre)
        if solo_activas:
            stmt = stmt.where(Categoria.activa.is_(True))
        return list(self.db.scalars(stmt))


@dataclass
class FiltroSolicitudes:
    estado: EstadoSolicitud | None = None
    categoria_id: int | None = None
    prioridad: Prioridad | None = None
    responsable_id: int | None = None
    solicitante_id: int | None = None
    desde: datetime | None = None
    hasta: datetime | None = None
    q: str | None = None


class SolicitudRepository(BaseRepository[Solicitud]):
    model = Solicitud

    def _aplicar(self, stmt, f: FiltroSolicitudes):
        if f.estado:
            stmt = stmt.where(Solicitud.estado == f.estado)
        if f.categoria_id:
            stmt = stmt.where(Solicitud.categoria_id == f.categoria_id)
        if f.prioridad:
            stmt = stmt.where(Solicitud.prioridad == f.prioridad)
        if f.responsable_id:
            stmt = stmt.where(Solicitud.responsable_id == f.responsable_id)
        if f.solicitante_id:
            stmt = stmt.where(Solicitud.solicitante_id == f.solicitante_id)
        if f.desde:
            stmt = stmt.where(Solicitud.fecha_registro >= f.desde)
        if f.hasta:
            stmt = stmt.where(Solicitud.fecha_registro <= f.hasta)
        if f.q:
            like = f"%{f.q.lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Solicitud.asunto).like(like),
                    func.lower(Solicitud.codigo).like(like),
                    func.lower(Solicitud.descripcion).like(like),
                )
            )
        return stmt

    def buscar(self, f: FiltroSolicitudes, limite: int | None = None) -> list[Solicitud]:
        stmt = self._aplicar(select(Solicitud), f).order_by(Solicitud.fecha_registro.desc())
        if limite:
            stmt = stmt.limit(limite)
        return list(self.db.scalars(stmt).unique())

    def conteo_por(self, columna, f: FiltroSolicitudes) -> list[tuple]:
        stmt = self._aplicar(select(columna, func.count(Solicitud.id)), f).group_by(columna)
        return list(self.db.execute(stmt).all())


class NotificacionRepository(BaseRepository[Notificacion]):
    model = Notificacion

    def de_usuario(self, usuario_id: int, solo_no_leidas: bool = False, limite: int = 50) -> list[Notificacion]:
        stmt = select(Notificacion).where(Notificacion.usuario_id == usuario_id)
        if solo_no_leidas:
            stmt = stmt.where(Notificacion.leida.is_(False))
        stmt = stmt.order_by(Notificacion.fecha.desc(), Notificacion.id.desc()).limit(limite)
        return list(self.db.scalars(stmt))

    def no_leidas(self, usuario_id: int) -> int:
        return self.db.scalar(
            select(func.count(Notificacion.id)).where(
                Notificacion.usuario_id == usuario_id, Notificacion.leida.is_(False)
            )
        ) or 0


class ParametroRepository(BaseRepository[Parametro]):
    model = Parametro

    def valor(self, clave: str, defecto: str = "") -> str:
        p = self.get(clave)
        return p.valor if p else defecto
