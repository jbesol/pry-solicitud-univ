"""Reportes y estadísticas para el Supervisor (RF11): por estado, categoría, prioridad,
responsable y periodo, más indicadores de tiempos de respuesta."""
import csv
import io
from collections import Counter

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import utcnow
from app.domain.enums import ESTADOS_FINALIZADOS, EstadoSolicitud, Prioridad
from app.domain.estados import estado_de
from app.models import Categoria, Solicitud, Usuario
from app.repositories import FiltroSolicitudes, SolicitudRepository


class ReporteService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = SolicitudRepository(db)

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _items(conteo: dict, claves, etiqueta) -> list[dict]:
        """Convierte {clave: total} en la lista [{clave, etiqueta, total}] que consume la interfaz."""
        return [{"clave": str(k.value if hasattr(k, "value") else k or 0), "etiqueta": etiqueta(k),
                 "total": conteo.get(k, 0)} for k in claves]

    @staticmethod
    def _ordenar(items: list[dict]) -> list[dict]:
        return sorted(items, key=lambda x: -x["total"])

    def _nombres_responsables(self, ids) -> dict[int, str]:
        ids = [i for i in ids if i]
        if not ids:
            return {}
        usuarios = self.db.scalars(select(Usuario).where(Usuario.id.in_(ids))).unique()
        return {u.id: u.nombre_completo for u in usuarios}

    def _indicadores_tiempo(self, f: FiltroSolicitudes) -> dict:
        """Vencidas, cumplimiento del tiempo límite (SLA), promedio de resolución y conteo por mes."""
        filas = self.db.execute(self.repo._aplicar(
            select(Solicitud.estado, Solicitud.fecha_registro, Solicitud.fecha_limite, Solicitud.fecha_resolucion), f
        )).all()
        ahora = utcnow()
        resueltas = [r for r in filas if r.fecha_resolucion]
        horas = [(r.fecha_resolucion - r.fecha_registro).total_seconds() / 3600 for r in resueltas]
        a_tiempo = sum(1 for r in resueltas if r.fecha_limite and r.fecha_resolucion <= r.fecha_limite)
        abiertas_con_limite = [r for r in filas if r.estado not in ESTADOS_FINALIZADOS and r.fecha_limite]
        return {
            "total": len(filas),
            "vencidas": sum(1 for r in abiertas_con_limite if ahora > r.fecha_limite),
            "cumplimiento_sla": _porcentaje(a_tiempo, len(resueltas)),
            "tiempo_promedio_resolucion_horas": _promedio(horas),
            "por_mes": Counter(r.fecha_registro.strftime("%Y-%m") for r in filas),
        }

    # ------------------------------------------------------------------ API
    def resumen(self, f: FiltroSolicitudes) -> dict:
        por_estado = dict(self.repo.conteo_por(Solicitud.estado, f))
        por_prioridad = dict(self.repo.conteo_por(Solicitud.prioridad, f))
        por_categoria = dict(self.repo.conteo_por(Solicitud.categoria_id, f))
        por_responsable = dict(self.repo.conteo_por(Solicitud.responsable_id, f))
        categorias = {c.id: c.nombre for c in self.db.scalars(select(Categoria))}
        responsables = self._nombres_responsables(por_responsable)
        t = self._indicadores_tiempo(f)
        finalizadas = sum(por_estado.get(e, 0) for e in ESTADOS_FINALIZADOS)
        return {
            "total": t["total"],
            "abiertas": t["total"] - finalizadas,
            "finalizadas": finalizadas,
            "vencidas": t["vencidas"],
            "cumplimiento_sla": t["cumplimiento_sla"],
            "tiempo_promedio_resolucion_horas": t["tiempo_promedio_resolucion_horas"],
            "por_estado": self._items(por_estado, EstadoSolicitud, lambda e: estado_de(e).nombre),
            "por_prioridad": self._items(por_prioridad, Prioridad, lambda p: p.value.capitalize()),
            "por_categoria": self._ordenar(
                self._items(por_categoria, por_categoria, lambda k: categorias.get(k, "?"))),
            "por_responsable": self._ordenar(
                self._items(por_responsable, por_responsable, lambda k: responsables.get(k, "Sin asignar"))),
            "por_mes": [{"clave": k, "etiqueta": k, "total": v} for k, v in sorted(t["por_mes"].items())],
        }

    def exportar_csv(self, f: FiltroSolicitudes) -> str:
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";")
        w.writerow(["Código", "Fecha registro", "Asunto", "Categoría", "Prioridad", "Estado",
                    "Solicitante", "Responsable", "Fecha límite", "Fecha resolución", "Vencida"])
        for s in self.repo.buscar(f):
            w.writerow([
                s.codigo, s.fecha_registro.strftime("%Y-%m-%d %H:%M"), s.asunto, s.categoria.nombre,
                s.prioridad.value, estado_de(s.estado).nombre, s.solicitante.nombre_completo,
                s.responsable.nombre_completo if s.responsable else "",
                s.fecha_limite.strftime("%Y-%m-%d %H:%M") if s.fecha_limite else "",
                s.fecha_resolucion.strftime("%Y-%m-%d %H:%M") if s.fecha_resolucion else "",
                "Sí" if s.vencida else "No",
            ])
        return "﻿" + buf.getvalue()  # BOM para que Excel abra bien las tildes


def _porcentaje(parte: int, total: int) -> float | None:
    return round(100 * parte / total, 1) if total else None


def _promedio(valores: list[float]) -> float | None:
    return round(sum(valores) / len(valores), 1) if valores else None
