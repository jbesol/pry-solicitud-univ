from sqlalchemy import update
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models import Notificacion, Usuario
from app.repositories import NotificacionRepository


class NotificacionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = NotificacionRepository(db)

    def listar(self, usuario: Usuario, solo_no_leidas=False, limite=50):
        return self.repo.de_usuario(usuario.id, solo_no_leidas, limite)

    def contar_no_leidas(self, usuario: Usuario) -> int:
        return self.repo.no_leidas(usuario.id)

    def marcar_leida(self, usuario: Usuario, notif_id: int) -> Notificacion:
        n = self.repo.get(notif_id)
        if not n or n.usuario_id != usuario.id:
            raise NotFoundError("Notificación no encontrada.")
        n.leida = True
        self.db.commit()
        return n

    def marcar_todas(self, usuario: Usuario) -> int:
        res = self.db.execute(
            update(Notificacion)
            .where(Notificacion.usuario_id == usuario.id, Notificacion.leida.is_(False))
            .values(leida=True)
        )
        self.db.commit()
        return res.rowcount or 0
