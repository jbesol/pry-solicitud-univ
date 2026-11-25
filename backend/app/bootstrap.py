"""Inicialización de la base de datos: crea tablas, roles, parámetros y (opcional) datos de demostración.

    python -m app.bootstrap          # tablas + catálogos + datos demo (si la BD está vacía)
    python -m app.bootstrap --reset  # BORRA todo y vuelve a sembrar (solo desarrollo)
"""
import random
import sys
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import Base, SessionLocal, engine
from app.core.security import hash_password
from app.domain.enums import Canal, EstadoSolicitud as E, Prioridad, RolCodigo as R
from app.models import Categoria, Movimiento, Notificacion, Rol, Solicitud, Usuario
from app.schemas import AsignacionIn, CambioEstadoIn, ObservacionIn, SolicitudCreate
from app.services.catalogo_service import ParametroService
from app.services.solicitud_service import SolicitudService

DEMO_PASSWORD = "Demo1234*"

ROLES = [
    (R.ADMINISTRADOR, "Administrador", "Gestiona usuarios, roles, categorías y parámetros"),
    (R.ESTUDIANTE, "Estudiante", "Registra solicitudes y consulta sus propios casos"),
    (R.FUNCIONARIO, "Funcionario", "Atiende las solicitudes asignadas"),
    (R.SUPERVISOR, "Supervisor", "Consulta indicadores, reportes y asigna responsables"),
]

CATEGORIAS = [
    ("Certificados académicos", "Constancias de estudio, notas y paz y salvo", "Registro y Control", 48),
    ("Homologaciones", "Estudio de homologación de asignaturas", "Coordinación Académica", 120),
    ("Soporte tecnológico", "Plataforma virtual, correo institucional, Wi-Fi", "Oficina TIC", 24),
    ("Financiera", "Pagos, recibos, financiación y devoluciones", "Tesorería", 72),
    ("Bienestar universitario", "Apoyos, becas, salud y actividades", "Bienestar", 96),
    ("Biblioteca", "Préstamos, multas y acceso a bases de datos", "Biblioteca", 48),
]

USUARIOS = [
    ("1000000001", "Ana", "Ramírez", "admin@universidad.edu.co", R.ADMINISTRADOR, "Oficina TIC"),
    ("1000000002", "Sergio", "Mendoza", "supervisor@universidad.edu.co", R.SUPERVISOR, "Vicerrectoría"),
    ("1000000003", "Fabio", "Pérez", "funcionario@universidad.edu.co", R.FUNCIONARIO, "Registro y Control"),
    ("1000000004", "Laura", "Gómez Torres", "laura.gomez@universidad.edu.co", R.FUNCIONARIO, "Oficina TIC"),
    ("1000000005", "Esteban", "Ruiz", "estudiante@universidad.edu.co", R.ESTUDIANTE, "Ingeniería de Sistemas"),
    ("1000000006", "María", "López Díaz", "maria.lopez@universidad.edu.co", R.ESTUDIANTE, "Contaduría Pública"),
    ("1000000007", "Carlos", "Ramírez Mejía", "carlos.ramirez@universidad.edu.co", R.ESTUDIANTE, "Derecho"),
]

DEMO_SOLICITUDES = [
    ("Certificado de notas del semestre 2026-1", "Necesito el certificado de notas para postularme a una beca externa.", 0, Prioridad.ALTA),
    ("No puedo ingresar a la plataforma virtual", "Desde ayer el aula virtual me muestra error de credenciales al iniciar sesión.", 2, Prioridad.URGENTE),
    ("Homologación de Cálculo I", "Vengo transferido de otra universidad y solicito homologar Cálculo I.", 1, Prioridad.MEDIA),
    ("Recibo de matrícula con valor errado", "El recibo generado no incluye el descuento por convenio que tengo aprobado.", 3, Prioridad.ALTA),
    ("Solicitud de apoyo alimentario", "Quisiera aplicar al programa de apoyo alimentario de bienestar.", 4, Prioridad.MEDIA),
    ("Multa de biblioteca por libro devuelto a tiempo", "Me cobraron una multa pero devolví el libro dentro del plazo.", 5, Prioridad.BAJA),
    ("Correo institucional bloqueado", "Mi correo institucional aparece bloqueado y no recibo notificaciones.", 2, Prioridad.ALTA),
    ("Constancia de estudio para el trabajo", "Requiero constancia de estudio con horario para presentar en mi empresa.", 0, Prioridad.MEDIA),
    ("Devolución de pago doble", "Pagué dos veces la matrícula por error del portal de pagos.", 3, Prioridad.URGENTE),
    ("Acceso a base de datos Scopus", "No tengo acceso a Scopus desde fuera del campus.", 5, Prioridad.BAJA),
]


def crear_tablas():
    Base.metadata.create_all(bind=engine)


def sembrar_catalogos(db: Session):
    for codigo, nombre, desc in ROLES:
        if not db.scalar(select(Rol).where(Rol.codigo == codigo)):
            db.add(Rol(codigo=codigo, nombre=nombre, descripcion=desc))
    db.commit()
    ParametroService(db).asegurar_por_defecto()


