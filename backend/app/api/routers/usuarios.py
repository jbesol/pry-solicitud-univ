from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import solo_admin, staff
from app.core.database import get_db
from app.domain.enums import RolCodigo
from app.models import Usuario
from app.repositories import RolRepository
from app.schemas import (
    ActivoUpdate,
    RolOut,
    RolUpdate,
    UsuarioCreate,
    UsuarioOut,
    UsuarioResumen,
    UsuarioUpdate,
)
from app.services.usuario_service import UsuarioService

router = APIRouter(tags=["Usuarios y roles"])


@router.get("/roles", response_model=list[RolOut])
def listar_roles(_: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return RolRepository(db).list_all()


@router.get("/usuarios", response_model=list[UsuarioOut])
def listar(q: str | None = None, rol: RolCodigo | None = None, activo: bool | None = None,
           _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return UsuarioService(db).listar(q, rol, activo)


@router.get("/usuarios/funcionarios", response_model=list[UsuarioResumen])
def funcionarios(_: Usuario = Depends(staff), db: Session = Depends(get_db)):
    """Funcionarios activos disponibles para asignar solicitudes."""
    return UsuarioService(db).funcionarios_activos()


@router.post("/usuarios", response_model=UsuarioOut, status_code=201)
def crear(data: UsuarioCreate, _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return UsuarioService(db).crear(data)


@router.get("/usuarios/{usuario_id}", response_model=UsuarioOut)
def obtener(usuario_id: int, _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return UsuarioService(db).obtener(usuario_id)


@router.put("/usuarios/{usuario_id}", response_model=UsuarioOut)
def actualizar(usuario_id: int, data: UsuarioUpdate, _: Usuario = Depends(solo_admin),
               db: Session = Depends(get_db)):
    return UsuarioService(db).actualizar(usuario_id, data)


@router.patch("/usuarios/{usuario_id}/rol", response_model=UsuarioOut)
def cambiar_rol(usuario_id: int, data: RolUpdate, actor: Usuario = Depends(solo_admin),
                db: Session = Depends(get_db)):
    return UsuarioService(db).cambiar_rol(usuario_id, data.rol, actor)


@router.patch("/usuarios/{usuario_id}/activo", response_model=UsuarioOut)
def cambiar_activo(usuario_id: int, data: ActivoUpdate, actor: Usuario = Depends(solo_admin),
                   db: Session = Depends(get_db)):
    return UsuarioService(db).cambiar_activo(usuario_id, data.activo, actor)
