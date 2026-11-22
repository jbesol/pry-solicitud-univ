"""RF01, RF02 — Autenticación y control de acceso por rol."""
from app.core.security import hash_password, verify_password


def test_hash_password_no_guarda_texto_plano():
    h = hash_password("Secreta123")
    assert h != "Secreta123" and h.startswith("$2")
    assert verify_password("Secreta123", h)
    assert not verify_password("otra", h)


def test_login_correcto_devuelve_token_y_rol(client):
    r = client.post("/api/auth/login", json={"email": "admin@universidad.edu.co", "password": "Demo1234*"})
    assert r.status_code == 200
    assert r.json()["usuario"]["rol"]["codigo"] == "ADMINISTRADOR"
    assert "password_hash" not in r.json()["usuario"]


def test_login_incorrecto(client):
    r = client.post("/api/auth/login", json={"email": "admin@universidad.edu.co", "password": "mala"})
    assert r.status_code == 401


def test_endpoint_protegido_sin_token(client):
    assert client.get("/api/solicitudes").status_code == 401
    r = client.get("/api/solicitudes", headers={"Authorization": "Bearer token-falso"})
    assert r.status_code == 401


def test_solo_admin_gestiona_usuarios(client, h):
    assert client.get("/api/usuarios", headers=h["admin"]).status_code == 200
    for rol in ("estudiante", "funcionario", "supervisor"):
        assert client.get("/api/usuarios", headers=h[rol]).status_code == 403


def test_admin_crea_usuario_y_cambia_rol(client, h):
    nuevo = {"documento": "2000000001", "nombres": "Pedro", "apellidos": "Prueba",
             "email": "pedro@universidad.edu.co", "password": "Clave1234", "rol": "ESTUDIANTE"}
    r = client.post("/api/usuarios", json=nuevo, headers=h["admin"])
    assert r.status_code == 201
    uid = r.json()["id"]
    # correo duplicado
    assert client.post("/api/usuarios", json={**nuevo, "documento": "2000000002"}, headers=h["admin"]).status_code == 409
    r = client.patch(f"/api/usuarios/{uid}/rol", json={"rol": "FUNCIONARIO"}, headers=h["admin"])
    assert r.json()["rol"]["codigo"] == "FUNCIONARIO"


def test_usuario_inactivo_no_puede_ingresar(client, h, ids):
    client.patch(f"/api/usuarios/{ids['carlos.ramirez']}/activo", json={"activo": False}, headers=h["admin"])
    r = client.post("/api/auth/login", json={"email": "carlos.ramirez@universidad.edu.co", "password": "Demo1234*"})
    assert r.status_code == 401


def test_no_se_puede_quitar_el_ultimo_administrador(client, h, ids):
    r = client.patch(f"/api/usuarios/{ids['admin']}/rol", json={"rol": "ESTUDIANTE"}, headers=h["admin"])
    assert r.status_code == 422


def test_validacion_datos_obligatorios_usuario(client, h):
    r = client.post("/api/usuarios", json={"email": "no-es-correo", "rol": "ESTUDIANTE"}, headers=h["admin"])
    assert r.status_code == 422


def test_cambiar_password(client, h):
    r = client.post("/api/auth/cambiar-password", json={"actual": "Demo1234*", "nueva": "NuevaClave1"},
                    headers=h["estudiante"])
    assert r.status_code == 204
    r = client.post("/api/auth/login", json={"email": "estudiante@universidad.edu.co", "password": "NuevaClave1"})
    assert r.status_code == 200
