"""RF03–RF10 — Categorías, registro, consulta, ciclo de vida, observaciones, historial y notificaciones."""


def test_admin_gestiona_categorias(client, h):
    r = client.post("/api/categorias", json={"nombre": "Prácticas", "tiempo_respuesta_horas": 48}, headers=h["admin"])
    assert r.status_code == 201
    cid = r.json()["id"]
    assert client.post("/api/categorias", json={"nombre": "x"}, headers=h["estudiante"]).status_code == 403
    client.patch(f"/api/categorias/{cid}/activa", json={"activo": False}, headers=h["admin"])
    nombres = [c["nombre"] for c in client.get("/api/categorias", headers=h["estudiante"]).json()]
    assert "Prácticas" not in nombres  # categoría inactiva no se ofrece


def test_registro_estado_inicial_codigo_y_fecha_limite(nueva):
    s = nueva()
    assert s["estado"] == "REGISTRADA"
    assert s["codigo"].startswith("SOL-")
    assert s["fecha_limite"] is not None and s["responsable"] is None


def test_registro_requiere_categoria_valida(client, h):
    body = {"asunto": "Sin categoría", "descripcion": "Descripción larga de prueba", "categoria_id": 9999}
    assert client.post("/api/solicitudes", json=body, headers=h["estudiante"]).status_code == 422


def test_registro_valida_datos_obligatorios(client, h, ids):
    r = client.post("/api/solicitudes", json={"asunto": "x", "categoria_id": ids["categoria"]}, headers=h["estudiante"])
    assert r.status_code == 422


def test_supervisor_no_registra_solicitudes(client, h, ids):
    body = {"asunto": "Prueba sup", "descripcion": "Descripción larga de prueba", "categoria_id": ids["categoria"]}
    assert client.post("/api/solicitudes", json=body, headers=h["supervisor"]).status_code == 403


def test_estudiante_solo_ve_sus_solicitudes(client, h, nueva):
    s = nueva()
    propias = client.get("/api/solicitudes", headers=h["estudiante"]).json()
    assert all(x["solicitante"]["email"] == "estudiante@universidad.edu.co" for x in propias)
    # Otro estudiante no puede ver el detalle
    assert client.get(f"/api/solicitudes/{s['id']}", headers=h["estudiante2"]).status_code == 403


def test_funcionario_ve_solo_asignadas(client, h, nueva, ids):
    s = nueva()
    assert client.get(f"/api/solicitudes/{s['id']}", headers=h["funcionario"]).status_code == 403
    client.post(f"/api/solicitudes/{s['id']}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["supervisor"])
    lista = client.get("/api/solicitudes", headers=h["funcionario"]).json()
    assert s["id"] in [x["id"] for x in lista]
    assert all(x["responsable"]["email"] == "funcionario@universidad.edu.co" for x in lista)


def test_solo_staff_asigna_y_responsable_debe_ser_funcionario(client, h, nueva, ids):
    s = nueva()
    url = f"/api/solicitudes/{s['id']}/asignar"
    assert client.post(url, json={"responsable_id": ids["funcionario"]}, headers=h["funcionario"]).status_code == 403
    assert client.post(url, json={"responsable_id": ids["estudiante"]}, headers=h["admin"]).status_code == 422
    r = client.post(url, json={"responsable_id": ids["funcionario"]}, headers=h["admin"])
    assert r.status_code == 200 and r.json()["estado"] == "ASIGNADA"


def test_ciclo_de_vida_completo(client, h, nueva, ids):
    s = nueva()
    sid = s["id"]
    est = lambda hd, **b: client.post(f"/api/solicitudes/{sid}/estado", json=b, headers=hd)

    # No se puede saltar estados
    assert est(h["admin"], estado="RESUELTA", solucion="x").status_code == 422
    # ASIGNADA solo mediante asignación
    assert est(h["admin"], estado="ASIGNADA").status_code == 422

    client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["supervisor"])
    # Otro funcionario no asignado no puede iniciar
    assert est(h["funcionario2"], estado="EN_PROCESO").status_code == 403
    assert est(h["funcionario"], estado="EN_PROCESO").json()["estado"] == "EN_PROCESO"
    # RESUELTA exige solución
    assert est(h["funcionario"], estado="RESUELTA").status_code == 422
    r = est(h["funcionario"], estado="RESUELTA", solucion="Se generó el certificado.")
    assert r.json()["estado"] == "RESUELTA" and r.json()["fecha_resolucion"]
    # El estudiante cierra
    assert est(h["estudiante"], estado="CERRADA").json()["estado"] == "CERRADA"

    # Cerrada: no se modifica
    obs = client.post(f"/api/solicitudes/{sid}/observaciones", json={"texto": "Hola"}, headers=h["estudiante"])
    assert obs.status_code == 422
    assert client.patch(f"/api/solicitudes/{sid}", json={"prioridad": "BAJA"}, headers=h["admin"]).status_code == 422
    # Reapertura: el estudiante NO puede; supervisor sí, con motivo obligatorio
    assert est(h["estudiante"], estado="REABIERTA", comentario="Quiero reabrir").status_code == 403
    assert est(h["supervisor"], estado="REABIERTA").status_code == 422
    assert est(h["supervisor"], estado="REABIERTA", comentario="Reclamo justificado").json()["estado"] == "REABIERTA"


