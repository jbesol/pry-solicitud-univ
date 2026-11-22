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

<Encabezado {titulo} subtitulo={lista.length >= 500 ? "Mostrando las 500 más recientes · use los filtros para acotar" : `${lista.length} resultado(s)`}>
  {#if puedeRegistrar}<button class="btn-primario" on:click={() => (modalNueva = true)}>+ Nueva solicitud</button>{/if}
</Encabezado>

{#if rol === 'FUNCIONARIO'}
  <div class="mb-4 inline-flex rounded-lg border border-slate-200 bg-white p-1 text-sm">
    {#each [['', 'Asignadas a mí'], ['propias', 'Registradas por mí']] as [v, txt]}
      <button class="rounded-md px-3 py-1.5 {f.alcance === v ? 'bg-brand-600 text-white' : 'text-slate-600 hover:bg-slate-50'}" on:click={() => { f.alcance = v; cargar() }}>{txt}</button>
    {/each}
  </div>
{/if}

<div class="tarjeta mb-4 grid gap-3 p-4 sm:grid-cols-2 lg:grid-cols-6">
  <div class="lg:col-span-2">
    <label class="etiqueta" for="q">Buscar</label>
    <input id="q" class="campo" placeholder="Código, asunto o descripción" bind:value={f.q} on:input={buscarDiferido} />
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
  <div class="flex items-end"><button class="btn-fantasma" on:click={limpiar}>Limpiar filtros</button></div>
</div>

<div class="tarjeta overflow-x-auto">
  <table class="tabla w-full min-w-[820px]">
    <thead>
      <tr><th>Código</th><th>Solicitud</th><th>Prioridad</th><th>Estado</th><th>Responsable</th><th>Registro</th><th>Límite</th></tr>
    </thead>
    <tbody>
      {#if cargando}
        <tr><td colspan="7" class="py-10 text-center text-slate-400">Cargando…</td></tr>
      {:else}
        {#each lista as s}
          <tr class="cursor-pointer hover:bg-slate-50" on:click={() => navigate(`/solicitudes/${s.id}`)}>
            <td class="whitespace-nowrap font-mono text-xs"><a href="/solicitudes/{s.id}" use:link class="text-brand-700 hover:underline" on:click|stopPropagation>{s.codigo}</a></td>
            <td class="max-w-[22rem]">
              <p class="truncate font-medium text-slate-800" title={s.asunto}>{s.asunto}</p>
              <p class="truncate text-xs text-slate-500">{s.categoria.nombre}{rol !== 'ESTUDIANTE' ? ' · ' + s.solicitante.nombre_completo : ''}</p>
            </td>
            <td><PrioridadBadge prioridad={s.prioridad} /></td>
            <td><EstadoBadge estado={s.estado} /></td>
            <td class="whitespace-nowrap text-xs {s.responsable ? '' : 'italic text-slate-400'}">{s.responsable?.nombre_completo || 'Sin asignar'}</td>
            <td class="whitespace-nowrap text-xs">{fechaCorta(s.fecha_registro)}</td>
            <td class="whitespace-nowrap text-xs {s.vencida ? 'font-semibold text-rose-600' : ''}">{fechaCorta(s.fecha_limite)}{s.vencida ? ' · vencida' : ''}</td>
          </tr>
        {:else}
          <tr><td colspan="7" class="py-12 text-center text-slate-400">No se encontraron solicitudes con esos filtros.</td></tr>
        {/each}
      {/if}
    </tbody>
  </table>
</div>

<NuevaSolicitud bind:abierto={modalNueva} on:creada={cargar} />
