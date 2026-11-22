# Entrega 3 — Diseño del sistema

## 3.1 Arquitectura

Se eligió una **arquitectura cliente-servidor con API REST**, y en el servidor una **arquitectura en capas** (layered architecture):

```mermaid
flowchart TB
    subgraph Cliente["Cliente (navegador)"]
        UI["SPA Svelte + Tailwind<br/>páginas por rol"]
    end
    subgraph Servidor["Servidor (FastAPI · Python)"]
        API["Capa de presentación / API<br/>routers + validación Pydantic + control de acceso (deps)"]
        SRV["Capa de servicios (aplicación)<br/>SolicitudService, UsuarioService, ReporteService…"]
        DOM["Capa de dominio<br/>entidades, máquina de estados (State), eventos (Observer)"]
        REP["Capa de acceso a datos<br/>repositorios (Repository)"]
    end
    DB[("Base de datos relacional<br/>PostgreSQL / SQLite")]
    SMTP[["Servidor SMTP<br/>(opcional)"]]

    UI -- "HTTPS · JSON · JWT Bearer" --> API
    API --> SRV --> DOM
    SRV --> REP --> DB
    DOM -. "CorreoObserver" .-> SMTP
```

**Justificación**

| Decisión | Motivo |
|---|---|
| Cliente-servidor con API REST | Separa la interfaz de la lógica; la misma API sirve para la web y para una futura app móvil o integración |
| Capas con dependencias hacia abajo | Cada capa tiene una responsabilidad: la API no conoce SQL, los servicios no conocen HTTP. Facilita pruebas y cambios (RNF09) |
| Reglas del ciclo de vida en la capa de dominio | Las reglas de negocio más críticas están en un solo lugar (`domain/estados.py`), no repartidas en controladores |
| Un único despliegue (FastAPI sirve el frontend compilado) | Simplifica la instalación y la sustentación: un proceso, un puerto. Misma estrategia que el proyecto previo PlataformaCUL |

### Tecnologías

| Componente | Tecnología | Justificación |
|---|---|---|
| Backend | **Python 3.12 + FastAPI** | Experiencia previa del equipo (PlataformaCUL); validación automática con tipos; documentación OpenAPI/Swagger generada en `/docs` |
| ORM | **SQLAlchemy 2.0** | Mapea las clases del diseño OO a tablas; independiza del motor (PostgreSQL / SQLite); evita inyección SQL |
| Base de datos | **PostgreSQL 16** (producción), SQLite (desarrollo/pruebas) | Relacional, gratuita, con integridad referencial y restricciones CHECK |
| Autenticación | **JWT (PyJWT) + bcrypt** | Sesiones sin estado en el servidor; contraseñas con hash adaptativo |
| Frontend | **Svelte 4 + Vite + Tailwind CSS** | Ligero y reactivo, poco código; Tailwind permite una interfaz consistente y responsiva |
| Pruebas | **pytest + pytest-cov + TestClient** | Pruebas unitarias y de integración de la API con BD en memoria |
| Despliegue | **Docker + docker-compose** | Mismo entorno en cualquier equipo; levanta BD y aplicación con un comando |
| Control de versiones / CI | **Git + GitHub + GitHub Actions** | Historial del avance; pruebas automáticas en cada push |

## 3.2 Módulos y componentes

```mermaid
flowchart LR
    subgraph Frontend
        P1[Login] --- P2[Inicio por rol]
        P3[Solicitudes / Detalle] --- P4[Notificaciones]
        P5[Usuarios · Categorías · Parámetros] --- P6[Reportes]
    end
    subgraph Backend["Backend — routers"]
        R1[auth] --- R2[usuarios]
        R3[catalogos] --- R4[solicitudes]
        R5[notificaciones] --- R6[reportes]
    end
    P1 --> R1
    P5 --> R2 & R3
    P3 --> R4
    P4 --> R5
    P6 --> R6
```

