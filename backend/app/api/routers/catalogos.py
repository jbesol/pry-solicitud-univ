from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, solo_admin
from app.core.database import get_db
from app.domain.enums import RolCodigo
from app.models import Usuario
from app.schemas import ActivoUpdate, CategoriaIn, CategoriaOut, ParametroIn, ParametroOut
from app.services.catalogo_service import CategoriaService, ParametroService

router = APIRouter(tags=["Categorías y parámetros"])


@router.get("/categorias", response_model=list[CategoriaOut])
def listar_categorias(todas: bool = False, usuario: Usuario = Depends(get_current_user),
                      db: Session = Depends(get_db)):
    # Solo el administrador ve las categorías inactivas
    solo_activas = not (todas and usuario.rol.codigo == RolCodigo.ADMINISTRADOR)
    return CategoriaService(db).listar(solo_activas)


@router.post("/categorias", response_model=CategoriaOut, status_code=201)
def crear_categoria(data: CategoriaIn, _: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return CategoriaService(db).crear(data)


@router.put("/categorias/{cat_id}", response_model=CategoriaOut)
def actualizar_categoria(cat_id: int, data: CategoriaIn, _: Usuario = Depends(solo_admin),
                         db: Session = Depends(get_db)):
    return CategoriaService(db).actualizar(cat_id, data)


@router.patch("/categorias/{cat_id}/activa", response_model=CategoriaOut)
def activar_categoria(cat_id: int, data: ActivoUpdate, _: Usuario = Depends(solo_admin),
                      db: Session = Depends(get_db)):
    return CategoriaService(db).cambiar_activa(cat_id, data.activo)


@router.get("/parametros", response_model=list[ParametroOut])
def listar_parametros(_: Usuario = Depends(solo_admin), db: Session = Depends(get_db)):
    return ParametroService(db).listar()


@router.put("/parametros/{clave}", response_model=ParametroOut)
def actualizar_parametro(clave: str, data: ParametroIn, _: Usuario = Depends(solo_admin),
                         db: Session = Depends(get_db)):
    return ParametroService(db).actualizar(clave, data.valor)
