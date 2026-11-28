# Entrega 5 — Informe final

## 5.1 Descripción de la solución

El **SGSU** es una aplicación web que centraliza las solicitudes de servicios universitarios. Los estudiantes (y funcionarios) registran sus solicitudes desde el navegador. El supervisor las asigna a un funcionario responsable, que las atiende siguiendo un ciclo de vida controlado. Cada paso queda en el historial y genera notificaciones. La supervisión cuenta con indicadores de volumen y tiempos de respuesta.

Características principales:

- 4 roles con menús y permisos diferenciados, validados en el servidor.
- Ciclo de vida de 7 estados implementado con el patrón **State**; la interfaz solo muestra las acciones que el usuario puede ejecutar.
- Fecha límite automática según la categoría (SLA) e indicador de solicitudes **vencidas**.
- Historial completo (registro, asignaciones, cambios de estado, observaciones, ediciones) con fecha, usuario y motivo.
- Observaciones públicas e internas.
- Notificaciones internas con contador y correo opcional, implementadas con el patrón **Observer**.
- Reportes por estado, prioridad, categoría, responsable y mes; % de cumplimiento del SLA; tiempo promedio de resolución; exportación CSV.
- Interfaz responsiva en español, con la identidad de la Corporación Universitaria Latinoamericana.

## 5.2 Comparación con el alcance inicial

| Elemento del alcance (Entrega 1) | Resultado | Observación |
|---|---|---|
| Gestión de usuarios y roles | ✅ Cumplido | Además: activar/desactivar y protección del último administrador |
| Gestión de categorías y parámetros | ✅ Cumplido | Categorías con dependencia y tiempo de respuesta; 4 parámetros usados por el sistema |
| Registro de solicitudes | ✅ Cumplido | Se agregaron *asunto* y *canal* (justificados en el análisis) |
| Asignación, atención y observaciones | ✅ Cumplido | Además: reasignación y observaciones internas |
| Ciclo de vida con RECHAZADA y REABIERTA | ✅ Cumplido | Transiciones y condiciones documentadas en la sección 2.3 |
| Historial | ✅ Cumplido | Incluye responsable anterior/nuevo en reasignaciones |
| Notificaciones internas + correo opcional | ✅ Cumplido | Correo activable por parámetro sin cambiar código |
| Reportes por estado, categoría, prioridad, responsable y periodo | ✅ Cumplido | Más indicadores de SLA y exportación CSV |
| Adjuntos, SSO, integración con sistemas académicos | ⏸ Fuera de alcance | Se mantienen como mejoras futuras (sección 5.6) |

**Cambios de alcance justificados durante el proyecto:**

1. **El Supervisor también asigna responsables.** El enunciado dice "solo un usuario autorizado podrá asignar"; se definió que los usuarios autorizados son Administrador y Supervisor, porque en la práctica la coordinación es quien reparte la carga de trabajo.
2. **El Funcionario también puede registrar solicitudes.** El problema menciona solicitudes de estudiantes *y funcionarios*.
3. **El estudiante cierra o reabre su solicitud resuelta.** Así se confirma la conformidad del usuario antes de cerrar; la reapertura de una solicitud *cerrada* sigue reservada al personal autorizado (RN06).
4. **Límite de resultados en el listado (500).** Surgió de la prueba de rendimiento (sección 4.6).

## 5.3 Arquitectura definitiva y tecnologías

