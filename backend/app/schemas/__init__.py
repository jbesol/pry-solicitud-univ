"""DTOs (Pydantic): validan los datos de entrada y dan forma a las respuestas de la API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_serializer

from app.domain.enums import Canal, EstadoSolicitud, Prioridad, RolCodigo, TipoEvento, TipoMovimiento


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("*", when_used="json", check_fields=False)
    def _fechas_utc(self, v):
        # Las fechas se guardan en UTC; se marcan con "Z" para que el navegador las convierta a hora local.
        if isinstance(v, datetime) and v.tzinfo is None:
            return v.isoformat() + "Z"
        return v


# ---------------------------------------------------------------- Auth
class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)


class CambioPasswordIn(BaseModel):
    actual: str
    nueva: str = Field(min_length=8, max_length=72)


# ---------------------------------------------------------------- Roles / usuarios
class RolOut(ORM):
    id: int
    codigo: RolCodigo
    nombre: str
    descripcion: str | None = None


class UsuarioResumen(ORM):
    id: int
    nombres: str
    apellidos: str
    email: str
    nombre_completo: str


class UsuarioOut(ORM):
    id: int
    documento: str
    nombres: str
    apellidos: str
    nombre_completo: str
    email: str
    telefono: str | None = None
    dependencia: str | None = None
    activo: bool
    fecha_creacion: datetime
    rol: RolOut


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioOut


class UsuarioCreate(BaseModel):
    documento: str = Field(min_length=5, max_length=20, pattern=r"^[0-9A-Za-z-]+$")
    nombres: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    telefono: str | None = Field(default=None, max_length=20)
    dependencia: str | None = Field(default=None, max_length=100)
    rol: RolCodigo


class UsuarioUpdate(BaseModel):
    nombres: str | None = Field(default=None, min_length=2, max_length=80)
    apellidos: str | None = Field(default=None, min_length=2, max_length=80)
    email: EmailStr | None = None
    telefono: str | None = Field(default=None, max_length=20)
    dependencia: str | None = Field(default=None, max_length=100)
    password: str | None = Field(default=None, min_length=8, max_length=72)


class RolUpdate(BaseModel):
    rol: RolCodigo


class ActivoUpdate(BaseModel):
    activo: bool


# ---------------------------------------------------------------- Categorías / parámetros
class CategoriaIn(BaseModel):
    nombre: str = Field(min_length=3, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)
    dependencia: str | None = Field(default=None, max_length=100)
    tiempo_respuesta_horas: int = Field(default=72, gt=0, le=2160)


class CategoriaOut(ORM):
    id: int
    nombre: str
    descripcion: str | None = None
    dependencia: str | None = None
    tiempo_respuesta_horas: int
    activa: bool


class ParametroOut(ORM):
    clave: str
    valor: str
    descripcion: str | None = None


class ParametroIn(BaseModel):
    valor: str = Field(min_length=1, max_length=255)


# ---------------------------------------------------------------- Solicitudes
class SolicitudCreate(BaseModel):
    asunto: str = Field(min_length=5, max_length=150)
    descripcion: str = Field(min_length=10, max_length=5000)
    categoria_id: int
    prioridad: Prioridad = Prioridad.MEDIA
    canal: Canal = Canal.WEB


class SolicitudUpdate(BaseModel):
    asunto: str | None = Field(default=None, min_length=5, max_length=150)
    descripcion: str | None = Field(default=None, min_length=10, max_length=5000)
    categoria_id: int | None = None
    prioridad: Prioridad | None = None


class AsignacionIn(BaseModel):
    responsable_id: int
    comentario: str | None = Field(default=None, max_length=1000)


class CambioEstadoIn(BaseModel):
    estado: EstadoSolicitud
    comentario: str | None = Field(default=None, max_length=2000)  # motivo u observación
    solucion: str | None = Field(default=None, max_length=5000)


class ObservacionIn(BaseModel):
    texto: str = Field(min_length=2, max_length=2000)
    interna: bool = False


class ObservacionOut(ORM):
    id: int
    texto: str
    interna: bool
    fecha: datetime
    autor: UsuarioResumen


class MovimientoOut(ORM):
    id: int
    tipo: TipoMovimiento
    estado_anterior: EstadoSolicitud | None = None
    estado_nuevo: EstadoSolicitud | None = None
    detalle: str | None = None
    fecha: datetime
    usuario: UsuarioResumen
    responsable_anterior: UsuarioResumen | None = None
    responsable_nuevo: UsuarioResumen | None = None


class CategoriaMini(ORM):
    id: int
    nombre: str


class SolicitudOut(ORM):
    id: int
    codigo: str | None
    asunto: str
    descripcion: str
    prioridad: Prioridad
    canal: Canal
    estado: EstadoSolicitud
    solucion: str | None = None
    fecha_registro: datetime
    fecha_actualizacion: datetime
    fecha_limite: datetime | None = None
    fecha_resolucion: datetime | None = None
    fecha_cierre: datetime | None = None
    vencida: bool
    categoria: CategoriaMini
    solicitante: UsuarioResumen
    responsable: UsuarioResumen | None = None


class TransicionOut(BaseModel):
    estado: EstadoSolicitud
    etiqueta: str
    requiere_motivo: bool
    requiere_solucion: bool


class PermisosOut(BaseModel):
    puede_editar: bool
    puede_asignar: bool
    puede_observar: bool
    transiciones: list[TransicionOut]


class SolicitudDetalle(SolicitudOut):
    observaciones: list[ObservacionOut]
    movimientos: list[MovimientoOut]
    permisos: PermisosOut


# ---------------------------------------------------------------- Notificaciones
class NotificacionOut(ORM):
    id: int
    solicitud_id: int | None
    tipo: TipoEvento
    titulo: str
    mensaje: str
    leida: bool
    fecha: datetime


# ---------------------------------------------------------------- Reportes
class ConteoItem(BaseModel):
    clave: str
    etiqueta: str
    total: int


class ReporteResumen(BaseModel):
    total: int
    abiertas: int
    finalizadas: int
    vencidas: int
    cumplimiento_sla: float | None  # % resueltas dentro del tiempo límite
    tiempo_promedio_resolucion_horas: float | None
    por_estado: list[ConteoItem]
    por_categoria: list[ConteoItem]
    por_prioridad: list[ConteoItem]
    por_responsable: list[ConteoItem]
    por_mes: list[ConteoItem]
