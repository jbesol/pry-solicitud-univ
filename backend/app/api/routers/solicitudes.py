from datetime import date, datetime, time
from typing import Literal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.domain.enums import EstadoSolicitud, Prioridad
from app.domain.estados import diagrama_transiciones
from app.models import Usuario
from app.repositories import FiltroSolicitudes
from app.schemas import (
    AsignacionIn,
    CambioEstadoIn,
    MovimientoOut,
    ObservacionIn,
    ObservacionOut,
    SolicitudCreate,
    SolicitudDetalle,
    SolicitudOut,
    SolicitudUpdate,
)
from app.services.solicitud_service import SolicitudService

router = APIRouter(prefix="/solicitudes", tags=["Solicitudes"])


def filtros(
    estado: EstadoSolicitud | None = None,
    categoria_id: int | None = None,
    prioridad: Prioridad | None = None,
    responsable_id: int | None = None,
    desde: date | None = None,
    hasta: date | None = None,
    q: str | None = Query(default=None, max_length=100),
) -> FiltroSolicitudes:
    return FiltroSolicitudes(
        estado=estado, categoria_id=categoria_id, prioridad=prioridad, responsable_id=responsable_id,
        desde=datetime.combine(desde, time.min) if desde else None,
        hasta=datetime.combine(hasta, time.max) if hasta else None,
        q=q or None,
    )


@router.get("/estados", summary="Máquina de estados del ciclo de vida")
def estados(_: Usuario = Depends(get_current_user)):
    return diagrama_transiciones()


@router.post("", response_model=SolicitudOut, status_code=201)
def registrar(data: SolicitudCreate, usuario: Usuario = Depends(get_current_user),
              db: Session = Depends(get_db)):
    return SolicitudService(db).registrar(usuario, data)


@router.get("", response_model=list[SolicitudOut])
def listar(f: FiltroSolicitudes = Depends(filtros),
           alcance: Literal["asignadas", "propias", "todas"] | None = None,
           limite: int = Query(default=500, ge=1, le=5000, description="Máximo de resultados (más recientes primero)"),
           usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return SolicitudService(db).listar(usuario, f, alcance, limite)


@router.get("/{solicitud_id}", response_model=SolicitudDetalle)
def detalle(solicitud_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return SolicitudService(db).detalle(usuario, solicitud_id)


@router.patch("/{solicitud_id}", response_model=SolicitudOut)
def editar(solicitud_id: int, data: SolicitudUpdate, usuario: Usuario = Depends(get_current_user),
           db: Session = Depends(get_db)):
    return SolicitudService(db).editar(usuario, solicitud_id, data)


@router.post("/{solicitud_id}/asignar", response_model=SolicitudOut)
def asignar(solicitud_id: int, data: AsignacionIn, usuario: Usuario = Depends(get_current_user),
            db: Session = Depends(get_db)):
    return SolicitudService(db).asignar(usuario, solicitud_id, data)


@router.post("/{solicitud_id}/estado", response_model=SolicitudOut)
def cambiar_estado(solicitud_id: int, data: CambioEstadoIn, usuario: Usuario = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    return SolicitudService(db).cambiar_estado(usuario, solicitud_id, data)


@router.post("/{solicitud_id}/observaciones", response_model=ObservacionOut, status_code=201)
def observar(solicitud_id: int, data: ObservacionIn, usuario: Usuario = Depends(get_current_user),
             db: Session = Depends(get_db)):
    return SolicitudService(db).agregar_observacion(usuario, solicitud_id, data)


@router.get("/{solicitud_id}/historial", response_model=list[MovimientoOut])
def historial(solicitud_id: int, usuario: Usuario = Depends(get_current_user), db: Session = Depends(get_db)):
    return SolicitudService(db).historial(usuario, solicitud_id)
