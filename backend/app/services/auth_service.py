from sqlalchemy.orm import Session

from app.core.exceptions import AuthError, BusinessRuleError
from app.core.security import create_access_token, hash_password, verify_password
from app.models import Usuario
from app.repositories import UsuarioRepository


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.usuarios = UsuarioRepository(db)

    def login(self, email: str, password: str) -> tuple[str, Usuario]:
        usuario = self.usuarios.por_email(email)
        # Mismo mensaje para usuario inexistente o clave errada: no revela qué correos existen
        if not usuario or not verify_password(password, usuario.password_hash):
            raise AuthError("Correo o contraseña incorrectos.")
        if not usuario.activo:
            raise AuthError("El usuario está inactivo. Contacte al administrador.")
        return create_access_token(usuario.id, usuario.rol.codigo.value), usuario

    def cambiar_password(self, usuario: Usuario, actual: str, nueva: str) -> None:
        if not verify_password(actual, usuario.password_hash):
            raise BusinessRuleError("La contraseña actual no es correcta.")
        usuario.password_hash = hash_password(nueva)
        self.db.commit()
