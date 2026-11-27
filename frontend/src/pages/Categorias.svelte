<script>
  import { onMount } from 'svelte'
  import { api } from '../lib/api.js'
  import { avisar } from '../lib/stores.js'
  import Encabezado from '../components/Encabezado.svelte'
  import Modal from '../components/Modal.svelte'

  let lista = []
  let modal = false
  let editando = null
  let form = {}
  const cargar = async () => (lista = await api('/categorias?todas=true').catch(() => []))
  onMount(cargar)

  function abrir(c = null) {
    editando = c
    form = c ? { nombre: c.nombre, descripcion: c.descripcion || '', dependencia: c.dependencia || '', tiempo_respuesta_horas: c.tiempo_respuesta_horas }
             : { nombre: '', descripcion: '', dependencia: '', tiempo_respuesta_horas: 72 }
    modal = true
  }
  async function guardar() {
    try {
      const body = { ...form, tiempo_respuesta_horas: +form.tiempo_respuesta_horas }
      await api(editando ? `/categorias/${editando.id}` : '/categorias', { method: editando ? 'PUT' : 'POST', body })
      avisar('Categoría guardada'); modal = false; cargar()
    } catch (e) { avisar(e.message, 'error') }
  }
  async function alternar(c) {
    await api(`/categorias/${c.id}/activa`, { method: 'PATCH', body: { activo: !c.activa } }).catch((e) => avisar(e.message, 'error'))
    cargar()
  }
</script>

<Encabezado titulo="Categorías de solicitud" subtitulo="Tipos de servicio, dependencia responsable y tiempo de respuesta (SLA)">
  <button class="btn-primario" on:click={() => abrir()}>+ Nueva categoría</button>
</Encabezado>

<div class="mb-3 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">
  <span class="h-1.5 w-1.5 rounded-full bg-brand-500"></span>
  Catálogo · {lista.length} categoría(s)
</div>

<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {#each lista as c}
    <div class="tarjeta-destacada group relative flex flex-col overflow-hidden p-5 {c.activa ? '' : 'opacity-70'}">
      <span class="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-brand-500/10 blur-2xl transition duration-500 group-hover:bg-brand-500/20"></span>
      <div class="relative flex items-start justify-between gap-3">
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600 ring-1 ring-brand-100">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
        </span>
        <span class="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium ring-1 {c.activa ? 'bg-brand-50 text-brand-700 ring-brand-100' : 'bg-slate-100 text-slate-500 ring-slate-200'}">{c.activa ? 'Activa' : 'Inactiva'}</span>
      </div>
      <h3 class="relative mt-3 font-semibold leading-snug text-slate-900">{c.nombre}</h3>
      <p class="relative mt-0.5 truncate text-xs text-slate-500">{c.dependencia || 'Sin dependencia asignada'}</p>
      <p class="relative mt-3 flex-1 text-sm leading-relaxed text-slate-600">{c.descripcion || 'Sin descripción'}</p>
      <div class="relative mt-4 flex flex-wrap items-center justify-between gap-2 border-t border-white/70 pt-3">
        <span class="inline-flex items-center gap-1.5 rounded-full bg-white/70 px-2.5 py-1 text-xs font-medium text-slate-600 ring-1 ring-slate-200/70">
          <svg class="h-3.5 w-3.5 text-brand-600" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"/></svg>
          SLA {c.tiempo_respuesta_horas} h
        </span>
        <span class="flex gap-1">
          <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => abrir(c)}>Editar</button>
          <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => alternar(c)}>{c.activa ? 'Desactivar' : 'Activar'}</button>
        </span>
      </div>
    </div>
  {:else}
    <div class="panel sm:col-span-2 lg:col-span-3">
      <div class="panel-vacio">
        <span class="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-500 ring-1 ring-brand-100">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/></svg>
        </span>
        <div>
          <p class="text-sm font-medium text-slate-700">Aún no hay categorías</p>
          <p class="mt-1 text-xs text-slate-500">Cree la primera categoría para clasificar las solicitudes.</p>
        </div>
      </div>
    </div>
  {/each}
</div>

<Modal titulo={editando ? 'Editar categoría' : 'Nueva categoría'} bind:abierto={modal}>
  <form class="space-y-4" on:submit|preventDefault={guardar}>
    <div><label class="etiqueta" for="cn">Nombre *</label><input id="cn" class="campo" bind:value={form.nombre} minlength="3" required /></div>
    <div><label class="etiqueta" for="cd">Descripción</label><textarea id="cd" class="campo" rows="2" bind:value={form.descripcion}></textarea></div>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div><label class="etiqueta" for="cdep">Dependencia responsable</label><input id="cdep" class="campo" bind:value={form.dependencia} /></div>
      <div><label class="etiqueta" for="ct">Tiempo de respuesta (horas) *</label><input id="ct" type="number" min="1" max="2160" class="campo" bind:value={form.tiempo_respuesta_horas} required /></div>
    </div>
    <div class="flex justify-end gap-2"><button type="button" class="btn-secundario" on:click={() => (modal = false)}>Cancelar</button><button class="btn-primario">Guardar</button></div>
  </form>
</Modal>
