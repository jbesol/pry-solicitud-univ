"""Ciclo de vida de una solicitud — Patrón de diseño STATE.

Cada estado es una clase que conoce:
  * a qué estados puede pasar y quién puede ejecutar cada transición,
  * qué datos exige la transición (motivo o solución),
  * qué operaciones permite mientras la solicitud está en él (editar, observar, asignar),
  * qué efectos tiene entrar en él (fechas de resolución/cierre).

El servicio de solicitudes (contexto) no contiene condicionales sobre estados: delega en
el objeto estado actual. Agregar un estado nuevo = agregar una clase y registrarla.

Diagrama:
    REGISTRADA → ASIGNADA → EN_PROCESO → RESUELTA → CERRADA
         │           │                       │          │
         └→ RECHAZADA ←┘                     └→ REABIERTA ←┘ (reapertura autorizada)
    RECHAZADA → REABIERTA ;  REABIERTA → ASIGNADA | EN_PROCESO
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from app.core.exceptions import BusinessRuleError, ForbiddenError
from app.core.security import utcnow
from app.domain.enums import EstadoSolicitud as E
from app.domain.enums import RolCodigo as R

if TYPE_CHECKING:
    from app.models import Solicitud, Usuario

STAFF_ASIGNADOR = frozenset({R.ADMINISTRADOR, R.SUPERVISOR})


@dataclass(frozen=True)
class ReglaTransicion:
    """Quién puede ejecutar una transición y qué datos exige."""
    roles: frozenset[R] = field(default_factory=frozenset)  # roles que siempre pueden
    responsable: bool = False   # el funcionario asignado puede
    solicitante: bool = False   # el estudiante dueño puede
    requiere_motivo: bool = False
    requiere_solucion: bool = False
    solo_por_asignacion: bool = False  # se ejecuta únicamente mediante "asignar responsable"
    etiqueta: str = ""

    def autoriza(self, usuario: "Usuario", solicitud: "Solicitud") -> bool:
        if usuario.rol.codigo in self.roles:
            return True
        if self.responsable and usuario.rol.codigo == R.FUNCIONARIO and solicitud.esta_asignada_a(usuario):
            return True
        if self.solicitante and solicitud.es_de(usuario):
            return True
        return False


class EstadoBase:
    codigo: E
    nombre: str
    transiciones: dict[E, ReglaTransicion] = {}
    permite_edicion: bool = False        # el solicitante puede editar descripción/categoría
    permite_observaciones: bool = True
    permite_asignacion: bool = False     # se puede asignar / reasignar responsable

    # --- consultas -----------------------------------------------------------------
    def transiciones_disponibles(self, usuario: "Usuario", solicitud: "Solicitud") -> list[dict]:
        return [
            {
                "estado": destino.value,
                "etiqueta": regla.etiqueta or estado_de(destino).nombre,
                "requiere_motivo": regla.requiere_motivo,
                "requiere_solucion": regla.requiere_solucion,
            }
            for destino, regla in self.transiciones.items()
            if not regla.solo_por_asignacion and regla.autoriza(usuario, solicitud)
        ]

    # --- validación ----------------------------------------------------------------
    def validar_transicion(
        self,
        usuario: "Usuario",
        solicitud: "Solicitud",
        destino: E,
        motivo: str | None,
        solucion: str | None,
        por_asignacion: bool = False,
    ) -> ReglaTransicion:
        regla = self.transiciones.get(destino)
        if regla is None:
            raise BusinessRuleError(
                f"No se permite pasar de {self.nombre} a {estado_de(destino).nombre}."
            )
        if regla.solo_por_asignacion and not por_asignacion:
            raise BusinessRuleError("Para pasar a Asignada debe asignarse un responsable.")
        if not regla.autoriza(usuario, solicitud):
            raise ForbiddenError("No tiene permiso para realizar este cambio de estado.")
        if regla.requiere_motivo and not (motivo and motivo.strip()):
            raise BusinessRuleError("Debe indicar el motivo del cambio de estado.")
        if regla.requiere_solucion and not (solucion and solucion.strip()):
            raise BusinessRuleError("Para marcar como Resuelta debe registrar la solución aplicada.")
        return regla

    # --- efectos -------------------------------------------------------------------
    def al_entrar(self, solicitud: "Solicitud", solucion: str | None = None) -> None:
        """Hook ejecutado cuando la solicitud entra en este estado."""


class Registrada(EstadoBase):
    codigo, nombre = E.REGISTRADA, "Registrada"
    permite_edicion = True
    permite_asignacion = True
    transiciones = {
        E.ASIGNADA: ReglaTransicion(roles=STAFF_ASIGNADOR, solo_por_asignacion=True),
        E.RECHAZADA: ReglaTransicion(roles=STAFF_ASIGNADOR, requiere_motivo=True, etiqueta="Rechazar"),
    }


class Asignada(EstadoBase):
    codigo, nombre = E.ASIGNADA, "Asignada"
    permite_asignacion = True
    transiciones = {
        E.EN_PROCESO: ReglaTransicion(responsable=True, etiqueta="Iniciar atención"),
        E.RECHAZADA: ReglaTransicion(
            roles=STAFF_ASIGNADOR, responsable=True, requiere_motivo=True, etiqueta="Rechazar"
        ),
    }


class EnProceso(EstadoBase):
    codigo, nombre = E.EN_PROCESO, "En proceso"
    permite_asignacion = True
    transiciones = {
        E.RESUELTA: ReglaTransicion(responsable=True, requiere_solucion=True, etiqueta="Marcar como resuelta"),
        # Reasignar devuelve la solicitud a ASIGNADA para que el nuevo responsable la inicie
        E.ASIGNADA: ReglaTransicion(roles=STAFF_ASIGNADOR, solo_por_asignacion=True),
    }


class Resuelta(EstadoBase):
    codigo, nombre = E.RESUELTA, "Resuelta"
    transiciones = {
        E.CERRADA: ReglaTransicion(roles=STAFF_ASIGNADOR, solicitante=True, etiqueta="Cerrar solicitud"),
        E.REABIERTA: ReglaTransicion(
            roles=STAFF_ASIGNADOR, solicitante=True, requiere_motivo=True, etiqueta="Reabrir (no conforme)"
        ),
    }

    def al_entrar(self, solicitud, solucion=None):
        solicitud.solucion = solucion.strip() if solucion else solicitud.solucion
        solicitud.fecha_resolucion = utcnow()


class Cerrada(EstadoBase):
    codigo, nombre = E.CERRADA, "Cerrada"
    permite_observaciones = False  # una solicitud cerrada no puede modificarse
    transiciones = {
        # Reapertura autorizada: solo administrador o supervisor
        E.REABIERTA: ReglaTransicion(roles=STAFF_ASIGNADOR, requiere_motivo=True, etiqueta="Reapertura autorizada"),
    }

    def al_entrar(self, solicitud, solucion=None):
        solicitud.fecha_cierre = utcnow()


class Rechazada(EstadoBase):
    codigo, nombre = E.RECHAZADA, "Rechazada"
    permite_observaciones = False
    transiciones = {
        E.REABIERTA: ReglaTransicion(roles=STAFF_ASIGNADOR, requiere_motivo=True, etiqueta="Reabrir"),
    }

    def al_entrar(self, solicitud, solucion=None):
        solicitud.fecha_cierre = utcnow()


class Reabierta(EstadoBase):
    codigo, nombre = E.REABIERTA, "Reabierta"
    permite_asignacion = True
    transiciones = {
        E.ASIGNADA: ReglaTransicion(roles=STAFF_ASIGNADOR, solo_por_asignacion=True),
        E.EN_PROCESO: ReglaTransicion(responsable=True, etiqueta="Retomar atención"),
    }

    def al_entrar(self, solicitud, solucion=None):
        solicitud.fecha_resolucion = None
        solicitud.fecha_cierre = None


# Registro / fábrica simple de estados
_ESTADOS: dict[E, EstadoBase] = {
    cls.codigo: cls()
    for cls in (Registrada, Asignada, EnProceso, Resuelta, Cerrada, Rechazada, Reabierta)
}


def estado_de(codigo: E | str) -> EstadoBase:
    return _ESTADOS[E(codigo)]


def diagrama_transiciones() -> dict[str, list[str]]:
    """Representación de la máquina de estados (usada en documentación y pruebas)."""
    return {e.value: [d.value for d in s.transiciones] for e, s in _ESTADOS.items()}
