from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models import Usuario
from app.schemas import CambioPasswordIn, LoginIn, TokenOut, UsuarioOut
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/login", response_model=TokenOut)
def login(data: LoginIn, db: Session = Depends(get_db)):
    token, usuario = AuthService(db).login(data.email, data.password)
    return {"access_token": token, "usuario": usuario}


@router.get("/me", response_model=UsuarioOut)
def me(usuario: Usuario = Depends(get_current_user)):
    return usuario


@router.post("/cambiar-password", status_code=204)
def cambiar_password(data: CambioPasswordIn, usuario: Usuario = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    AuthService(db).cambiar_password(usuario, data.actual, data.nueva)