| Módulo obligatorio | Componentes backend | Componentes frontend |
|---|---|---|
| Gestión de usuarios | `routers/usuarios.py`, `UsuarioService`, `UsuarioRepository`, `RolRepository` | `pages/Usuarios.svelte` |
| Gestión de categorías | `routers/catalogos.py`, `CategoriaService`, `ParametroService` | `pages/Categorias.svelte`, `pages/Parametros.svelte` |
| Registro de solicitudes | `routers/solicitudes.py`, `SolicitudService.registrar` | `components/NuevaSolicitud.svelte` |
| Asignación y atención | `SolicitudService.asignar / cambiar_estado / agregar_observacion`, `domain/estados.py` | `pages/SolicitudDetalle.svelte` |
| Seguimiento e historial | `Movimiento`, `SolicitudService.historial` | `pages/Solicitudes.svelte`, línea de tiempo en el detalle |
| Notificaciones | `services/eventos.py`, `NotificacionService`, `routers/notificaciones.py` | Campana en `Layout.svelte`, `pages/Notificaciones.svelte` |
| Reportes y estadísticas | `ReporteService`, `routers/reportes.py` | `pages/Reportes.svelte`, `components/Barras.svelte` |
| Autenticación y acceso | `core/security.py`, `api/deps.py`, `AuthService` | `pages/Login.svelte`, `components/Protegida.svelte`, `lib/api.js` |

Estructura del código:

```
backend/app/
├── main.py              # Arranque, manejo de errores, registro de routers
├── bootstrap.py         # Creación de tablas, catálogos y datos de demostración
├── core/                # Configuración, BD, seguridad (bcrypt/JWT), excepciones de dominio
├── domain/              # Enumeraciones y máquina de estados (patrón State)
├── models/              # Entidades SQLAlchemy (clases del modelo OO)
├── repositories/        # Acceso a datos (patrón Repository)
├── services/            # Lógica de negocio + eventos/notificaciones (patrón Observer)
├── schemas/             # DTOs de entrada/salida (Pydantic)
└── api/                 # Dependencias de seguridad y routers REST
```

## 3.3 Diagrama de clases

### Modelo de dominio (entidades persistentes)

```mermaid
classDiagram
    direction LR
    class Rol {
        +int id
        +RolCodigo codigo
        +str nombre
        +str descripcion
    }
    class Usuario {
        +int id
        +str documento
        +str nombres
        +str apellidos
        +str email
        -str password_hash
        +str telefono
        +str dependencia
        +bool activo
        +datetime fecha_creacion
        +nombre_completo() str
        +tiene_rol(roles) bool
    }
    class Categoria {
        +int id
        +str nombre
        +str descripcion
        +str dependencia
        +int tiempo_respuesta_horas
        +bool activa
    }
    class Solicitud {
        +int id
        +str codigo
        +str asunto
        +str descripcion
        +Prioridad prioridad
        +Canal canal
        +EstadoSolicitud estado
        +str solucion
        +datetime fecha_registro
        +datetime fecha_limite
        +datetime fecha_resolucion
        +datetime fecha_cierre
        +vencida() bool
        +es_de(usuario) bool
        +esta_asignada_a(usuario) bool
    }
    class Observacion {
        +int id
        +str texto
        +bool interna
        +datetime fecha
    }
    class Movimiento {
        +int id
        +TipoMovimiento tipo
        +EstadoSolicitud estado_anterior
        +EstadoSolicitud estado_nuevo
        +str detalle
        +bool interno
        +datetime fecha
    }
    class Notificacion {
        +int id
        +TipoEvento tipo
        +str titulo
        +str mensaje
        +bool leida
        +datetime fecha
    }
    class Parametro {
        +str clave
        +str valor
        +str descripcion
    }

    Rol "1" <-- "0..*" Usuario : rol
    Usuario "1" <-- "0..*" Solicitud : solicitante
    Usuario "0..1" <-- "0..*" Solicitud : responsable
    Categoria "1" <-- "0..*" Solicitud : categoria
    Solicitud "1" *-- "0..*" Observacion : observaciones
    Solicitud "1" *-- "0..*" Movimiento : movimientos
    Usuario "1" <-- "0..*" Observacion : autor
    Usuario "1" <-- "0..*" Movimiento : usuario
    Usuario "0..1" <-- "0..*" Movimiento : responsable anterior/nuevo
    Usuario "1" <-- "0..*" Notificacion : destinatario
    Solicitud "0..1" <-- "0..*" Notificacion : origen
```

### Ciclo de vida (patrón State)

