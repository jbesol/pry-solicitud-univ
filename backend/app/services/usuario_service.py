from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.core.security import hash_password
from app.domain.enums import RolCodigo
from app.models import Usuario
from app.repositories import RolRepository, UsuarioRepository
from app.schemas import UsuarioCreate, UsuarioUpdate


class UsuarioService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UsuarioRepository(db)
        self.roles = RolRepository(db)

    def obtener(self, usuario_id: int) -> Usuario:
        u = self.repo.get(usuario_id)
        if not u:
            raise NotFoundError("Usuario no encontrado.")
        return u

    def listar(self, q=None, rol=None, activo=None) -> list[Usuario]:
        return self.repo.buscar(q=q, rol=rol, activo=activo)

    def funcionarios_activos(self) -> list[Usuario]:
        return self.repo.buscar(rol=RolCodigo.FUNCIONARIO, activo=True)

    def crear(self, data: UsuarioCreate) -> Usuario:
        if self.repo.por_email(data.email):
            raise ConflictError("Ya existe un usuario con ese correo.")
        if self.repo.por_documento(data.documento):
            raise ConflictError("Ya existe un usuario con ese documento.")
        rol = self.roles.por_codigo(data.rol)
        u = Usuario(
            documento=data.documento.strip(),
            nombres=data.nombres.strip(),
            apellidos=data.apellidos.strip(),
            email=data.email.lower(),
            password_hash=hash_password(data.password),
            telefono=data.telefono,
            dependencia=data.dependencia,
            rol_id=rol.id,
            activo=True,
        )
        self.repo.add(u)
        self.db.commit()
        self.db.refresh(u)
        return u

    def actualizar(self, usuario_id: int, data: UsuarioUpdate) -> Usuario:
        u = self.obtener(usuario_id)
        cambios = data.model_dump(exclude_unset=True)
        if "email" in cambios and cambios["email"]:
            otro = self.repo.por_email(cambios["email"])
            if otro and otro.id != u.id:
                raise ConflictError("Ya existe un usuario con ese correo.")
            cambios["email"] = cambios["email"].lower()
        if cambios.get("password"):
            u.password_hash = hash_password(cambios.pop("password"))
        cambios.pop("password", None)
        for k, v in cambios.items():
            setattr(u, k, v)
        self.db.commit()
        self.db.refresh(u)
        return u

    def _validar_no_ultimo_admin(self, u: Usuario, actor: Usuario):
        if u.rol.codigo == RolCodigo.ADMINISTRADOR:
            admins = self.repo.con_roles(RolCodigo.ADMINISTRADOR)
            if len(admins) <= 1:
                raise BusinessRuleError("Debe existir al menos un administrador activo.")

    def cambiar_rol(self, usuario_id: int, rol: RolCodigo, actor: Usuario) -> Usuario:
        u = self.obtener(usuario_id)
        if u.rol.codigo == rol:
            return u
        self._validar_no_ultimo_admin(u, actor)
        u.rol_id = self.roles.por_codigo(rol).id
        self.db.commit()
        self.db.expire(u)
        return self.obtener(usuario_id)

    def cambiar_activo(self, usuario_id: int, activo: bool, actor: Usuario) -> Usuario:
        u = self.obtener(usuario_id)
        if not activo:
            if u.id == actor.id:
                raise BusinessRuleError("No puede desactivar su propio usuario.")
            self._validar_no_ultimo_admin(u, actor)
        u.activo = activo
        self.db.commit()
        self.db.refresh(u)
        return u
