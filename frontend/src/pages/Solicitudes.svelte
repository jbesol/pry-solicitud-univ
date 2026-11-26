<script>
  import { onMount } from 'svelte'
  import { link, navigate } from 'svelte-routing'
  import { api, qs } from '../lib/api.js'
  import { sesion } from '../lib/stores.js'
  import { ESTADOS, PRIORIDADES, fechaCorta } from '../lib/formato.js'
  import Encabezado from '../components/Encabezado.svelte'
  import EstadoBadge from '../components/EstadoBadge.svelte'
  import PrioridadBadge from '../components/PrioridadBadge.svelte'
  import NuevaSolicitud from '../components/NuevaSolicitud.svelte'

  $: rol = $sesion.rol.codigo
  $: esStaff = ['ADMINISTRADOR', 'SUPERVISOR'].includes(rol)
  $: puedeRegistrar = ['ESTUDIANTE', 'FUNCIONARIO'].includes(rol)

  let lista = []
  let categorias = []
  let funcionarios = []
  let cargando = true
  let modalNueva = false
  let f = { q: '', estado: '', categoria_id: '', prioridad: '', responsable_id: '', desde: '', hasta: '', alcance: '' }

  async function cargar() {
    cargando = true
    try {
      lista = await api('/solicitudes' + qs(f))
    } catch {
      lista = []
    }
    cargando = false
  }
  onMount(async () => {
    categorias = await api('/categorias').catch(() => [])
    if (esStaff) funcionarios = await api('/usuarios/funcionarios').catch(() => [])
    cargar()
  })
  let t
  const buscarDiferido = () => { clearTimeout(t); t = setTimeout(cargar, 300) }
  function limpiar() {
    f = { q: '', estado: '', categoria_id: '', prioridad: '', responsable_id: '', desde: '', hasta: '', alcance: f.alcance }
    cargar()
  }
  $: titulo = rol === 'ESTUDIANTE' ? 'Mis solicitudes' : rol === 'FUNCIONARIO' ? (f.alcance === 'propias' ? 'Solicitudes que registré' : 'Solicitudes asignadas a mí') : 'Todas las solicitudes'
</script>

