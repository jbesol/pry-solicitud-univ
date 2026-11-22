-- Esquema relacional del Sistema de Gestión de Solicitudes Universitarias (PostgreSQL)
-- Generado desde los modelos SQLAlchemy (app/models/entities.py). La aplicación lo crea automáticamente al iniciar.


-- Name: categorias; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.categorias (
    id integer NOT NULL,
    nombre character varying(80) NOT NULL,
    descripcion character varying(255),
    dependencia character varying(100),
    tiempo_respuesta_horas integer NOT NULL,
    activa boolean NOT NULL,
    CONSTRAINT ck_categoria_tiempo CHECK ((tiempo_respuesta_horas > 0))
);

-- Name: categorias_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.categorias_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: categorias_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.categorias_id_seq OWNED BY public.categorias.id;

-- Name: movimientos; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.movimientos (
    id integer NOT NULL,
    solicitud_id integer NOT NULL,
    usuario_id integer NOT NULL,
    tipo character varying(20) NOT NULL,
    estado_anterior character varying(20),
    estado_nuevo character varying(20),
    responsable_anterior_id integer,
    responsable_nuevo_id integer,
    detalle text,
    interno boolean NOT NULL,
    fecha timestamp without time zone NOT NULL,
    CONSTRAINT ck_estado_ant CHECK (((estado_anterior)::text = ANY ((ARRAY['REGISTRADA'::character varying, 'ASIGNADA'::character varying, 'EN_PROCESO'::character varying, 'RESUELTA'::character varying, 'CERRADA'::character varying, 'RECHAZADA'::character varying, 'REABIERTA'::character varying])::text[]))),
    CONSTRAINT ck_estado_nue CHECK (((estado_nuevo)::text = ANY ((ARRAY['REGISTRADA'::character varying, 'ASIGNADA'::character varying, 'EN_PROCESO'::character varying, 'RESUELTA'::character varying, 'CERRADA'::character varying, 'RECHAZADA'::character varying, 'REABIERTA'::character varying])::text[]))),
    CONSTRAINT ck_tipo_movimiento CHECK (((tipo)::text = ANY ((ARRAY['REGISTRO'::character varying, 'ASIGNACION'::character varying, 'CAMBIO_ESTADO'::character varying, 'OBSERVACION'::character varying, 'EDICION'::character varying])::text[])))
);

-- Name: movimientos_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.movimientos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: movimientos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.movimientos_id_seq OWNED BY public.movimientos.id;

-- Name: notificaciones; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.notificaciones (
    id integer NOT NULL,
    usuario_id integer NOT NULL,
    solicitud_id integer,
    tipo character varying(20) NOT NULL,
    titulo character varying(150) NOT NULL,
    mensaje text NOT NULL,
    leida boolean NOT NULL,
    fecha timestamp without time zone NOT NULL,
    CONSTRAINT ck_tipo_evento CHECK (((tipo)::text = ANY ((ARRAY['SOLICITUD_REGISTRADA'::character varying, 'SOLICITUD_ASIGNADA'::character varying, 'ESTADO_ACTUALIZADO'::character varying, 'OBSERVACION_AGREGADA'::character varying])::text[])))
);

-- Name: notificaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.notificaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: notificaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.notificaciones_id_seq OWNED BY public.notificaciones.id;

-- Name: observaciones; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.observaciones (
    id integer NOT NULL,
    solicitud_id integer NOT NULL,
    autor_id integer NOT NULL,
    texto text NOT NULL,
    interna boolean NOT NULL,
    fecha timestamp without time zone NOT NULL
);

-- Name: observaciones_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.observaciones_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: observaciones_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.observaciones_id_seq OWNED BY public.observaciones.id;

-- Name: parametros; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.parametros (
    clave character varying(50) NOT NULL,
    valor character varying(255) NOT NULL,
    descripcion character varying(255)
);

-- Name: roles; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.roles (
    id integer NOT NULL,
    codigo character varying(20) NOT NULL,
    nombre character varying(50) NOT NULL,
    descripcion character varying(255),
    CONSTRAINT ck_rol_codigo CHECK (((codigo)::text = ANY ((ARRAY['ADMINISTRADOR'::character varying, 'ESTUDIANTE'::character varying, 'FUNCIONARIO'::character varying, 'SUPERVISOR'::character varying])::text[])))
);

