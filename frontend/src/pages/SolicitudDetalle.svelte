<script>
  import { link } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { avisar, sesion } from '../lib/stores.js'
  import { CANALES, ESTADOS, PRIORIDADES, TIPOS_MOV, fecha, iniciales, relativo } from '../lib/formato.js'
  import EstadoBadge from '../components/EstadoBadge.svelte'
  import PrioridadBadge from '../components/PrioridadBadge.svelte'
  import Modal from '../components/Modal.svelte'

  export let id
  let s = null
  let error = ''
  $: rol = $sesion.rol.codigo
  $: esPersonal = rol !== 'ESTUDIANTE'

  async function cargar() {
    try {
      s = await api(`/solicitudes/${id}`)
      error = ''
    } catch (e) {
      error = e.message
    }
  }
  $: id, cargar()

  // ---- cambio de estado
  let trans = null
  let modalTrans = false
  let comentario = ''
  let solucion = ''
  let enviando = false
  function abrirTransicion(t) { trans = t; comentario = ''; solucion = ''; modalTrans = true }
  async function aplicarTransicion() {
    enviando = true
    try {
      await api(`/solicitudes/${id}/estado`, { method: 'POST', body: { estado: trans.estado, comentario: comentario || null, solucion: solucion || null } })
      avisar(`Solicitud actualizada a «${ESTADOS[trans.estado].etiqueta}»`)
      modalTrans = false
      await cargar()
    } catch (e) { avisar(e.message, 'error') } finally { enviando = false }
  }

  // ---- asignación
  let modalAsignar = false
  let funcionarios = []
  let asig = { responsable_id: '', comentario: '' }
  async function abrirAsignar() {
    funcionarios = await api('/usuarios/funcionarios').catch(() => [])
    asig = { responsable_id: '', comentario: '' }
    modalAsignar = true
  }
  async function asignar() {
    enviando = true
    try {
      await api(`/solicitudes/${id}/asignar`, { method: 'POST', body: { responsable_id: +asig.responsable_id, comentario: asig.comentario || null } })
      avisar('Responsable asignado'); modalAsignar = false; await cargar()
    } catch (e) { avisar(e.message, 'error') } finally { enviando = false }
  }

  // ---- edición
  let modalEditar = false
  let categorias = []
  let ed = {}
  $: editaTexto = s && s.solicitante.id === $sesion.id && s.estado === 'REGISTRADA'
  async function abrirEditar() {
    categorias = await api('/categorias').catch(() => [])
    ed = { asunto: s.asunto, descripcion: s.descripcion, categoria_id: s.categoria.id, prioridad: s.prioridad }
    modalEditar = true
  }
  async function guardarEdicion() {
    const body = editaTexto ? { ...ed, categoria_id: +ed.categoria_id } : { categoria_id: +ed.categoria_id, prioridad: ed.prioridad }
    try {
      await api(`/solicitudes/${id}`, { method: 'PATCH', body })
      avisar('Cambios guardados'); modalEditar = false; await cargar()
    } catch (e) { avisar(e.message, 'error') }
  }

  // ---- observaciones
  let obs = ''
  let interna = false
  async function agregarObs() {
    try {
      await api(`/solicitudes/${id}/observaciones`, { method: 'POST', body: { texto: obs, interna } })
      obs = ''; interna = false; await cargar()
    } catch (e) { avisar(e.message, 'error') }
  }

  const colorTrans = (e) => (e === 'RECHAZADA' ? 'btn-peligro' : e === 'REABIERTA' ? 'btn-secundario' : 'btn-primario')
  function descMov(m) {
    if (m.tipo === 'ASIGNACION')
      return m.responsable_anterior ? `Reasignada de ${m.responsable_anterior.nombre_completo} a ${m.responsable_nuevo?.nombre_completo}` : `Asignada a ${m.responsable_nuevo?.nombre_completo}`
    if (m.tipo === 'CAMBIO_ESTADO') return `${ESTADOS[m.estado_anterior]?.etiqueta} → ${ESTADOS[m.estado_nuevo]?.etiqueta}`
    return TIPOS_MOV[m.tipo]
  }
</script>

<a href="/solicitudes" use:link class="btn-volver group mb-4">
  <span class="btn-volver-icono">
    <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
  </span>
  Volver al listado
</a>