<Encabezado {titulo} subtitulo={rol === 'ESTUDIANTE' ? 'Consulte el avance de sus casos y registre nuevas solicitudes' : rol === 'FUNCIONARIO' ? 'Gestione las solicitudes bajo su responsabilidad' : 'Supervise, asigne y haga seguimiento a las solicitudes'}>
  {#if puedeRegistrar}<button class="btn-primario" on:click={() => (modalNueva = true)}>+ Nueva solicitud</button>{/if}
</Encabezado>

{#if rol === 'FUNCIONARIO'}
  <div class="mb-4 inline-flex rounded-xl border border-white/70 bg-white/60 p-1 text-sm shadow-sm shadow-brand-900/5 backdrop-blur-md">
    {#each [['', 'Asignadas a mí'], ['propias', 'Registradas por mí']] as [v, txt]}
      <button class="rounded-lg px-3 py-1.5 transition {f.alcance === v ? 'bg-gradient-to-b from-brand-500 to-brand-600 text-white shadow' : 'text-slate-600 hover:bg-white/70'}" on:click={() => { f.alcance = v; cargar() }}>{txt}</button>
    {/each}
  </div>
{/if}

<div class="panel mb-4">
  <div class="panel-cabecera">
    <div class="panel-titulo">
      <span class="panel-icono">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 5h18M6 12h12M10 19h4"/></svg>
      </span>
      Filtros
      {#if !cargando}<span class="chip-conteo">{lista.length}</span>{/if}
    </div>
    <button class="btn-fantasma px-3 py-1.5 text-xs" on:click={limpiar}>
      <svg class="h-3.5 w-3.5" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 4v6h6M20 20v-6h-6M20 9A8 8 0 0 0 5.6 5.6L4 8m16 8-1.6 2.4A8 8 0 0 1 4 15"/></svg>
      Limpiar filtros
    </button>
  </div>
  <div class="grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-6">
    <div class="lg:col-span-2">
      <label class="etiqueta" for="q">Buscar</label>
      <div class="relative">
        <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z"/></svg>
        <input id="q" class="campo pl-9" placeholder="Código, asunto o descripción" bind:value={f.q} on:input={buscarDiferido} />
      </div>
    </div>
    <div>
      <label class="etiqueta" for="fe">Estado</label>
      <select id="fe" class="campo" bind:value={f.estado} on:change={cargar}>
        <option value="">Todos</option>
        {#each Object.entries(ESTADOS) as [k, e]}<option value={k}>{e.etiqueta}</option>{/each}
      </select>
    </div>
    <div>
      <label class="etiqueta" for="fc">Categoría</label>
      <select id="fc" class="campo" bind:value={f.categoria_id} on:change={cargar}>
        <option value="">Todas</option>
        {#each categorias as c}<option value={c.id}>{c.nombre}</option>{/each}
      </select>
    </div>
    <div>
      <label class="etiqueta" for="fp">Prioridad</label>
      <select id="fp" class="campo" bind:value={f.prioridad} on:change={cargar}>
        <option value="">Todas</option>
        {#each Object.entries(PRIORIDADES) as [k, p]}<option value={k}>{p.etiqueta}</option>{/each}
      </select>
    </div>
    {#if esStaff}
      <div>
        <label class="etiqueta" for="fr">Responsable</label>
        <select id="fr" class="campo" bind:value={f.responsable_id} on:change={cargar}>
          <option value="">Todos</option>
          {#each funcionarios as u}<option value={u.id}>{u.nombre_completo}</option>{/each}
        </select>
      </div>
    {/if}
    <div>
      <label class="etiqueta" for="fd">Desde</label>
      <input id="fd" type="date" class="campo" bind:value={f.desde} on:change={cargar} />
    </div>
    <div>
      <label class="etiqueta" for="fh">Hasta</label>
      <input id="fh" type="date" class="campo" bind:value={f.hasta} on:change={cargar} />
    </div>
  </div>
</div>

<div class="panel">
  <div class="panel-cabecera">
    <div class="panel-titulo">
      <span class="panel-icono">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h10"/></svg>
      </span>
      Listado
    </div>
    <span class="text-xs text-slate-500">{cargando ? 'Cargando…' : lista.length >= 500 ? 'Mostrando las 500 más recientes' : `${lista.length} registro(s)`}</span>
  </div>
  <div class="overflow-x-auto">
    <table class="tabla w-full min-w-[780px] table-fixed">
      <thead>
        <tr><th class="w-[13%]">Código</th><th class="w-[31%]">Solicitud</th><th class="w-[12%]">Prioridad</th><th class="w-[13%]">Estado</th><th class="w-[16%]">Responsable</th><th class="w-[15%]">Fechas</th></tr>
      </thead>
      <tbody>
        {#if cargando}
          <tr><td colspan="6" class="py-10 text-center text-slate-400">Cargando…</td></tr>
        {:else}
          {#each lista as s}
            <tr class="cursor-pointer transition odd:bg-white/25 hover:bg-white/70" on:click={() => navigate(`/solicitudes/${s.id}`)}>
              <td class="whitespace-nowrap font-mono text-xs"><a href="/solicitudes/{s.id}" use:link class="text-brand-700 hover:underline" on:click|stopPropagation>{s.codigo}</a></td>
              <td class="max-w-[22rem]">
                <p class="truncate font-medium text-slate-800" title={s.asunto}>{s.asunto}</p>
                <p class="truncate text-xs text-slate-500">{s.categoria.nombre}{rol !== 'ESTUDIANTE' ? ' · ' + s.solicitante.nombre_completo : ''}</p>
              </td>
              <td><PrioridadBadge prioridad={s.prioridad} /></td>
              <td><EstadoBadge estado={s.estado} /></td>
              <td class="truncate text-xs {s.responsable ? '' : 'italic text-slate-400'}" title={s.responsable?.nombre_completo || 'Sin asignar'}>{s.responsable?.nombre_completo || 'Sin asignar'}</td>
              <td class="text-xs">
                <p class="text-slate-600">Reg. {fechaCorta(s.fecha_registro)}</p>
                <p class={s.vencida ? 'font-semibold text-rose-600' : 'text-slate-500'}>Lím. {fechaCorta(s.fecha_limite)}</p>
              </td>
            </tr>
          {:else}
            <tr>
              <td colspan="6">
                <div class="panel-vacio">
                  <span class="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-500 ring-1 ring-brand-100">
                    <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z"/></svg>
                  </span>
                  <div>
                    <p class="text-sm font-medium text-slate-700">Sin resultados</p>
                    <p class="mt-1 text-xs text-slate-500">Ajuste los filtros o limpie la búsqueda.</p>
                  </div>
                </div>
              </td>
            </tr>
          {/each}
        {/if}
      </tbody>
    </table>
  </div>
</div>

<NuevaSolicitud bind:abierto={modalNueva} on:creada={cargar} />