-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;

-- Name: solicitudes; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.solicitudes (
    id integer NOT NULL,
    codigo character varying(30),
    asunto character varying(150) NOT NULL,
    descripcion text NOT NULL,
    prioridad character varying(20) NOT NULL,
    canal character varying(20) NOT NULL,
    estado character varying(20) NOT NULL,
    solucion text,
    solicitante_id integer NOT NULL,
    categoria_id integer NOT NULL,
    responsable_id integer,
    fecha_registro timestamp without time zone NOT NULL,
    fecha_actualizacion timestamp without time zone NOT NULL,
    fecha_limite timestamp without time zone,
    fecha_resolucion timestamp without time zone,
    fecha_cierre timestamp without time zone,
    CONSTRAINT ck_canal CHECK (((canal)::text = ANY ((ARRAY['WEB'::character varying, 'CORREO'::character varying, 'PRESENCIAL'::character varying, 'MENSAJERIA'::character varying])::text[]))),
    CONSTRAINT ck_estado_solicitud CHECK (((estado)::text = ANY ((ARRAY['REGISTRADA'::character varying, 'ASIGNADA'::character varying, 'EN_PROCESO'::character varying, 'RESUELTA'::character varying, 'CERRADA'::character varying, 'RECHAZADA'::character varying, 'REABIERTA'::character varying])::text[]))),
    CONSTRAINT ck_prioridad CHECK (((prioridad)::text = ANY ((ARRAY['BAJA'::character varying, 'MEDIA'::character varying, 'ALTA'::character varying, 'URGENTE'::character varying])::text[])))
);

-- Name: solicitudes_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.solicitudes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: solicitudes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.solicitudes_id_seq OWNED BY public.solicitudes.id;

-- Name: usuarios; Type: TABLE; Schema: public; Owner: -

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    documento character varying(20) NOT NULL,
    nombres character varying(80) NOT NULL,
    apellidos character varying(80) NOT NULL,
    email character varying(120) NOT NULL,
    password_hash character varying(255) NOT NULL,
    telefono character varying(20),
    dependencia character varying(100),
    rol_id integer NOT NULL,
    activo boolean NOT NULL,
    fecha_creacion timestamp without time zone NOT NULL
);

-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: -

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;

-- Name: categorias id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.categorias ALTER COLUMN id SET DEFAULT nextval('public.categorias_id_seq'::regclass);

-- Name: movimientos id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.movimientos ALTER COLUMN id SET DEFAULT nextval('public.movimientos_id_seq'::regclass);

-- Name: notificaciones id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificaciones ALTER COLUMN id SET DEFAULT nextval('public.notificaciones_id_seq'::regclass);

-- Name: observaciones id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.observaciones ALTER COLUMN id SET DEFAULT nextval('public.observaciones_id_seq'::regclass);

-- Name: roles id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);

-- Name: solicitudes id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.solicitudes ALTER COLUMN id SET DEFAULT nextval('public.solicitudes_id_seq'::regclass);

-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: -

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);

-- Name: categorias categorias_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_nombre_key UNIQUE (nombre);

-- Name: categorias categorias_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.categorias
    ADD CONSTRAINT categorias_pkey PRIMARY KEY (id);

-- Name: movimientos movimientos_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_pkey PRIMARY KEY (id);

-- Name: notificaciones notificaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_pkey PRIMARY KEY (id);

-- Name: observaciones observaciones_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT observaciones_pkey PRIMARY KEY (id);

-- Name: parametros parametros_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.parametros
    ADD CONSTRAINT parametros_pkey PRIMARY KEY (clave);

-- Name: roles roles_codigo_key; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_codigo_key UNIQUE (codigo);

-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);

-- Name: solicitudes solicitudes_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.solicitudes
    ADD CONSTRAINT solicitudes_pkey PRIMARY KEY (id);

-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);

-- Name: ix_movimientos_fecha; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_movimientos_fecha ON public.movimientos USING btree (fecha);