```mermaid
classDiagram
    direction TB
    class SolicitudService {
        +registrar(usuario, datos) Solicitud
        +listar(usuario, filtro, alcance) list
        +detalle(usuario, id) dict
        +editar(usuario, id, datos) Solicitud
        +asignar(usuario, id, datos) Solicitud
        +cambiar_estado(usuario, id, datos) Solicitud
        +agregar_observacion(usuario, id, datos) Observacion
        +historial(usuario, id) list
    }
    class EstadoBase {
        <<abstract>>
        +EstadoSolicitud codigo
        +str nombre
        +dict transiciones
        +bool permite_edicion
        +bool permite_observaciones
        +bool permite_asignacion
        +transiciones_disponibles(usuario, solicitud) list
        +validar_transicion(usuario, solicitud, destino, motivo, solucion) ReglaTransicion
        +al_entrar(solicitud, solucion)
    }
    class ReglaTransicion {
        +frozenset roles
        +bool responsable
        +bool solicitante
        +bool requiere_motivo
        +bool requiere_solucion
        +bool solo_por_asignacion
        +autoriza(usuario, solicitud) bool
    }
    class Registrada
    class Asignada
    class EnProceso
    class Resuelta {
        +al_entrar()
    }
    class Cerrada {
        +al_entrar()
    }
    class Rechazada {
        +al_entrar()
    }
    class Reabierta {
        +al_entrar()
    }

    EstadoBase <|-- Registrada
    EstadoBase <|-- Asignada
    EstadoBase <|-- EnProceso
    EstadoBase <|-- Resuelta
    EstadoBase <|-- Cerrada
    EstadoBase <|-- Rechazada
    EstadoBase <|-- Reabierta
    EstadoBase "1" *-- "1..*" ReglaTransicion : transiciones
    SolicitudService ..> EstadoBase : estado_de(codigo)
```

### Notificaciones (patrón Observer) y acceso a datos (patrón Repository)

```mermaid
classDiagram
    direction LR
    class PublicadorEventos {
        -list~Observador~ observadores
        +suscribir(obs)
        +desuscribir(obs)
        +publicar(evento, db)
    }
    class Observador {
        <<interface>>
        +notificar(evento, db)
    }
    class NotificacionInternaObserver {
        +notificar(evento, db)
    }
    class CorreoObserver {
        +notificar(evento, db)
    }
    class Evento {
        +TipoEvento tipo
        +Solicitud solicitud
        +Usuario actor
        +str titulo
        +str mensaje
        +list destinatarios
        +destinatarios_unicos() list
    }
    class BaseRepository~T~ {
        #Session db
        +get(id) T
        +add(obj) T
        +list_all() list~T~
    }
    class SolicitudRepository {
        +buscar(filtro) list
        +conteo_por(columna, filtro) list
    }
    class UsuarioRepository {
        +por_email(email) Usuario
        +por_documento(doc) Usuario
        +buscar(q, rol, activo) list
        +con_roles(roles) list
    }
    class CategoriaRepository
    class NotificacionRepository
    class ParametroRepository {
        +valor(clave, defecto) str
    }
    class SolicitudService
    class ReporteService {
        +resumen(filtro) dict
        +exportar_csv(filtro) str
    }

    Observador <|.. NotificacionInternaObserver
    Observador <|.. CorreoObserver
    PublicadorEventos "1" o-- "0..*" Observador
    PublicadorEventos ..> Evento
    BaseRepository <|-- SolicitudRepository
    BaseRepository <|-- UsuarioRepository
    BaseRepository <|-- CategoriaRepository
    BaseRepository <|-- NotificacionRepository
    BaseRepository <|-- ParametroRepository
    SolicitudService --> PublicadorEventos : publica
    SolicitudService --> SolicitudRepository
    SolicitudService --> UsuarioRepository
    SolicitudService --> CategoriaRepository
    ReporteService --> SolicitudRepository
```

## 3.4 Responsabilidades y colaboraciones (tarjetas CRC)

