from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Usuario
from app.schemas import NotificacionOut
from app.services.notificacion_service import NotificacionService

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])


@router.get("", response_model=list[NotificacionOut])
def listar(no_leidas: bool = False, usuario: Usuario = Depends(get_current_user),
           db: Session = Depends(get_db)):
    return NotificacionService(db).listar(usuario, no_leidas)


@router.get("/no-leidas")
def contar(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"total": NotificacionService(db).contar_no_leidas(usuario)}


@router.patch("/{notif_id}/leida", response_model=NotificacionOut)
def marcar(notif_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return NotificacionService(db).marcar_leida(usuario, notif_id)


@router.patch("/leer-todas")
def marcar_todas(usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return {"actualizadas": NotificacionService(db).marcar_todas(usuario)}
