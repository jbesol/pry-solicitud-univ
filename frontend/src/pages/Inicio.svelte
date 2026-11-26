<script>
  import { onMount } from 'svelte'
  import { link } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { sesion } from '../lib/stores.js'
  import { ROLES, fechaCorta } from '../lib/formato.js'
  import Encabezado from '../components/Encabezado.svelte'
  import EstadoBadge from '../components/EstadoBadge.svelte'
  import PrioridadBadge from '../components/PrioridadBadge.svelte'
  import NuevaSolicitud from '../components/NuevaSolicitud.svelte'

  let lista = []
  let cargando = true
  let modalNueva = false
  $: rol = $sesion.rol.codigo
  $: puedeRegistrar = ['ESTUDIANTE', 'FUNCIONARIO'].includes(rol)

  async function cargar() {
    cargando = true
    lista = await api('/solicitudes').catch(() => [])
    cargando = false
  }
  onMount(cargar)

  $: abiertas = lista.filter((s) => !['RESUELTA', 'CERRADA', 'RECHAZADA'].includes(s.estado))
  const ICONOS = {
    total: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2',
    abiertas: 'M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z',
    reloj: 'M12 8v4l3 2m6-2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z',
    check: 'M9 12l2 2 4-4m6 2a9 9 0 1 1-18 0 9 9 0 0 1 18 0z'
  }
  $: tarjetas = [
    { t: rol === 'FUNCIONARIO' ? 'Asignadas a mí' : rol === 'ESTUDIANTE' ? 'Mis solicitudes' : 'Total', v: lista.length, icono: 'total' },
    { t: 'Abiertas', v: abiertas.length, icono: 'abiertas' },
    { t: 'Vencen pronto', v: abiertas.filter((s) => s.vencida || (s.fecha_limite && new Date(s.fecha_limite) - Date.now() < 864e5)).length, icono: 'reloj', alerta: true },
    { t: 'Resueltas / cerradas', v: lista.filter((s) => ['RESUELTA', 'CERRADA'].includes(s.estado)).length, icono: 'check' }
  ]
  $: pendientesTexto = {
    ESTUDIANTE: 'Revise el estado de sus casos y cierre los que ya fueron resueltos.',
    FUNCIONARIO: 'Atienda primero las solicitudes urgentes y las próximas a vencer.',
    SUPERVISOR: 'Asigne las solicitudes nuevas y vigile los tiempos de respuesta.',
    ADMINISTRADOR: 'Gestione usuarios, categorías y parámetros del sistema.'
  }[rol]
  $: recientes = [...abiertas].sort((a, b) => (b.vencida - a.vencida) || (a.fecha_limite || '').localeCompare(b.fecha_limite || '')).slice(0, 6)
</script>

<Encabezado titulo="Hola, {$sesion.nombres}" subtitulo="{ROLES[rol]} · {pendientesTexto}">
  {#if puedeRegistrar}<button class="btn-primario" on:click={() => (modalNueva = true)}>+ Nueva solicitud</button>{/if}
</Encabezado>

<div class="grid grid-cols-2 gap-4 lg:grid-cols-4">
  {#each tarjetas as c}
    <div class="tarjeta-destacada group relative overflow-hidden p-5">
      <span class="pointer-events-none absolute -right-10 -top-10 h-28 w-28 rounded-full blur-2xl transition duration-500 {c.alerta ? 'bg-rose-500/10 group-hover:bg-rose-500/20' : 'bg-brand-500/10 group-hover:bg-brand-500/20'}"></span>
      <div class="relative flex items-start justify-between gap-3">
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">{c.t}</p>
        <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ring-1 {c.alerta ? 'bg-rose-50 text-rose-600 ring-rose-100' : 'bg-brand-50 text-brand-600 ring-brand-100'}">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={ICONOS[c.icono]}/></svg>
        </span>
      </div>
      <p class="relative mt-3 text-3xl font-semibold {c.alerta && c.v ? 'text-rose-600' : 'text-slate-900'}">{cargando ? '…' : c.v}</p>
    </div>
  {/each}
</div>

<div class="panel mt-6">
  <div class="panel-cabecera">
    <div class="panel-titulo">
      <span class="panel-icono">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={ICONOS.reloj}/></svg>
      </span>
      Requieren atención
      {#if recientes.length}<span class="chip-conteo">{recientes.length}</span>{/if}
    </div>
    <a href="/solicitudes" use:link class="btn-fantasma px-3 py-1.5 text-xs">Ver todas →</a>
  </div>
  {#if !cargando && recientes.length === 0}
    <div class="panel-vacio">
      <span class="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-500 ring-1 ring-brand-100">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={ICONOS.check}/></svg>
      </span>
      <p class="text-sm text-slate-500">No hay solicitudes abiertas.</p>
    </div>
  {/if}
  <ul class="divide-y divide-white/60">
    {#each recientes as s}
      <li>
        <a href="/solicitudes/{s.id}" use:link class="group flex flex-wrap items-center gap-x-4 gap-y-1 px-5 py-3 transition hover:bg-white/70">
          <span class="w-32 font-mono text-xs text-slate-500">{s.codigo}</span>
          <span class="min-w-0 flex-1 truncate text-sm font-medium text-slate-800">{s.asunto}</span>
          <PrioridadBadge prioridad={s.prioridad} />
          <EstadoBadge estado={s.estado} />
          <span class="w-32 whitespace-nowrap text-right text-xs {s.vencida ? 'font-semibold text-rose-600' : 'text-slate-500'}">
            {s.vencida ? 'Vencida' : 'Límite'} {fechaCorta(s.fecha_limite)}
          </span>
          <span class="flex h-6 w-6 items-center justify-center rounded-full text-slate-300 transition group-hover:bg-brand-50 group-hover:text-brand-600">
            <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
          </span>
        </a>
      </li>
    {/each}
  </ul>
</div>

<NuevaSolicitud bind:abierto={modalNueva} on:creada={cargar} />
