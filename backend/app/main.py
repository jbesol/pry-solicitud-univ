"""Punto de entrada de la API.

    uvicorn app.main:app --reload     (desde la carpeta backend/)
Documentación interactiva: http://localhost:8000/docs
"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.routers import auth, catalogos, notificaciones, reportes, solicitudes, usuarios
from app.bootstrap import init_db
from app.core.config import get_settings
from app.core.exceptions import DomainError

log = logging.getLogger("app")
settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.JWT_SECRET_KEY.startswith("dev-") and settings.ENVIRONMENT == "production":
        raise RuntimeError("Configure JWT_SECRET_KEY antes de ejecutar en producción.")
    if os.getenv("SKIP_INIT_DB") != "1":
        init_db(demo=os.getenv("SEED_DEMO", "true").lower() == "true")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API REST para registrar, asignar, atender y consultar solicitudes universitarias.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(DomainError)
async def domain_error_handler(_: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    errores = []
    for e in exc.errors():
        campo = ".".join(str(x) for x in e["loc"] if x not in ("body", "query", "path"))
        errores.append(f"{campo}: {e['msg']}" if campo else e["msg"])
    return JSONResponse(status_code=422, content={"detail": "Datos inválidos. " + "; ".join(errores)})


@app.get("/api/health", tags=["Sistema"])
def health():
    return {"status": "ok"}


for r in (auth, usuarios, catalogos, solicitudes, notificaciones, reportes):
    app.include_router(r.router, prefix="/api")


# --- Frontend compilado (frontend/dist) servido por la misma app, como en PlataformaCUL ----
FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (FRONTEND_DIR / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        if full_path.startswith("api/"):
            return JSONResponse(status_code=404, content={"detail": "Recurso no encontrado"})
        archivo = (FRONTEND_DIR / full_path).resolve()
        if full_path and archivo.is_file() and FRONTEND_DIR in archivo.parents:
            return FileResponse(archivo)
        return FileResponse(FRONTEND_DIR / "index.html")