-- Name: ix_movimientos_solicitud_id; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_movimientos_solicitud_id ON public.movimientos USING btree (solicitud_id);

-- Name: ix_notificaciones_leida; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_notificaciones_leida ON public.notificaciones USING btree (leida);

-- Name: ix_notificaciones_usuario_id; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_notificaciones_usuario_id ON public.notificaciones USING btree (usuario_id);

-- Name: ix_observaciones_solicitud_id; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_observaciones_solicitud_id ON public.observaciones USING btree (solicitud_id);

-- Name: ix_solicitudes_categoria_id; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_solicitudes_categoria_id ON public.solicitudes USING btree (categoria_id);

-- Name: ix_solicitudes_codigo; Type: INDEX; Schema: public; Owner: -

CREATE UNIQUE INDEX ix_solicitudes_codigo ON public.solicitudes USING btree (codigo);

-- Name: ix_solicitudes_estado; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_solicitudes_estado ON public.solicitudes USING btree (estado);

-- Name: ix_solicitudes_fecha_registro; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_solicitudes_fecha_registro ON public.solicitudes USING btree (fecha_registro);

-- Name: ix_solicitudes_responsable_id; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_solicitudes_responsable_id ON public.solicitudes USING btree (responsable_id);

-- Name: ix_solicitudes_solicitante_id; Type: INDEX; Schema: public; Owner: -

CREATE INDEX ix_solicitudes_solicitante_id ON public.solicitudes USING btree (solicitante_id);

-- Name: ix_usuarios_documento; Type: INDEX; Schema: public; Owner: -

CREATE UNIQUE INDEX ix_usuarios_documento ON public.usuarios USING btree (documento);

-- Name: ix_usuarios_email; Type: INDEX; Schema: public; Owner: -

CREATE UNIQUE INDEX ix_usuarios_email ON public.usuarios USING btree (email);

-- Name: movimientos movimientos_responsable_anterior_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_responsable_anterior_id_fkey FOREIGN KEY (responsable_anterior_id) REFERENCES public.usuarios(id);

-- Name: movimientos movimientos_responsable_nuevo_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_responsable_nuevo_id_fkey FOREIGN KEY (responsable_nuevo_id) REFERENCES public.usuarios(id);

-- Name: movimientos movimientos_solicitud_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_solicitud_id_fkey FOREIGN KEY (solicitud_id) REFERENCES public.solicitudes(id) ON DELETE CASCADE;

-- Name: movimientos movimientos_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.movimientos
    ADD CONSTRAINT movimientos_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id);

-- Name: notificaciones notificaciones_solicitud_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_solicitud_id_fkey FOREIGN KEY (solicitud_id) REFERENCES public.solicitudes(id) ON DELETE CASCADE;

-- Name: notificaciones notificaciones_usuario_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.notificaciones
    ADD CONSTRAINT notificaciones_usuario_id_fkey FOREIGN KEY (usuario_id) REFERENCES public.usuarios(id) ON DELETE CASCADE;

-- Name: observaciones observaciones_autor_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT observaciones_autor_id_fkey FOREIGN KEY (autor_id) REFERENCES public.usuarios(id);

-- Name: observaciones observaciones_solicitud_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.observaciones
    ADD CONSTRAINT observaciones_solicitud_id_fkey FOREIGN KEY (solicitud_id) REFERENCES public.solicitudes(id) ON DELETE CASCADE;

-- Name: solicitudes solicitudes_categoria_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.solicitudes
    ADD CONSTRAINT solicitudes_categoria_id_fkey FOREIGN KEY (categoria_id) REFERENCES public.categorias(id);

-- Name: solicitudes solicitudes_responsable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.solicitudes
    ADD CONSTRAINT solicitudes_responsable_id_fkey FOREIGN KEY (responsable_id) REFERENCES public.usuarios(id);

-- Name: solicitudes solicitudes_solicitante_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.solicitudes
    ADD CONSTRAINT solicitudes_solicitante_id_fkey FOREIGN KEY (solicitante_id) REFERENCES public.usuarios(id);

-- Name: usuarios usuarios_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id);

