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

<div class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
  {#each lista as c}
    <div class="tarjeta flex flex-col p-5 {c.activa ? '' : 'opacity-60'}">
      <div class="flex items-start justify-between gap-2">
        <h3 class="font-semibold text-slate-900">{c.nombre}</h3>
        <span class="rounded-full px-2 py-0.5 text-xs {c.activa ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-500'}">{c.activa ? 'Activa' : 'Inactiva'}</span>
      </div>
      <p class="mt-1 flex-1 text-sm text-slate-500">{c.descripcion || 'Sin descripción'}</p>
      <div class="mt-4 flex items-center justify-between text-xs text-slate-500">
        <span>{c.dependencia || '—'} · {c.tiempo_respuesta_horas} h</span>
        <span class="flex gap-1">
          <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => abrir(c)}>Editar</button>
          <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => alternar(c)}>{c.activa ? 'Desactivar' : 'Activar'}</button>
        </span>
      </div>
    </div>
  {/each}
</div>

<Modal titulo={editando ? 'Editar categoría' : 'Nueva categoría'} bind:abierto={modal}>
  <form class="space-y-4" on:submit|preventDefault={guardar}>
    <div><label class="etiqueta" for="cn">Nombre *</label><input id="cn" class="campo" bind:value={form.nombre} minlength="3" required /></div>
    <div><label class="etiqueta" for="cd">Descripción</label><textarea id="cd" class="campo" rows="2" bind:value={form.descripcion}></textarea></div>
    <div class="grid grid-cols-2 gap-4">
      <div><label class="etiqueta" for="cdep">Dependencia responsable</label><input id="cdep" class="campo" bind:value={form.dependencia} /></div>
      <div><label class="etiqueta" for="ct">Tiempo de respuesta (horas) *</label><input id="ct" type="number" min="1" max="2160" class="campo" bind:value={form.tiempo_respuesta_horas} required /></div>
    </div>
    <div class="flex justify-end gap-2"><button type="button" class="btn-secundario" on:click={() => (modal = false)}>Cancelar</button><button class="btn-primario">Guardar</button></div>
  </form>
</Modal>
