<script>
  import { onMount } from 'svelte'
  import { navigate } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { noLeidas } from '../lib/stores.js'
  import { fecha, relativo } from '../lib/formato.js'
  import Encabezado from '../components/Encabezado.svelte'

  let lista = []
  let soloNoLeidas = false
  const cargar = async () => {
    lista = await api('/notificaciones' + (soloNoLeidas ? '?no_leidas=true' : '')).catch(() => [])
    noLeidas.set((await api('/notificaciones/no-leidas').catch(() => ({ total: 0 }))).total)
  }
  onMount(cargar)
  async function leerTodas() { await api('/notificaciones/leer-todas', { method: 'PATCH' }); cargar() }
  async function abrir(n) {
    if (!n.leida) await api(`/notificaciones/${n.id}/leida`, { method: 'PATCH' }).catch(() => {})
    if (n.solicitud_id) navigate(`/solicitudes/${n.solicitud_id}`)
    else cargar()
  }
  const ETQ = { SOLICITUD_REGISTRADA: 'Registro', SOLICITUD_ASIGNADA: 'Asignación', ESTADO_ACTUALIZADO: 'Estado', OBSERVACION_AGREGADA: 'Observación' }
</script>

<Encabezado titulo="Notificaciones" subtitulo="Avisos internos sobre sus solicitudes">
  <label class="flex items-center gap-2 text-sm text-slate-600"><input type="checkbox" bind:checked={soloNoLeidas} on:change={cargar} class="rounded" /> Solo no leídas</label>
  <button class="btn-secundario" on:click={leerTodas}>Marcar todas como leídas</button>
</Encabezado>

<div class="tarjeta divide-y divide-slate-100">
  {#each lista as n}
    <button class="flex w-full items-start gap-4 px-5 py-4 text-left transition hover:bg-white/70 {n.leida ? '' : 'bg-brand-50/50'}" on:click={() => abrir(n)}>
      <span class="mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full {n.leida ? 'bg-slate-200' : 'bg-brand-600'}"></span>
      <div class="min-w-0 flex-1">
        <div class="flex flex-wrap items-center gap-2">
          <p class="text-sm font-medium text-slate-800">{n.titulo}</p>
          <span class="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] font-semibold uppercase text-slate-500">{ETQ[n.tipo]}</span>
        </div>
        <p class="mt-0.5 text-sm text-slate-600">{n.mensaje}</p>
      </div>
      <span class="shrink-0 text-xs text-slate-400" title={fecha(n.fecha)}>{relativo(n.fecha)}</span>
    </button>
  {:else}
    <p class="px-5 py-12 text-center text-sm text-slate-400">No hay notificaciones.</p>
  {/each}
</div>