| Clase | Responsabilidades | Colaboradores |
|---|---|---|
| **Usuario** | Conocer sus datos, su rol y si está activo | Rol |
| **Solicitud** | Conocer sus datos, estado, fechas; saber si está vencida, quién la registró y quién la atiende | Usuario, Categoria, Observacion, Movimiento |
| **Categoria** | Definir el tipo de servicio, la dependencia y el tiempo de respuesta | Solicitud |
| **Movimiento** | Registrar un hecho del historial (quién, cuándo, qué cambió y por qué) | Solicitud, Usuario |
| **Observacion** | Guardar un comentario público o interno | Solicitud, Usuario |
| **Notificacion** | Guardar un aviso para un usuario y si ya fue leído | Usuario, Solicitud |
| **EstadoBase** (y subclases) | Decidir qué transiciones existen, quién las autoriza y qué datos exigen; aplicar efectos al entrar a un estado | ReglaTransicion, Solicitud, Usuario |
| **ReglaTransicion** | Evaluar si un usuario puede ejecutar una transición sobre una solicitud | Usuario, Solicitud |
| **SolicitudService** | Orquestar los casos de uso de solicitudes: validar acceso, delegar en el estado, registrar movimientos, publicar eventos, confirmar la transacción | EstadoBase, repositorios, PublicadorEventos |
| **PublicadorEventos** | Distribuir cada evento a todos los observadores suscritos | Observador, Evento |
| **NotificacionInternaObserver** | Crear notificaciones en la BD para los destinatarios | Notificacion |
| **CorreoObserver** | Enviar correo si está configurado; nunca interrumpir la operación | ParametroRepository, SMTP |
| **Repositorios** | Encapsular consultas a la BD (búsquedas, filtros, conteos) | Session (SQLAlchemy), entidades |
| **ReporteService** | Calcular indicadores y conteos por estado, categoría, prioridad, responsable y periodo; exportar CSV | SolicitudRepository |
| **UsuarioService / AuthService** | Gestionar usuarios y roles / autenticar y emitir tokens | UsuarioRepository, RolRepository, security |

### Secuencia: cambiar estado de una solicitud

```mermaid
sequenceDiagram
    actor F as Funcionario
    participant UI as Frontend (Svelte)
    participant API as Router /solicitudes
    participant D as deps.get_current_user
    participant S as SolicitudService
    participant E as EstadoBase (EnProceso)
    participant P as PublicadorEventos
    participant DB as Base de datos

    F->>UI: Clic "Marcar como resuelta" + solución
    UI->>API: POST /api/solicitudes/12/estado {estado: RESUELTA, solucion}
    API->>D: valida JWT y usuario activo
    D-->>API: Usuario
    API->>S: cambiar_estado(usuario, 12, datos)
    S->>DB: cargar solicitud 12
    S->>S: verificar acceso (RN08/RN09)
    S->>E: validar_transicion(usuario, solicitud, RESUELTA, motivo, solucion)
    E-->>S: ok (o BusinessRuleError / ForbiddenError)
    S->>S: solicitud.estado = RESUELTA y Resuelta.al_entrar()
    S->>DB: INSERT movimiento (CAMBIO_ESTADO)
    S->>P: publicar(Evento ESTADO_ACTUALIZADO)
    P->>DB: INSERT notificaciones (observer interno)
    S->>DB: COMMIT
    S-->>API: Solicitud
    API-->>UI: 200 JSON
    UI-->>F: "Solicitud actualizada a «Resuelta»"
```

## 3.5 Diseño de la base de datos relacional

El esquema completo (generado desde PostgreSQL) está en [`backend/sql/schema_postgresql.sql`](../backend/sql/schema_postgresql.sql). La aplicación crea las tablas automáticamente al iniciar.

| Tabla | PK | Llaves foráneas | Únicos | Restricciones / índices |
|---|---|---|---|---|
| `roles` | id | — | codigo | CHECK codigo ∈ 4 roles |
| `usuarios` | id | rol_id → roles | documento, email | Índices en documento y email |
| `categorias` | id | — | nombre | CHECK tiempo_respuesta_horas > 0 |
| `solicitudes` | id | solicitante_id, responsable_id → usuarios; categoria_id → categorias | codigo | CHECK estado, prioridad, canal; índices en estado, fecha_registro, solicitante, responsable, categoría |
| `observaciones` | id | solicitud_id (ON DELETE CASCADE), autor_id | — | Índice en solicitud_id |
| `movimientos` | id | solicitud_id (CASCADE), usuario_id, responsable_anterior_id, responsable_nuevo_id | — | CHECK tipo y estados; índices en solicitud_id y fecha |
| `notificaciones` | id | usuario_id (CASCADE), solicitud_id (CASCADE) | — | Índices en usuario_id y leida |
| `parametros` | clave | — | — | — |

**Normalización:** el esquema está en **3FN**. Los datos del solicitante y del responsable no se copian en la solicitud (se referencian por FK); el nombre de la categoría no se repite; el historial vive en su propia tabla en lugar de columnas repetidas. Los estados, prioridades y canales se guardan como texto con restricción CHECK (en vez de tablas catálogo) porque son valores fijos definidos por las reglas de negocio y no los administra el usuario; los roles sí tienen tabla porque se asignan a usuarios y tienen descripción.

## 3.6 Prototipos de interfaz

Los bocetos iniciales se refinaron directamente en la implementación. Pantallas principales:

