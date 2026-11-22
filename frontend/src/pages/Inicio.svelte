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
  $: tarjetas = [
    { t: rol === 'FUNCIONARIO' ? 'Asignadas a mí' : rol === 'ESTUDIANTE' ? 'Mis solicitudes' : 'Total', v: lista.length },
    { t: 'Abiertas', v: abiertas.length },
    { t: 'Por resolver hoy o vencidas', v: abiertas.filter((s) => s.vencida || (s.fecha_limite && new Date(s.fecha_limite) - Date.now() < 864e5)).length, alerta: true },
    { t: 'Resueltas / cerradas', v: lista.filter((s) => ['RESUELTA', 'CERRADA'].includes(s.estado)).length }
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
    <div class="tarjeta p-5">
      <p class="text-xs font-medium uppercase tracking-wide text-slate-500">{c.t}</p>
      <p class="mt-2 text-3xl font-semibold {c.alerta && c.v ? 'text-rose-600' : 'text-slate-900'}">{cargando ? '…' : c.v}</p>
    </div>
  {/each}
</div>

<div class="tarjeta mt-6">
  <div class="flex items-center justify-between border-b border-slate-100 px-5 py-4">
    <h2 class="font-semibold text-slate-900">Requieren atención</h2>
    <a href="/solicitudes" use:link class="text-sm font-medium text-brand-600 hover:underline">Ver todas →</a>
  </div>
  {#if !cargando && recientes.length === 0}
    <p class="px-5 py-10 text-center text-sm text-slate-400">No hay solicitudes abiertas.</p>
  {/if}
  <ul>
    {#each recientes as s}
      <li class="border-t border-slate-50 first:border-0">
        <a href="/solicitudes/{s.id}" use:link class="flex flex-wrap items-center gap-x-4 gap-y-1 px-5 py-3 hover:bg-slate-50">
          <span class="w-32 font-mono text-xs text-slate-500">{s.codigo}</span>
          <span class="min-w-0 flex-1 truncate text-sm font-medium text-slate-800">{s.asunto}</span>
          <PrioridadBadge prioridad={s.prioridad} />
          <EstadoBadge estado={s.estado} />
          <span class="w-32 whitespace-nowrap text-right text-xs {s.vencida ? 'font-semibold text-rose-600' : 'text-slate-500'}">
            {s.vencida ? 'Vencida' : 'Límite'} {fechaCorta(s.fecha_limite)}
          </span>
        </a>
      </li>
    {/each}
  </ul>
</div>

<NuevaSolicitud bind:abierto={modalNueva} on:creada={cargar} />