def test_historial_registra_fecha_usuario_y_motivo(client, h, nueva, ids):
    s = nueva()
    sid = s["id"]
    client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["admin"])
    client.post(f"/api/solicitudes/{sid}/estado", json={"estado": "RECHAZADA", "comentario": "Duplicada"},
                headers=h["funcionario"])
    hist = client.get(f"/api/solicitudes/{sid}/historial", headers=h["estudiante"]).json()
    tipos = [m["tipo"] for m in hist]
    assert tipos == ["REGISTRO", "ASIGNACION", "CAMBIO_ESTADO"]
    ultimo = hist[-1]
    assert ultimo["estado_anterior"] == "ASIGNADA" and ultimo["estado_nuevo"] == "RECHAZADA"
    assert ultimo["detalle"] == "Duplicada" and ultimo["usuario"]["email"] == "funcionario@universidad.edu.co"
    assert ultimo["fecha"]


def test_rechazo_requiere_motivo(client, h, nueva):
    s = nueva()
    r = client.post(f"/api/solicitudes/{s['id']}/estado", json={"estado": "RECHAZADA"}, headers=h["admin"])
    assert r.status_code == 422


def test_reasignacion_desde_en_proceso_vuelve_a_asignada(client, h, nueva, ids):
    s = nueva()
    sid = s["id"]
    client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["admin"])
    client.post(f"/api/solicitudes/{sid}/estado", json={"estado": "EN_PROCESO"}, headers=h["funcionario"])
    r = client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["laura.gomez"]}, headers=h["admin"])
    assert r.json()["estado"] == "ASIGNADA" and r.json()["responsable"]["email"] == "laura.gomez@universidad.edu.co"
    # El funcionario anterior pierde el acceso
    assert client.get(f"/api/solicitudes/{sid}", headers=h["funcionario"]).status_code == 403


def test_observaciones_internas_ocultas_al_estudiante(client, h, nueva, ids):
    s = nueva()
    sid = s["id"]
    client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["admin"])
    client.post(f"/api/solicitudes/{sid}/observaciones", json={"texto": "Nota interna", "interna": True}, headers=h["funcionario"])
    client.post(f"/api/solicitudes/{sid}/observaciones", json={"texto": "Mensaje público"}, headers=h["funcionario"])
    vista_est = client.get(f"/api/solicitudes/{sid}", headers=h["estudiante"]).json()
    vista_fun = client.get(f"/api/solicitudes/{sid}", headers=h["funcionario"]).json()
    assert [o["texto"] for o in vista_est["observaciones"]] == ["Mensaje público"]
    assert len(vista_fun["observaciones"]) == 2


