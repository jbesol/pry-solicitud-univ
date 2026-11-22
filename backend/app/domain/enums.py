"""Enumeraciones del dominio."""
from enum import Enum


class RolCodigo(str, Enum):
    ADMINISTRADOR = "ADMINISTRADOR"
    ESTUDIANTE = "ESTUDIANTE"
    FUNCIONARIO = "FUNCIONARIO"
    SUPERVISOR = "SUPERVISOR"


class EstadoSolicitud(str, Enum):
    REGISTRADA = "REGISTRADA"
    ASIGNADA = "ASIGNADA"
    EN_PROCESO = "EN_PROCESO"
    RESUELTA = "RESUELTA"
    CERRADA = "CERRADA"
    RECHAZADA = "RECHAZADA"
    REABIERTA = "REABIERTA"


# Estados en los que la solicitud ya no requiere atención (no cuentan como vencidas)
ESTADOS_FINALIZADOS = {EstadoSolicitud.RESUELTA, EstadoSolicitud.CERRADA, EstadoSolicitud.RECHAZADA}


class Prioridad(str, Enum):
    BAJA = "BAJA"
    MEDIA = "MEDIA"
    ALTA = "ALTA"
    URGENTE = "URGENTE"


class Canal(str, Enum):
    WEB = "WEB"
    CORREO = "CORREO"
    PRESENCIAL = "PRESENCIAL"
    MENSAJERIA = "MENSAJERIA"


class TipoMovimiento(str, Enum):
    REGISTRO = "REGISTRO"
    ASIGNACION = "ASIGNACION"
    CAMBIO_ESTADO = "CAMBIO_ESTADO"
    OBSERVACION = "OBSERVACION"
    EDICION = "EDICION"


class TipoEvento(str, Enum):
    """Eventos que disparan notificaciones (patrón Observer)."""
    SOLICITUD_REGISTRADA = "SOLICITUD_REGISTRADA"
    SOLICITUD_ASIGNADA = "SOLICITUD_ASIGNADA"
    ESTADO_ACTUALIZADO = "ESTADO_ACTUALIZADO"
    OBSERVACION_AGREGADA = "OBSERVACION_AGREGADA"