def sembrar_demo(db: Session):
    if db.scalar(select(Usuario).limit(1)):
        return False
    roles = {r.codigo: r.id for r in db.scalars(select(Rol))}
    pw = hash_password(DEMO_PASSWORD)
    usuarios = {}
    for doc, nom, ape, email, rol, dep in USUARIOS:
        u = Usuario(documento=doc, nombres=nom, apellidos=ape, email=email, password_hash=pw,
                    rol_id=roles[rol], dependencia=dep, activo=True)
        db.add(u)
        usuarios[email] = u
    cats = [Categoria(nombre=n, descripcion=d, dependencia=dep, tiempo_respuesta_horas=h, activa=True)
            for n, d, dep, h in CATEGORIAS]
    db.add_all(cats)
    db.commit()

    svc = SolicitudService(db)
    admin = usuarios["admin@universidad.edu.co"]
    sup = usuarios["supervisor@universidad.edu.co"]
    funcs = [usuarios["funcionario@universidad.edu.co"], usuarios["laura.gomez@universidad.edu.co"]]
    estudiantes = [u for u in usuarios.values() if u.rol_id == roles[R.ESTUDIANTE]]
    rnd = random.Random(42)
    # Estado objetivo de cada solicitud demo para poblar todos los estados y los reportes
    objetivos = [E.CERRADA, E.EN_PROCESO, E.ASIGNADA, E.RESUELTA, E.REGISTRADA,
                 E.RECHAZADA, E.CERRADA, E.REABIERTA, E.EN_PROCESO, E.REGISTRADA]

    for i, ((asunto, desc, cat_idx, prio), objetivo) in enumerate(zip(DEMO_SOLICITUDES, objetivos)):
        est = estudiantes[i % len(estudiantes)]
        s = svc.registrar(est, SolicitudCreate(asunto=asunto, descripcion=desc, categoria_id=cats[cat_idx].id,
                                               prioridad=prio, canal=rnd.choice(list(Canal))))
        func = funcs[0] if cat_idx in (0, 1, 3, 5) else funcs[1]
        if objetivo == E.RECHAZADA:
            svc.cambiar_estado(sup, s.id, CambioEstadoIn(estado=E.RECHAZADA,
                               comentario="La solicitud no corresponde a esta dependencia."))
        elif objetivo != E.REGISTRADA:
            svc.asignar(sup if i % 2 else admin, s.id, AsignacionIn(responsable_id=func.id))
            if objetivo != E.ASIGNADA:
                svc.cambiar_estado(func, s.id, CambioEstadoIn(estado=E.EN_PROCESO, comentario="Se inicia la revisión."))
                svc.agregar_observacion(func, s.id, ObservacionIn(texto="Se solicitó información a la dependencia.", interna=True))
            if objetivo in (E.RESUELTA, E.CERRADA, E.REABIERTA):
                svc.cambiar_estado(func, s.id, CambioEstadoIn(
                    estado=E.RESUELTA, solucion="Se atendió la solicitud y se envió respuesta al estudiante."))
            if objetivo == E.CERRADA:
                svc.cambiar_estado(est, s.id, CambioEstadoIn(estado=E.CERRADA, comentario="Gracias, quedó resuelto."))
            if objetivo == E.REABIERTA:
                svc.cambiar_estado(est, s.id, CambioEstadoIn(estado=E.REABIERTA,
                                   comentario="El problema persiste, sigo sin acceso."))

        # Distribuye fechas en los últimos 4 meses para que los reportes por periodo tengan datos
        desfase = timedelta(days=rnd.randint(2, 110), hours=rnd.randint(0, 20))
        sol = db.get(Solicitud, s.id)
        sol.fecha_registro -= desfase
        sol.fecha_limite -= desfase
        if sol.fecha_resolucion:
            sla = sol.categoria.tiempo_respuesta_horas
            sol.fecha_resolucion = sol.fecha_registro + timedelta(hours=round(sla * rnd.uniform(0.3, 1.25)))
        if sol.fecha_cierre:
            sol.fecha_cierre = (sol.fecha_resolucion or sol.fecha_registro) + timedelta(hours=rnd.randint(1, 24))
        for k, m in enumerate(sorted(sol.movimientos, key=lambda m: m.id)):
            m.fecha = sol.fecha_registro + timedelta(hours=k * rnd.randint(2, 12))
        db.commit()
    return True


def init_db(demo: bool = True) -> None:
    crear_tablas()
    with SessionLocal() as db:
        sembrar_catalogos(db)
        if demo:
            sembrar_demo(db)


if __name__ == "__main__":
    if "--reset" in sys.argv:
        Base.metadata.drop_all(bind=engine)
        print("Tablas eliminadas.")
    init_db(demo="--sin-demo" not in sys.argv)
    print("Base de datos lista. Usuarios demo con contraseña:", DEMO_PASSWORD)
