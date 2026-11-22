"""Notificaciones — Patrón de diseño OBSERVER.

El servicio de solicitudes publica eventos (registro, asignación, cambio de estado,
observación) en un `PublicadorEventos`. Los observadores suscritos reaccionan sin que
el publicador los conozca:

  * NotificacionInternaObserver → guarda avisos en la tabla `notificaciones`.
  * CorreoObserver             → envía correo SMTP (opcional, si está configurado).

Para agregar un canal nuevo (SMS, Teams, push) basta con crear otro observador.
"""
from __future__ import annotations

import logging
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from email.message import EmailMessage

from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.domain.enums import TipoEvento
from app.models import Notificacion, Solicitud, Usuario

log = logging.getLogger(__name__)


@dataclass
class Evento:
    tipo: TipoEvento
    solicitud: Solicitud
    actor: Usuario
    titulo: str
    mensaje: str
    destinatarios: list[Usuario] = field(default_factory=list)

    def destinatarios_unicos(self) -> list[Usuario]:
        """Sin duplicados y sin el usuario que provocó el evento."""
        vistos: dict[int, Usuario] = {}
        for u in self.destinatarios:
            if u is not None and u.id != self.actor.id and u.activo:
                vistos[u.id] = u
        return list(vistos.values())


class Observador(ABC):
    @abstractmethod
    def notificar(self, evento: Evento, db: Session) -> None: ...


class NotificacionInternaObserver(Observador):
    def notificar(self, evento: Evento, db: Session) -> None:
        for u in evento.destinatarios_unicos():
            db.add(
                Notificacion(
                    usuario_id=u.id,
                    solicitud_id=evento.solicitud.id,
                    tipo=evento.tipo,
                    titulo=evento.titulo,
                    mensaje=evento.mensaje,
                )
            )


class CorreoObserver(Observador):
    """Envía correo solo si SMTP_HOST está definido y el parámetro NOTIFICAR_CORREO = 'true'."""

    def notificar(self, evento: Evento, db: Session) -> None:
        from app.repositories import ParametroRepository  # evita import circular

        s = get_settings()
        if not s.SMTP_HOST or ParametroRepository(db).valor("NOTIFICAR_CORREO", "false").lower() != "true":
            return
        for u in evento.destinatarios_unicos():
            try:
                msg = EmailMessage()
                msg["Subject"] = evento.titulo
                msg["From"] = s.SMTP_FROM
                msg["To"] = u.email
                msg.set_content(f"Hola {u.nombres},\n\n{evento.mensaje}\n\nSistema de Solicitudes Universitarias")
                with smtplib.SMTP(s.SMTP_HOST, s.SMTP_PORT, timeout=5) as smtp:
                    smtp.starttls()
                    if s.SMTP_USER:
                        smtp.login(s.SMTP_USER, s.SMTP_PASSWORD)
                    smtp.send_message(msg)
            except Exception as exc:  # el correo es opcional: nunca debe romper la operación
                log.warning("No se pudo enviar correo a %s: %s", u.email, exc)


class PublicadorEventos:
    def __init__(self) -> None:
        self._observadores: list[Observador] = []

    def suscribir(self, obs: Observador) -> None:
        self._observadores.append(obs)

    def desuscribir(self, obs: Observador) -> None:
        self._observadores.remove(obs)

    def publicar(self, evento: Evento, db: Session) -> None:
        for obs in self._observadores:
            obs.notificar(evento, db)


# Instancia única de la aplicación con los observadores por defecto
publicador = PublicadorEventos()
publicador.suscribir(NotificacionInternaObserver())
publicador.suscribir(CorreoObserver())
