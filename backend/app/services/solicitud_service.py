"""Lógica de negocio de las solicitudes: registro, consulta, asignación, atención e historial.

Reglas de negocio implementadas (ver docs/02-analisis.md, RN01–RN10):
  RN01 Solo un usuario autenticado registra solicitudes (garantizado por la dependencia de auth).
  RN02 Toda solicitud se asocia a una categoría activa.
  RN03 El estado inicial es REGISTRADA.
  RN04 Solo Administrador o Supervisor asignan/reasignan responsables; el responsable debe ser Funcionario activo.
  RN05 Para pasar a RESUELTA se exige la solución aplicada.
  RN06 Una solicitud CERRADA no se modifica, salvo reapertura autorizada (Admin/Supervisor) con motivo.
  RN07 Cada cambio de estado guarda fecha, usuario y motivo/observación (tabla movimientos).
  RN08 El estudiante solo consulta sus propias solicitudes.
  RN09 El funcionario consulta las solicitudes que tiene asignadas (y las que él mismo registró).
  RN10 Las transiciones se validan contra la máquina de estados (domain/estados.py).
"""
from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.core.exceptions import BusinessRuleError, ForbiddenError, NotFoundError
from app.domain.enums import EstadoSolicitud as E
from app.domain.enums import RolCodigo as R
from app.domain.enums import TipoEvento, TipoMovimiento
from app.domain.estados import STAFF_ASIGNADOR, estado_de
from app.models import Movimiento, Notificacion, Observacion, Solicitud, Usuario
from app.repositories import (
    CategoriaRepository,
    FiltroSolicitudes,
    ParametroRepository,
    SolicitudRepository,
    UsuarioRepository,
)
from app.schemas import AsignacionIn, CambioEstadoIn, ObservacionIn, SolicitudCreate, SolicitudUpdate
from app.services.eventos import Evento, PublicadorEventos, publicador as publicador_global

ROLES_QUE_REGISTRAN = {R.ESTUDIANTE, R.FUNCIONARIO}


def es_staff(u: Usuario) -> bool:
    return u.rol.codigo in STAFF_ASIGNADOR


