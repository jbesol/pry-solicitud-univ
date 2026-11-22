"""Configuración de pruebas: cada prueba usa una BD SQLite en memoria nueva con datos demo."""
import os

os.environ["SKIP_INIT_DB"] = "1"
os.environ["DATABASE_URL"] = "sqlite://"

import bcrypt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app import bootstrap
from app.core import database
from app.core.database import Base, get_db
from app.main import app

PASSWORD = bootstrap.DEMO_PASSWORD

# En pruebas se usa un costo bajo de bcrypt para acelerar (en producción se usa el valor por defecto: 12)
_gensalt = bcrypt.gensalt
bcrypt.gensalt = lambda rounds=4, prefix=b"2b": _gensalt(4, prefix)


@pytest.fixture()
def db_session(monkeypatch):
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    monkeypatch.setattr(database, "engine", engine)
    monkeypatch.setattr(bootstrap, "engine", engine)
    Base.metadata.create_all(engine)
    with TestingSession() as s:
        bootstrap.sembrar_catalogos(s)
        bootstrap.sembrar_demo(s)
    yield TestingSession
    engine.dispose()


@pytest.fixture()
def client(db_session):
    def override():
        db = db_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def _login(client, email):
    r = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture()
def h(client):
    """Encabezados de autenticación por rol: h['admin'], h['estudiante'], ..."""
    return {
        "admin": _login(client, "admin@universidad.edu.co"),
        "supervisor": _login(client, "supervisor@universidad.edu.co"),
        "funcionario": _login(client, "funcionario@universidad.edu.co"),
        "funcionario2": _login(client, "laura.gomez@universidad.edu.co"),
        "estudiante": _login(client, "estudiante@universidad.edu.co"),
        "estudiante2": _login(client, "maria.lopez@universidad.edu.co"),
    }


@pytest.fixture()
def ids(client, h):
    """IDs útiles: usuarios y una categoría."""
    usuarios = {u["email"].split("@")[0]: u["id"] for u in client.get("/api/usuarios", headers=h["admin"]).json()}
    cat = client.get("/api/categorias", headers=h["estudiante"]).json()[0]["id"]
    return {**usuarios, "categoria": cat}


@pytest.fixture()
def nueva(client, h, ids):
    """Crea una solicitud nueva del estudiante demo y devuelve su JSON."""
    def _crear(headers=None, **kw):
        body = {"asunto": "Solicitud de prueba", "descripcion": "Descripción suficientemente larga.",
                "categoria_id": ids["categoria"], "prioridad": "ALTA", **kw}
        r = client.post("/api/solicitudes", json=body, headers=headers or h["estudiante"])
        assert r.status_code == 201, r.text
        return r.json()
    return _crear
