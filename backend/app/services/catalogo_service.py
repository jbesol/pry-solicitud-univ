"""Gestión de categorías de solicitud y parámetros del sistema (módulos del Administrador)."""
from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ConflictError, NotFoundError
from app.models import Categoria, Parametro
from app.repositories import CategoriaRepository, ParametroRepository
from app.schemas import CategoriaIn

PARAMETROS_POR_DEFECTO = {
    "PREFIJO_CODIGO": ("SOL", "Prefijo del código de las solicitudes (ej. SOL-2026-00001)"),
    "SLA_HORAS_DEFECTO": ("72", "Horas de respuesta cuando la categoría no define otro valor"),
    "NOTIFICAR_CORREO": ("false", "Enviar también las notificaciones por correo (true/false)"),
    "NOMBRE_INSTITUCION": ("Universidad", "Nombre mostrado en la interfaz y reportes"),
}


class CategoriaService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = CategoriaRepository(db)

    def listar(self, solo_activas=False):
        return self.repo.listar(solo_activas)

    def obtener(self, id_: int) -> Categoria:
        c = self.repo.get(id_)
        if not c:
            raise NotFoundError("Categoría no encontrada.")
        return c

    def crear(self, data: CategoriaIn) -> Categoria:
        if self.repo.por_nombre(data.nombre.strip()):
            raise ConflictError("Ya existe una categoría con ese nombre.")
        c = self.repo.add(Categoria(**data.model_dump(), activa=True))
        self.db.commit()
        return c

    def actualizar(self, id_: int, data: CategoriaIn) -> Categoria:
        c = self.obtener(id_)
        otra = self.repo.por_nombre(data.nombre.strip())
        if otra and otra.id != c.id:
            raise ConflictError("Ya existe una categoría con ese nombre.")
        for k, v in data.model_dump().items():
            setattr(c, k, v)
        self.db.commit()
        return c

    def cambiar_activa(self, id_: int, activa: bool) -> Categoria:
        # No se eliminan categorías con solicitudes: se desactivan para conservar la integridad.
        c = self.obtener(id_)
        c.activa = activa
        self.db.commit()
        return c


class ParametroService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = ParametroRepository(db)

    def listar(self):
        return sorted(self.repo.list_all(), key=lambda p: p.clave)

    def actualizar(self, clave: str, valor: str) -> Parametro:
        p = self.repo.get(clave)
        if not p:
            raise NotFoundError("Parámetro no encontrado.")
        valor = valor.strip()
        if clave == "SLA_HORAS_DEFECTO" and (not valor.isdigit() or int(valor) <= 0):
            raise BusinessRuleError("SLA_HORAS_DEFECTO debe ser un número entero positivo.")
        if clave == "NOTIFICAR_CORREO" and valor.lower() not in ("true", "false"):
            raise BusinessRuleError("NOTIFICAR_CORREO debe ser true o false.")
        if clave == "PREFIJO_CODIGO" and not (valor.isalnum() and len(valor) <= 6):
            raise BusinessRuleError("PREFIJO_CODIGO debe ser alfanumérico de máximo 6 caracteres.")
        p.valor = valor
        self.db.commit()
        return p

    def asegurar_por_defecto(self):
        for clave, (valor, desc) in PARAMETROS_POR_DEFECTO.items():
            if not self.repo.get(clave):
                self.db.add(Parametro(clave=clave, valor=valor, descripcion=desc))
        self.db.commit()