def test_estudiante_edita_solo_en_registrada(client, h, nueva, ids):
    s = nueva()
    sid = s["id"]
    r = client.patch(f"/api/solicitudes/{sid}", json={"asunto": "Asunto corregido"}, headers=h["estudiante"])
    assert r.json()["asunto"] == "Asunto corregido"
    client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["admin"])
    r = client.patch(f"/api/solicitudes/{sid}", json={"asunto": "Otro cambio"}, headers=h["estudiante"])
    assert r.status_code == 422


def test_permisos_en_detalle_segun_usuario(client, h, nueva, ids):
    s = nueva()
    sid = s["id"]
    client.post(f"/api/solicitudes/{sid}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["admin"])
    fun = client.get(f"/api/solicitudes/{sid}", headers=h["funcionario"]).json()["permisos"]
    est = client.get(f"/api/solicitudes/{sid}", headers=h["estudiante"]).json()["permisos"]
    assert "EN_PROCESO" in [t["estado"] for t in fun["transiciones"]]
    assert est["transiciones"] == [] and est["puede_asignar"] is False


def test_notificaciones_al_registrar_asignar_y_actualizar(client, h, nueva, ids):
    antes_sup = client.get("/api/notificaciones/no-leidas", headers=h["supervisor"]).json()["total"]
    s = nueva()
    assert client.get("/api/notificaciones/no-leidas", headers=h["supervisor"]).json()["total"] == antes_sup + 1

    antes_fun = client.get("/api/notificaciones/no-leidas", headers=h["funcionario"]).json()["total"]
    client.post(f"/api/solicitudes/{s['id']}/asignar", json={"responsable_id": ids["funcionario"]}, headers=h["supervisor"])
    notifs = client.get("/api/notificaciones?no_leidas=true", headers=h["funcionario"]).json()
    assert len(notifs) == antes_fun + 1 and notifs[0]["tipo"] == "SOLICITUD_ASIGNADA"

    client.post(f"/api/solicitudes/{s['id']}/estado", json={"estado": "EN_PROCESO"}, headers=h["funcionario"])
    est = client.get("/api/notificaciones", headers=h["estudiante"]).json()
    assert est[0]["tipo"] == "ESTADO_ACTUALIZADO" and est[0]["solicitud_id"] == s["id"]

    client.patch("/api/notificaciones/leer-todas", headers=h["estudiante"])
    assert client.get("/api/notificaciones/no-leidas", headers=h["estudiante"]).json()["total"] == 0


def test_no_se_puede_leer_notificacion_ajena(client, h):
    n = client.get("/api/notificaciones", headers=h["supervisor"]).json()[0]
    assert client.patch(f"/api/notificaciones/{n['id']}/leida", headers=h["estudiante"]).status_code == 404


def test_parametros_solo_admin_y_validados(client, h, nueva):
    assert client.get("/api/parametros", headers=h["supervisor"]).status_code == 403
    claves = [p["clave"] for p in client.get("/api/parametros", headers=h["admin"]).json()]
    assert {"PREFIJO_CODIGO", "SLA_HORAS_DEFECTO", "NOTIFICAR_CORREO"} <= set(claves)
    assert client.put("/api/parametros/SLA_HORAS_DEFECTO", json={"valor": "-3"}, headers=h["admin"]).status_code == 422
    assert client.put("/api/parametros/PREFIJO_CODIGO", json={"valor": "PQRS"}, headers=h["admin"]).status_code == 200
    assert nueva()["codigo"].startswith("PQRS-")  # el parámetro se usa al generar el código


def test_categoria_nombre_duplicado(client, h):
    r = client.post("/api/categorias", json={"nombre": "Biblioteca"}, headers=h["admin"])
    assert r.status_code == 409
