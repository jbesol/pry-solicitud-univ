"""RF11 — Reportes; pruebas unitarias de la máquina de estados (patrón State) y del Observer."""
from types import SimpleNamespace

import pytest

from app.core.exceptions import BusinessRuleError, ForbiddenError
from app.domain.enums import EstadoSolicitud as E
from app.domain.enums import RolCodigo as R
from app.domain.estados import diagrama_transiciones, estado_de
from app.services.eventos import Evento, Observador, PublicadorEventos


def test_reporte_solo_para_supervisor_y_admin(client, h):
    assert client.get("/api/reportes/resumen", headers=h["supervisor"]).status_code == 200
    assert client.get("/api/reportes/resumen", headers=h["admin"]).status_code == 200
    assert client.get("/api/reportes/resumen", headers=h["estudiante"]).status_code == 403
    assert client.get("/api/reportes/resumen", headers=h["funcionario"]).status_code == 403


def test_reporte_resumen_consistente(client, h):
    r = client.get("/api/reportes/resumen", headers=h["supervisor"]).json()
    assert r["total"] == 10
    assert sum(x["total"] for x in r["por_estado"]) == r["total"]
    assert sum(x["total"] for x in r["por_categoria"]) == r["total"]
    assert sum(x["total"] for x in r["por_prioridad"]) == r["total"]
    assert r["abiertas"] + r["finalizadas"] == r["total"]
    assert r["tiempo_promedio_resolucion_horas"] is not None


def test_reporte_filtra_por_estado_y_periodo(client, h):
    r = client.get("/api/reportes/resumen?estado=CERRADA", headers=h["supervisor"]).json()
    assert r["total"] == 2
    r = client.get("/api/reportes/resumen?desde=2000-01-01&hasta=2000-12-31", headers=h["supervisor"]).json()
    assert r["total"] == 0


def test_exportar_csv(client, h):
    r = client.get("/api/reportes/exportar", headers=h["supervisor"])
    assert r.status_code == 200 and "text/csv" in r.headers["content-type"]
    assert len(r.text.strip().splitlines()) == 11  # encabezado + 10 solicitudes


# ---------------------------------------------------------------- pruebas unitarias del dominio
def _usuario(id_, rol):
    return SimpleNamespace(id=id_, rol=SimpleNamespace(codigo=rol))


def _solicitud(solicitante=1, responsable=2):
    return SimpleNamespace(
        solicitante_id=solicitante, responsable_id=responsable,
        es_de=lambda u: u.id == solicitante, esta_asignada_a=lambda u: u.id == responsable,
    )


def test_maquina_de_estados_coincide_con_el_diseno():
    assert diagrama_transiciones() == {
        "REGISTRADA": ["ASIGNADA", "RECHAZADA"],
        "ASIGNADA": ["EN_PROCESO", "RECHAZADA"],
        "EN_PROCESO": ["RESUELTA", "ASIGNADA"],
        "RESUELTA": ["CERRADA", "REABIERTA"],
        "CERRADA": ["REABIERTA"],
        "RECHAZADA": ["REABIERTA"],
        "REABIERTA": ["ASIGNADA", "EN_PROCESO"],
    }


@pytest.mark.parametrize("origen,destino", [
    (E.REGISTRADA, E.CERRADA), (E.REGISTRADA, E.EN_PROCESO), (E.CERRADA, E.EN_PROCESO),
    (E.RESUELTA, E.EN_PROCESO), (E.RECHAZADA, E.CERRADA),
])
def test_transiciones_invalidas(origen, destino):
    admin = _usuario(9, R.ADMINISTRADOR)
    with pytest.raises(BusinessRuleError):
        estado_de(origen).validar_transicion(admin, _solicitud(), destino, "motivo", "solución")


def test_funcionario_no_asignado_no_resuelve():
    otro = _usuario(5, R.FUNCIONARIO)
    with pytest.raises(ForbiddenError):
        estado_de(E.EN_PROCESO).validar_transicion(otro, _solicitud(responsable=2), E.RESUELTA, None, "ok")


def test_cerrada_no_admite_observaciones():
    assert estado_de(E.CERRADA).permite_observaciones is False
    assert estado_de(E.REGISTRADA).permite_edicion is True


def test_publicador_notifica_a_todos_los_observadores():
    recibidos = []

    class Espia(Observador):
        def notificar(self, evento, db):
            recibidos.append(evento.tipo)

    pub = PublicadorEventos()
    pub.suscribir(Espia())
    pub.suscribir(Espia())
    actor = SimpleNamespace(id=1, activo=True)
    pub.publicar(Evento("X", None, actor, "t", "m", []), db=None)
    assert recibidos == ["X", "X"]


def test_evento_excluye_al_actor_y_duplicados():
    actor = SimpleNamespace(id=1, activo=True)
    otro = SimpleNamespace(id=2, activo=True)
    inactivo = SimpleNamespace(id=3, activo=False)
    ev = Evento("X", None, actor, "t", "m", [actor, otro, otro, None, inactivo])
    assert [u.id for u in ev.destinatarios_unicos()] == [2]