{#if error}
  <div class="tarjeta p-8 text-center text-slate-600">{error}</div>
{:else if !s}
  <p class="text-slate-400">Cargando…</p>
{:else}
  <div class="mb-6 flex flex-wrap items-start justify-between gap-4">
    <div class="min-w-0">
      <div class="flex flex-wrap items-center gap-3">
        <span class="font-mono text-sm text-slate-500">{s.codigo}</span>
        <EstadoBadge estado={s.estado} />
        <PrioridadBadge prioridad={s.prioridad} />
        {#if s.vencida}<span class="rounded-full bg-rose-600 px-2 py-0.5 text-xs font-semibold text-white">Vencida</span>{/if}
      </div>
      <h1 class="mt-2 text-2xl font-semibold text-slate-900">{s.asunto}</h1>
    </div>
    <div class="flex flex-wrap gap-2">
      {#if s.permisos.puede_editar}<button class="btn-secundario" on:click={abrirEditar}>Editar</button>{/if}
      {#if s.permisos.puede_asignar}<button class="btn-secundario" on:click={abrirAsignar}>{s.responsable ? 'Reasignar' : 'Asignar responsable'}</button>{/if}
      {#each s.permisos.transiciones as t}
        <button class={colorTrans(t.estado)} on:click={() => abrirTransicion(t)}>{t.etiqueta}</button>
      {/each}
    </div>
  </div>

  <div class="grid gap-6 lg:grid-cols-3">
    <div class="space-y-6 lg:col-span-2">
      <section class="tarjeta p-5">
        <h2 class="etiqueta">Descripción</h2>
        <p class="whitespace-pre-line text-sm leading-relaxed text-slate-700">{s.descripcion}</p>
        {#if s.solucion}
          <div class="mt-5 rounded-lg border border-brand-200 bg-brand-50 p-4">
            <h3 class="text-xs font-semibold uppercase tracking-wide text-brand-800">Solución aplicada</h3>
            <p class="mt-1 whitespace-pre-line text-sm text-brand-900">{s.solucion}</p>
          </div>
        {/if}
      </section>

      <section class="tarjeta">
        <h2 class="border-b border-slate-100 px-5 py-3 font-semibold text-slate-900">Observaciones ({s.observaciones.length})</h2>
        <ul class="divide-y divide-slate-50">
          {#each s.observaciones as o}
            <li class="flex gap-3 px-5 py-4">
              <div class="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-slate-100 text-xs font-semibold text-slate-600">{iniciales(o.autor.nombre_completo)}</div>
              <div class="min-w-0">
                <p class="text-sm"><span class="font-medium text-slate-800">{o.autor.nombre_completo}</span>
                  <span class="ml-2 text-xs text-slate-400">{relativo(o.fecha)}</span>
                  {#if o.interna}<span class="ml-2 rounded bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-amber-800">Interna</span>{/if}</p>
                <p class="mt-1 whitespace-pre-line text-sm text-slate-600">{o.texto}</p>
              </div>
            </li>
          {:else}
            <li class="px-5 py-6 text-center text-sm text-slate-400">Aún no hay observaciones.</li>
          {/each}
        </ul>
        {#if s.permisos.puede_observar}
          <form class="border-t border-slate-100 p-4" on:submit|preventDefault={agregarObs}>
            <textarea class="campo" rows="2" bind:value={obs} placeholder="Escriba una observación…" minlength="2" required></textarea>
            <div class="mt-2 flex items-center justify-between">
              {#if esPersonal}
                <label class="flex items-center gap-2 text-xs text-slate-600"><input type="checkbox" bind:checked={interna} class="rounded" /> Nota interna (no la ve el estudiante)</label>
              {:else}<span></span>{/if}
              <button class="btn-primario py-1.5">Agregar</button>
            </div>
          </form>
        {:else}
          <p class="border-t border-slate-100 px-5 py-3 text-xs text-slate-500">La solicitud está {ESTADOS[s.estado].etiqueta.toLowerCase()}: no admite nuevas observaciones.</p>
        {/if}
      </section>
    </div>

    <div class="space-y-6">
      <section class="tarjeta p-5">
        <dl class="space-y-3 text-sm">
          {#each [
            ['Solicitante', s.solicitante.nombre_completo],
            ['Categoría', s.categoria.nombre],
            ['Responsable', s.responsable?.nombre_completo || 'Sin asignar'],
            ['Canal', CANALES[s.canal]],
            ['Registro', fecha(s.fecha_registro)],
            ['Fecha límite', fecha(s.fecha_limite)],
            ['Resolución', fecha(s.fecha_resolucion)],
            ['Cierre', fecha(s.fecha_cierre)]
          ] as [k, v]}
            <div class="flex justify-between gap-4"><dt class="text-slate-500">{k}</dt><dd class="text-right font-medium text-slate-800">{v}</dd></div>
          {/each}
        </dl>
      </section>

      <section class="tarjeta p-5">
        <h2 class="mb-4 font-semibold text-slate-900">Historial</h2>
        <ol class="relative ml-2 border-l border-slate-200">
          {#each [...s.movimientos].reverse() as m}
            <li class="mb-5 ml-4">
              <span class="absolute -left-1.5 mt-1.5 h-3 w-3 rounded-full border-2 border-white {m.tipo === 'CAMBIO_ESTADO' ? 'bg-brand-600' : m.tipo === 'ASIGNACION' ? 'bg-brand-500' : 'bg-slate-300'}"></span>
              <p class="text-xs text-slate-400">{fecha(m.fecha)}</p>
              <p class="text-sm font-medium text-slate-800">{descMov(m)}</p>
              <p class="text-xs text-slate-500">por {m.usuario.nombre_completo}</p>
              {#if m.detalle && m.tipo !== 'REGISTRO'}<p class="mt-1 line-clamp-3 whitespace-pre-line text-xs text-slate-600">{m.detalle}</p>{/if}
            </li>
          {/each}
        </ol>
      </section>
    </div>
  </div>
{/if}

<Modal titulo={trans ? trans.etiqueta : ''} bind:abierto={modalTrans}>
  {#if trans}
    <form class="space-y-4" on:submit|preventDefault={aplicarTransicion}>
      <p class="text-sm text-slate-600">La solicitud pasará de <EstadoBadge estado={s.estado} /> a <EstadoBadge estado={trans.estado} />.</p>
      {#if trans.requiere_solucion}
        <div>
          <label class="etiqueta" for="sol">Solución aplicada *</label>
          <textarea id="sol" class="campo" rows="4" bind:value={solucion} required placeholder="Describa cómo se resolvió la solicitud"></textarea>
        </div>
      {/if}
      <div>
        <label class="etiqueta" for="com">{trans.requiere_motivo ? 'Motivo *' : 'Observación (opcional)'}</label>
        <textarea id="com" class="campo" rows="3" bind:value={comentario} required={trans.requiere_motivo}></textarea>
      </div>
      <div class="flex justify-end gap-2">
        <button type="button" class="btn-secundario" on:click={() => (modalTrans = false)}>Cancelar</button>
        <button class={colorTrans(trans.estado)} disabled={enviando}>Confirmar</button>
      </div>
    </form>
  {/if}
</Modal>

<Modal titulo="Asignar responsable" bind:abierto={modalAsignar}>
  <form class="space-y-4" on:submit|preventDefault={asignar}>
    <div>
      <label class="etiqueta" for="resp">Funcionario *</label>
      <select id="resp" class="campo" bind:value={asig.responsable_id} required>
        <option value="" disabled>Seleccione…</option>
        {#each funcionarios.filter((f) => f.id !== s?.responsable?.id) as f}<option value={f.id}>{f.nombre_completo} · {f.email}</option>{/each}
      </select>
    </div>
    <div><label class="etiqueta" for="ac">Comentario</label><textarea id="ac" class="campo" rows="2" bind:value={asig.comentario}></textarea></div>
    <div class="flex justify-end gap-2">
      <button type="button" class="btn-secundario" on:click={() => (modalAsignar = false)}>Cancelar</button>
      <button class="btn-primario" disabled={enviando}>Asignar</button>
    </div>
  </form>
</Modal>

<Modal titulo="Editar solicitud" bind:abierto={modalEditar}>
  <form class="space-y-4" on:submit|preventDefault={guardarEdicion}>
    {#if editaTexto}
      <div><label class="etiqueta" for="ea">Asunto</label><input id="ea" class="campo" bind:value={ed.asunto} minlength="5" required /></div>
      <div><label class="etiqueta" for="ed">Descripción</label><textarea id="ed" class="campo" rows="4" bind:value={ed.descripcion} minlength="10" required></textarea></div>
    {/if}
    <div class="grid grid-cols-2 gap-4">
      <div>
        <label class="etiqueta" for="ec">Categoría</label>
        <select id="ec" class="campo" bind:value={ed.categoria_id}>{#each categorias as c}<option value={c.id}>{c.nombre}</option>{/each}</select>
      </div>
      <div>
        <label class="etiqueta" for="ep">Prioridad</label>
        <select id="ep" class="campo" bind:value={ed.prioridad}>{#each Object.entries(PRIORIDADES) as [k, p]}<option value={k}>{p.etiqueta}</option>{/each}</select>
      </div>
    </div>
    <div class="flex justify-end gap-2">
      <button type="button" class="btn-secundario" on:click={() => (modalEditar = false)}>Cancelar</button>
      <button class="btn-primario">Guardar</button>
    </div>
  </form>
</Modal>
