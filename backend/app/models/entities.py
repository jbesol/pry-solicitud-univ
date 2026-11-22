"""Clases principales del modelo de dominio.

Rol 1──* Usuario 1──* Solicitud *──1 Categoria
Solicitud 1──* Observacion, 1──* Movimiento (historial)
Usuario 1──* Notificacion
"""
from datetime import datetime

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.security import utcnow
from app.domain.enums import (
    ESTADOS_FINALIZADOS,
    Canal,
    EstadoSolicitud,
    Prioridad,
    RolCodigo,
    TipoEvento,
    TipoMovimiento,
)


def _enum(e, name):
    return SAEnum(e, name=f"ck_{name}", native_enum=False, length=20, validate_strings=True, create_constraint=True)


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[RolCodigo] = mapped_column(_enum(RolCodigo, "rol_codigo"), unique=True)
    nombre: Mapped[str] = mapped_column(String(50))
    descripcion: Mapped[str | None] = mapped_column(String(255))

    usuarios: Mapped[list["Usuario"]] = relationship(back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    documento: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    nombres: Mapped[str] = mapped_column(String(80))
    apellidos: Mapped[str] = mapped_column(String(80))
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    telefono: Mapped[str | None] = mapped_column(String(20))
    dependencia: Mapped[str | None] = mapped_column(String(100))  # programa académico u oficina
    rol_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    fecha_creacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    rol: Mapped[Rol] = relationship(back_populates="usuarios", lazy="joined")

    @property
    def nombre_completo(self) -> str:
        return f"{self.nombres} {self.apellidos}"

    def tiene_rol(self, *roles: RolCodigo) -> bool:
        return self.rol.codigo in roles


class Categoria(Base):
    __tablename__ = "categorias"
    __table_args__ = (CheckConstraint("tiempo_respuesta_horas > 0", name="ck_categoria_tiempo"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(80), unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255))
    dependencia: Mapped[str | None] = mapped_column(String(100))  # área responsable
    tiempo_respuesta_horas: Mapped[int] = mapped_column(Integer, default=72)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)

    solicitudes: Mapped[list["Solicitud"]] = relationship(back_populates="categoria")


class Solicitud(Base):
    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str | None] = mapped_column(String(30), unique=True, index=True)
    asunto: Mapped[str] = mapped_column(String(150))
    descripcion: Mapped[str] = mapped_column(Text)
    prioridad: Mapped[Prioridad] = mapped_column(_enum(Prioridad, "prioridad"), default=Prioridad.MEDIA)
    canal: Mapped[Canal] = mapped_column(_enum(Canal, "canal"), default=Canal.WEB)
    estado: Mapped[EstadoSolicitud] = mapped_column(
        _enum(EstadoSolicitud, "estado_solicitud"), default=EstadoSolicitud.REGISTRADA, index=True
    )
    solucion: Mapped[str | None] = mapped_column(Text)

    solicitante_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), index=True)
    categoria_id: Mapped[int] = mapped_column(ForeignKey("categorias.id"), index=True)
    responsable_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"), index=True)

    fecha_registro: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=utcnow, onupdate=utcnow)
    fecha_limite: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_resolucion: Mapped[datetime | None] = mapped_column(DateTime)
    fecha_cierre: Mapped[datetime | None] = mapped_column(DateTime)

    solicitante: Mapped[Usuario] = relationship(foreign_keys=[solicitante_id], lazy="joined")
    responsable: Mapped[Usuario | None] = relationship(foreign_keys=[responsable_id], lazy="joined")
    categoria: Mapped[Categoria] = relationship(back_populates="solicitudes", lazy="joined")
    observaciones: Mapped[list["Observacion"]] = relationship(
        back_populates="solicitud", order_by="Observacion.fecha", cascade="all, delete-orphan"
    )
    movimientos: Mapped[list["Movimiento"]] = relationship(
        back_populates="solicitud", order_by="Movimiento.fecha", cascade="all, delete-orphan"
    )

    @property
    def vencida(self) -> bool:
        return (
            self.fecha_limite is not None
            and self.estado not in ESTADOS_FINALIZADOS
            and utcnow() > self.fecha_limite
        )

    def es_de(self, usuario: Usuario) -> bool:
        return self.solicitante_id == usuario.id

    def esta_asignada_a(self, usuario: Usuario) -> bool:
        return self.responsable_id == usuario.id


class Observacion(Base):
    __tablename__ = "observaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id", ondelete="CASCADE"), index=True)
    autor_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    texto: Mapped[str] = mapped_column(Text)
    interna: Mapped[bool] = mapped_column(Boolean, default=False)  # visible solo para el personal
    fecha: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    solicitud: Mapped[Solicitud] = relationship(back_populates="observaciones")
    autor: Mapped[Usuario] = relationship(lazy="joined")


class Movimiento(Base):
    """Historial: cada registro, asignación, cambio de estado u observación de una solicitud."""
    __tablename__ = "movimientos"

    id: Mapped[int] = mapped_column(primary_key=True)
    solicitud_id: Mapped[int] = mapped_column(ForeignKey("solicitudes.id", ondelete="CASCADE"), index=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id"))
    tipo: Mapped[TipoMovimiento] = mapped_column(_enum(TipoMovimiento, "tipo_movimiento"))
    estado_anterior: Mapped[EstadoSolicitud | None] = mapped_column(_enum(EstadoSolicitud, "estado_ant"))
    estado_nuevo: Mapped[EstadoSolicitud | None] = mapped_column(_enum(EstadoSolicitud, "estado_nue"))
    responsable_anterior_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    responsable_nuevo_id: Mapped[int | None] = mapped_column(ForeignKey("usuarios.id"))
    detalle: Mapped[str | None] = mapped_column(Text)  # motivo / observación del cambio
    interno: Mapped[bool] = mapped_column(Boolean, default=False)  # no visible para el estudiante
    fecha: Mapped[datetime] = mapped_column(DateTime, default=utcnow, index=True)

    solicitud: Mapped[Solicitud] = relationship(back_populates="movimientos")
    usuario: Mapped[Usuario] = relationship(foreign_keys=[usuario_id], lazy="joined")
    responsable_anterior: Mapped[Usuario | None] = relationship(foreign_keys=[responsable_anterior_id], lazy="joined")
    responsable_nuevo: Mapped[Usuario | None] = relationship(foreign_keys=[responsable_nuevo_id], lazy="joined")


class Notificacion(Base):
    __tablename__ = "notificaciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    solicitud_id: Mapped[int | None] = mapped_column(ForeignKey("solicitudes.id", ondelete="CASCADE"))
    tipo: Mapped[TipoEvento] = mapped_column(_enum(TipoEvento, "tipo_evento"))
    titulo: Mapped[str] = mapped_column(String(150))
    mensaje: Mapped[str] = mapped_column(Text)
    leida: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    fecha: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


class Parametro(Base):
    """Parámetros configurables del sistema administrados por el Administrador."""
    __tablename__ = "parametros"

    clave: Mapped[str] = mapped_column(String(50), primary_key=True)
    valor: Mapped[str] = mapped_column(String(255))
    descripcion: Mapped[str | None] = mapped_column(String(255))