class SolicitudService:
    def __init__(self, db: Session, publicador: PublicadorEventos | None = None):
        self.db = db
        self.repo = SolicitudRepository(db)
        self.categorias = CategoriaRepository(db)
        self.usuarios = UsuarioRepository(db)
        self.parametros = ParametroRepository(db)
        self.publicador = publicador or publicador_global

    # ------------------------------------------------------------------ helpers
    def _registrar_movimiento(self, s: Solicitud, actor: Usuario, tipo: TipoMovimiento, **kw) -> None:
        self.db.add(Movimiento(solicitud_id=s.id, usuario_id=actor.id, tipo=tipo, **kw))

    def _publicar(self, tipo, s, actor, titulo, mensaje, destinatarios):
        self.publicador.publicar(Evento(tipo, s, actor, titulo, mensaje, destinatarios), self.db)

    def _verificar_acceso(self, usuario: Usuario, s: Solicitud) -> None:
        if es_staff(usuario):
            return
        if s.es_de(usuario):
            return
        if usuario.rol.codigo == R.FUNCIONARIO and s.esta_asignada_a(usuario):
            return
        raise ForbiddenError("No tiene acceso a esta solicitud.")

    def _cargar(self, solicitud_id: int) -> Solicitud:
        s = self.repo.get(solicitud_id)
        if not s:
            raise NotFoundError("Solicitud no encontrada.")
        return s

    # ------------------------------------------------------------------ registro (RF04)
    def registrar(self, usuario: Usuario, data: SolicitudCreate) -> Solicitud:
        if usuario.rol.codigo not in ROLES_QUE_REGISTRAN:
            raise ForbiddenError("Su rol no puede registrar solicitudes.")
        categoria = self.categorias.get(data.categoria_id)
        if not categoria or not categoria.activa:
            raise BusinessRuleError("Debe seleccionar una categoría válida y activa.")

        s = Solicitud(
            asunto=data.asunto.strip(),
            descripcion=data.descripcion.strip(),
            prioridad=data.prioridad,
            canal=data.canal,
            categoria_id=categoria.id,
            solicitante_id=usuario.id,
            estado=E.REGISTRADA,
        )
        self.repo.add(s)  # flush → obtiene id
        prefijo = self.parametros.valor("PREFIJO_CODIGO", "SOL")
        s.codigo = f"{prefijo}-{s.fecha_registro.year}-{s.id:05d}"
        horas = categoria.tiempo_respuesta_horas or int(self.parametros.valor("SLA_HORAS_DEFECTO", "72"))
        s.fecha_limite = s.fecha_registro + timedelta(hours=horas)

        self._registrar_movimiento(s, usuario, TipoMovimiento.REGISTRO, estado_nuevo=E.REGISTRADA,
                                   detalle="Solicitud registrada")
        destinatarios = self.usuarios.con_roles(R.ADMINISTRADOR, R.SUPERVISOR)
        self._publicar(
            TipoEvento.SOLICITUD_REGISTRADA, s, usuario,
            f"Nueva solicitud {s.codigo}",
            f"{usuario.nombre_completo} registró la solicitud {s.codigo} «{s.asunto}» "
            f"en la categoría {categoria.nombre} con prioridad {s.prioridad.value}.",
            destinatarios,
        )
        # El solicitante también recibe confirmación (el observador excluye al actor del evento)
        self.db.add(Notificacion(
            usuario_id=usuario.id, solicitud_id=s.id, tipo=TipoEvento.SOLICITUD_REGISTRADA,
            titulo=f"Solicitud {s.codigo} registrada",
            mensaje=f"Su solicitud «{s.asunto}» fue registrada. Fecha límite de respuesta: "
                    f"{s.fecha_limite:%Y-%m-%d %H:%M} UTC.",
        ))
        self.db.commit()
        self.db.refresh(s)
        return s

    # ------------------------------------------------------------------ consulta (RF05, RF06)
    def listar(self, usuario: Usuario, f: FiltroSolicitudes, alcance: str | None = None,
               limite: int | None = None) -> list[Solicitud]:
        rol = usuario.rol.codigo
        if rol == R.ESTUDIANTE:
            f.solicitante_id = usuario.id           # RN08
        elif rol == R.FUNCIONARIO:
            if alcance == "propias":
                f.solicitante_id = usuario.id
            else:
                f.responsable_id = usuario.id       # RN09
        elif alcance == "propias":
            f.solicitante_id = usuario.id
        return self.repo.buscar(f, limite)

    def obtener(self, usuario: Usuario, solicitud_id: int) -> Solicitud:
        s = self._cargar(solicitud_id)
        self._verificar_acceso(usuario, s)
        return s

    def detalle(self, usuario: Usuario, solicitud_id: int) -> dict:
        s = self.obtener(usuario, solicitud_id)
        estado = estado_de(s.estado)
        ve_interno = usuario.rol.codigo != R.ESTUDIANTE
        return {
            **{c: getattr(s, c) for c in (
                "id", "codigo", "asunto", "descripcion", "prioridad", "canal", "estado", "solucion",
                "fecha_registro", "fecha_actualizacion", "fecha_limite", "fecha_resolucion",
                "fecha_cierre", "vencida", "categoria", "solicitante", "responsable")},
            "observaciones": [o for o in s.observaciones if ve_interno or not o.interna],
            "movimientos": [m for m in s.movimientos if ve_interno or not m.interno],
            "permisos": {
                "puede_editar": self._puede_editar(usuario, s),
                "puede_asignar": es_staff(usuario) and estado.permite_asignacion,
                "puede_observar": estado.permite_observaciones,
                "transiciones": estado.transiciones_disponibles(usuario, s),
            },
        }

    def historial(self, usuario: Usuario, solicitud_id: int) -> list[Movimiento]:
        s = self.obtener(usuario, solicitud_id)
        ve_interno = usuario.rol.codigo != R.ESTUDIANTE
        return [m for m in s.movimientos if ve_interno or not m.interno]

    # ------------------------------------------------------------------ edición
    def _puede_editar(self, usuario: Usuario, s: Solicitud) -> bool:
        estado = estado_de(s.estado)
        if s.es_de(usuario) and estado.permite_edicion:
            return True
        return es_staff(usuario) and s.estado not in (E.CERRADA, E.RECHAZADA)

    def editar(self, usuario: Usuario, solicitud_id: int, data: SolicitudUpdate) -> Solicitud:
        s = self.obtener(usuario, solicitud_id)
        if not self._puede_editar(usuario, s):
            if s.estado == E.CERRADA:
                raise BusinessRuleError("Una solicitud cerrada no puede modificarse; debe reabrirse.")
            raise BusinessRuleError("La solicitud ya no puede editarse en su estado actual.")
        cambios = data.model_dump(exclude_unset=True, exclude_none=True)
        # El personal solo ajusta clasificación (categoría/prioridad), no el texto del solicitante
        if not s.es_de(usuario) or not estado_de(s.estado).permite_edicion:
            cambios = {k: v for k, v in cambios.items() if k in ("categoria_id", "prioridad")}
        if "categoria_id" in cambios:
            cat = self.categorias.get(cambios["categoria_id"])
            if not cat or not cat.activa:
                raise BusinessRuleError("Debe seleccionar una categoría válida y activa.")
        detalle = []
        for k, v in cambios.items():
            anterior = getattr(s, k)
            if anterior != v:
                detalle.append(k)
                setattr(s, k, v)
        if detalle:
            self._registrar_movimiento(s, usuario, TipoMovimiento.EDICION,
                                       detalle="Campos modificados: " + ", ".join(detalle))
            self.db.commit()
            self.db.refresh(s)
        return s

    # ------------------------------------------------------------------ asignación (RN04)
    def asignar(self, usuario: Usuario, solicitud_id: int, data: AsignacionIn) -> Solicitud:
        s = self._cargar(solicitud_id)
        if not es_staff(usuario):
            raise ForbiddenError("Solo el administrador o el supervisor pueden asignar responsables.")
        estado = estado_de(s.estado)
        if not estado.permite_asignacion:
            raise BusinessRuleError(f"No se puede asignar responsable a una solicitud {estado.nombre}.")
        responsable = self.usuarios.get(data.responsable_id)
        if not responsable or not responsable.activo or responsable.rol.codigo != R.FUNCIONARIO:
            raise BusinessRuleError("El responsable debe ser un funcionario activo.")
        if s.responsable_id == responsable.id:
            raise BusinessRuleError("La solicitud ya está asignada a ese funcionario.")

        anterior_resp = s.responsable
        anterior_estado = s.estado
        if s.estado != E.ASIGNADA:
            estado.validar_transicion(usuario, s, E.ASIGNADA, None, None, por_asignacion=True)
            s.estado = E.ASIGNADA
        s.responsable_id = responsable.id

        accion = "reasignada" if anterior_resp else "asignada"
        self._registrar_movimiento(
            s, usuario, TipoMovimiento.ASIGNACION,
            estado_anterior=anterior_estado, estado_nuevo=s.estado,
            responsable_anterior_id=anterior_resp.id if anterior_resp else None,
            responsable_nuevo_id=responsable.id,
            detalle=data.comentario or f"Solicitud {accion} a {responsable.nombre_completo}",
        )
        self._publicar(
            TipoEvento.SOLICITUD_ASIGNADA, s, usuario,
            f"Solicitud {s.codigo} {accion}",
            f"La solicitud {s.codigo} «{s.asunto}» fue {accion} a {responsable.nombre_completo}.",
            [responsable, s.solicitante, anterior_resp],
        )
        self.db.commit()
        self.db.expire(s)
        return self._cargar(solicitud_id)

    # ------------------------------------------------------------------ cambio de estado (RF07)
    def cambiar_estado(self, usuario: Usuario, solicitud_id: int, data: CambioEstadoIn) -> Solicitud:
        s = self.obtener(usuario, solicitud_id)
        actual = estado_de(s.estado)
        actual.validar_transicion(usuario, s, data.estado, data.comentario, data.solucion)

        destino = estado_de(data.estado)
        anterior = s.estado
        s.estado = data.estado
        destino.al_entrar(s, data.solucion)

        detalle = data.solucion if data.estado == E.RESUELTA else data.comentario
        if data.estado == E.RESUELTA and data.comentario:
            detalle = f"{data.solucion}\n\nObservación: {data.comentario}"
        self._registrar_movimiento(
            s, usuario, TipoMovimiento.CAMBIO_ESTADO,
            estado_anterior=anterior, estado_nuevo=data.estado,
            detalle=detalle or f"Cambio a {destino.nombre}",
        )
        self._publicar(
            TipoEvento.ESTADO_ACTUALIZADO, s, usuario,
            f"Solicitud {s.codigo}: {destino.nombre}",
            f"{usuario.nombre_completo} cambió la solicitud {s.codigo} de "
            f"{actual.nombre} a {destino.nombre}." + (f" Motivo: {data.comentario}" if data.comentario else ""),
            [s.solicitante, s.responsable, *(
                self.usuarios.con_roles(R.SUPERVISOR) if data.estado == E.REABIERTA else [])],
        )
        self.db.commit()
        self.db.refresh(s)
        return s

    # ------------------------------------------------------------------ observaciones (RF08)
    def agregar_observacion(self, usuario: Usuario, solicitud_id: int, data: ObservacionIn) -> Observacion:
        s = self.obtener(usuario, solicitud_id)
        estado = estado_de(s.estado)
        if not estado.permite_observaciones:
            raise BusinessRuleError(
                f"No se pueden registrar observaciones en una solicitud {estado.nombre}."
            )
        interna = data.interna and usuario.rol.codigo != R.ESTUDIANTE
        obs = Observacion(solicitud_id=s.id, autor_id=usuario.id, texto=data.texto.strip(), interna=interna)
        self.db.add(obs)
        self._registrar_movimiento(s, usuario, TipoMovimiento.OBSERVACION, detalle=obs.texto, interno=interna)
        destinatarios = [s.responsable] + ([] if interna else [s.solicitante])
        self._publicar(
            TipoEvento.OBSERVACION_AGREGADA, s, usuario,
            f"Nueva observación en {s.codigo}",
            f"{usuario.nombre_completo} escribió: {obs.texto[:200]}",
            destinatarios,
        )
        self.db.commit()
        self.db.refresh(obs)
        return obs
