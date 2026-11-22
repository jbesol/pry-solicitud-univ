from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.api.deps import staff
from app.api.routers.solicitudes import filtros
from app.core.database import get_db
from app.models import Usuario
from app.repositories import FiltroSolicitudes
from app.schemas import ReporteResumen
from app.services.reporte_service import ReporteService

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/resumen", response_model=ReporteResumen)
def resumen(f: FiltroSolicitudes = Depends(filtros), _: Usuario = Depends(staff),
            db: Session = Depends(get_db)):
    return ReporteService(db).resumen(f)


@router.get("/exportar")
def exportar(f: FiltroSolicitudes = Depends(filtros), _: Usuario = Depends(staff),
             db: Session = Depends(get_db)):
    contenido = ReporteService(db).exportar_csv(f)
    return Response(
        content=contenido,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="reporte_solicitudes.csv"'},
    )