La arquitectura final es la diseñada en la [Entrega 3](03-diseno.md#31-arquitectura): cliente-servidor con API REST y backend en capas (API → servicios → dominio → repositorios → BD). No hubo cambios estructurales respecto al diseño; los diagramas del repositorio corresponden al código actual. Una prueba automática verifica que la máquina de estados coincida con el diagrama.

| Capa | Tecnología | Justificación resumida |
|---|---|---|
| Interfaz | Svelte 4, Vite, Tailwind CSS | Ligera, reactiva, responsiva; experiencia previa del equipo |
| API | FastAPI (Python 3.12) | Validación por tipos, OpenAPI automático, alto rendimiento |
| Persistencia | SQLAlchemy 2.0 + PostgreSQL 16 | ORM que refleja el diseño OO; BD relacional con integridad |
| Seguridad | JWT + bcrypt | Sesiones sin estado y contraseñas con hash adaptativo |
| Calidad | pytest, pytest-cov, radon, GitHub Actions | Pruebas automáticas, cobertura y métricas en cada cambio |
| Despliegue | Docker / docker-compose | Ejecución idéntica en cualquier equipo |

**Relación con el proyecto anterior (PlataformaCUL).** Se reutilizaron decisiones que funcionaron: stack FastAPI + PostgreSQL + Svelte/Tailwind, autenticación con JWT y bcrypt, y servir el frontend compilado desde FastAPI. Se corrigieron aspectos detectados en ese proyecto:

- Credenciales de BD escritas en el código → ahora solo por variables de entorno.
- SQL manual en los controladores → capas con repositorios y ORM.
- Reglas repartidas en condicionales → máquina de estados centralizada.
- Comparación de contraseñas en texto plano como respaldo → solo bcrypt.
- Ausencia de pruebas → 44 pruebas automatizadas con CI.

## 5.4 Resultados de las pruebas

- **44 de 44 pruebas aprobadas**, con **92 %** de cobertura del backend (detalle en la [sección 4.5](04-implementacion-pruebas.md#45-casos-de-prueba-y-resultados)).
- Los **16 requisitos funcionales** y las **15 reglas de negocio** tienen al menos un caso de prueba.
- Rendimiento: todas las consultas habituales responden en **≤ 0,14 s con 10.000 solicitudes** en PostgreSQL ([sección 4.6](04-implementacion-pruebas.md#46-prueba-de-rendimiento-rnf11)).
- Complejidad ciclomática promedio **A (2,3)** y mantenibilidad **A** en todos los módulos.
- Verificado en PostgreSQL 16 y SQLite.

## 5.5 Repositorio

**https://github.com/jbesol/pry-solicitud-univ**

## 5.6 Mejoras futuras

- Adjuntar archivos (soportes, documentos) a las solicitudes.
- Inicio de sesión único con la cuenta institucional (Microsoft 365 / Google).
- Notificaciones en tiempo real (WebSockets) en lugar de consulta periódica.
- Encuesta de satisfacción al cerrar la solicitud.
- Escalamiento automático al supervisor cuando una solicitud está por vencer.
- Paginación completa en el listado y en las notificaciones.

---

## Manual de instalación

### Opción A — Docker (recomendada, incluye PostgreSQL)

Requisitos: Docker Desktop.

```bash
git clone https://github.com/jbesol/pry-solicitud-univ.git
cd pry-solicitud-univ
docker compose up --build
```

Abrir **http://localhost:8000**. La primera vez se crean las tablas y los datos de demostración.

### Opción B — Ejecución local (sin Docker)

Requisitos: Python 3.11+ y Node.js 20+. PostgreSQL es opcional: sin él se usa SQLite automáticamente.

```bash
# 1. Backend
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (Linux/Mac: source .venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env            # Linux/Mac: cp .env.example .env
uvicorn app.main:app --reload     # API en http://localhost:8000  ·  documentación en /docs

# 2. Frontend (en otra terminal)
cd frontend
npm install
npm run dev                       # interfaz en http://localhost:5173
```

Para servir todo desde el puerto 8000, compile el frontend (`npm run build`). FastAPI detecta `frontend/dist` y lo sirve.

**Usar PostgreSQL:** cree la base `solicitudes` y en `backend/.env` defina
`DATABASE_URL=postgresql+psycopg2://usuario:clave@localhost:5432/solicitudes`.

**Reiniciar los datos de demostración:** `python -m app.bootstrap --reset` (desde `backend/`).

**Ejecutar las pruebas:**

```bash
cd backend
pip install -r requirements-dev.txt
pytest --cov=app
```

## Manual breve de uso

Usuarios de demostración (contraseña **`Demo1234*`**). En la pantalla de inicio de sesión hay botones para llenarlos automáticamente:

| Rol | Correo |
|---|---|
| Estudiante | estudiante@universidad.edu.co |
| Funcionario | funcionario@universidad.edu.co |
| Supervisor | supervisor@universidad.edu.co |
| Administrador | admin@universidad.edu.co |

**Estudiante**
1. *Inicio → + Nueva solicitud*: elija la categoría (verá el tiempo estimado de respuesta), escriba asunto y descripción y registre.
2. *Mis solicitudes*: consulte el estado; abra una solicitud para ver observaciones e historial.
3. Cuando esté **Resuelta**: *Cerrar solicitud* si quedó conforme, o *Reabrir (no conforme)* indicando el motivo.

**Supervisor**
1. *Solicitudes*: filtre por estado *Registrada* para ver las nuevas.
2. Abra la solicitud → *Asignar responsable* → elija el funcionario.
3. *Reportes*: elija el periodo (7/30/90 días o fechas) y la categoría; *Exportar CSV* para Excel.
4. Puede rechazar solicitudes improcedentes y autorizar reaperturas de solicitudes cerradas.

**Funcionario**
1. *Mis asignaciones*: las vencidas aparecen en rojo.
2. Abra la solicitud → *Iniciar atención* → agregue observaciones (marque *Nota interna* si el estudiante no debe verla).
3. *Marcar como resuelta* → escriba la solución aplicada (obligatoria).

**Administrador**
1. *Usuarios y roles*: cree usuarios, cambie su rol desde la lista y actívelos o desactívelos.
2. *Categorías*: cree tipos de servicio con su dependencia y tiempo de respuesta en horas.
3. *Parámetros*: prefijo del código, SLA por defecto, activar correo (requiere configurar SMTP en `.env`).

Todos los usuarios ven sus avisos en la **campana** de la barra superior y pueden cambiar su contraseña desde el menú lateral. En los campos de contraseña, el botón junto al texto permite mostrar u ocultar lo escrito.