| Pantalla | Captura |
|---|---|
| Inicio de sesión | ![](img/01-login.png) |
| Inicio del estudiante | ![](img/02-inicio-estudiante.png) |
| Registrar solicitud | ![](img/03-registrar-solicitud.png) |
| Listado con filtros (supervisor) | ![](img/07-listado-supervisor.png) |
| Detalle, observaciones e historial | ![](img/12-detalle-resuelta.png) |
| Reportes | ![](img/08-reportes.png) |
| Gestión de usuarios | ![](img/16-usuarios.png) |
| Vista en celular | ![](img/20-movil.png) |

Criterios de diseño de interfaz:

- **Un menú por rol**: cada usuario ve solo lo que puede hacer.
- **Acciones contextuales**: el detalle muestra únicamente los botones de las transiciones permitidas para ese usuario en ese estado (los calcula el backend con la máquina de estados).
- **Estados con color consistente** en toda la aplicación (badge) y prioridad con indicador de color.
- **Vencidas resaltadas en rojo** para priorizar la atención.

## 3.7 Patrones de diseño

### Patrón 1 — State (comportamiento)

**Problema:** el comportamiento de una solicitud cambia según su estado: qué transiciones admite, quién puede ejecutarlas, qué datos exige y qué efecto tienen (p. ej. registrar fecha de cierre). Con condicionales (`if estado == ... and rol == ...`) esa lógica se reparte por todo el código y es fácil romper una regla al agregar otra.

**Solución:** cada estado es una clase (`Registrada`, `Asignada`, `EnProceso`, `Resuelta`, `Cerrada`, `Rechazada`, `Reabierta`) que hereda de `EstadoBase` y declara sus transiciones como objetos `ReglaTransicion`. `SolicitudService` (el contexto) obtiene el objeto del estado actual con `estado_de(codigo)` y le delega la validación y los efectos.

**Beneficios en este proyecto:**

- Las reglas RN05, RN06, RN10 y RN11 están en un único archivo (`backend/app/domain/estados.py`) que se lee casi como la tabla de transiciones del análisis.
- La interfaz no repite reglas: el backend devuelve `permisos.transiciones` y el frontend solo dibuja esos botones.
- Agregar un estado nuevo (p. ej. *EN ESPERA DE INFORMACIÓN*) = una clase nueva y su registro, sin tocar el servicio.
- Es fácil de probar de forma aislada (pruebas unitarias parametrizadas de transiciones inválidas).

### Patrón 2 — Observer (comportamiento)

**Problema:** al registrar, asignar, cambiar de estado u observar una solicitud hay que avisar a distintas personas por distintos canales (notificación interna y, opcionalmente, correo). Si `SolicitudService` llamara directamente a cada canal, quedaría acoplado a todos ellos.

**Solución:** `SolicitudService` publica un `Evento` en `PublicadorEventos`; los observadores suscritos (`NotificacionInternaObserver`, `CorreoObserver`) reaccionan de forma independiente. El evento calcula sus destinatarios únicos y excluye al actor.

**Beneficios:** el servicio no conoce los canales; el correo se activa por parámetro sin cambiar código; agregar SMS o Teams es crear otro observador; un fallo del correo no afecta la transacción (el observador captura el error).

### Patrón 3 — Repository (acceso a datos)

**Problema:** mezclar consultas SQL con reglas de negocio dificulta las pruebas y el cambio de motor de BD.

**Solución:** `BaseRepository<T>` con operaciones genéricas y repositorios específicos (`SolicitudRepository.buscar(filtro)`, `conteo_por(columna, filtro)`, `UsuarioRepository.por_email`, …). Los servicios piden datos a los repositorios.

**Beneficios:** el mismo código corre en PostgreSQL y SQLite (las pruebas usan SQLite en memoria); los filtros de búsqueda se definen una sola vez (`FiltroSolicitudes`) y los reutilizan el listado, los reportes y la exportación CSV.

### Otros patrones y principios aplicados

- **Inyección de dependencias** (FastAPI `Depends`): la sesión de BD, el usuario autenticado y la verificación de roles se inyectan en cada endpoint; en las pruebas se reemplaza la BD con `dependency_overrides`.
- **Fábrica simple / registro**: `estado_de(codigo)` devuelve la instancia del estado correspondiente.
- **DTO** (Pydantic): separa lo que entra/sale por la API de las entidades persistentes (nunca se expone `password_hash`).
- **SOLID**: responsabilidad única por servicio; abierto/cerrado en estados y observadores; inversión de dependencias en servicios → repositorios.
