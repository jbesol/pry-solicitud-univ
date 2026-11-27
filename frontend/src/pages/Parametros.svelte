<script>
  import { onMount } from 'svelte'
  import { api } from '../lib/api.js'
  import { avisar } from '../lib/stores.js'
  import Encabezado from '../components/Encabezado.svelte'

  let lista = []
  onMount(async () => (lista = await api('/parametros').catch(() => [])))
  async function guardar(p) {
    try { await api(`/parametros/${p.clave}`, { method: 'PUT', body: { valor: p.valor } }); avisar(`${p.clave} actualizado`) }
    catch (e) { avisar(e.message, 'error') }
  }
</script>

<Encabezado titulo="Parámetros del sistema" subtitulo="Valores configurables usados por las reglas de negocio" />

<div class="panel">
  <div class="panel-cabecera">
    <div class="panel-titulo">
      <span class="panel-icono">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/></svg>
      </span>
      Valores configurables
    </div>
    <span class="chip-conteo">{lista.length}</span>
  </div>
  <div class="divide-y divide-white/60">
    {#each lista as p}
      <form class="flex flex-wrap items-center gap-3 px-4 py-4 transition hover:bg-white/50 sm:gap-4 sm:px-5" on:submit|preventDefault={() => guardar(p)}>
        <span class="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-brand-50 text-brand-600 ring-1 ring-brand-100">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h10M18 6h2M4 12h4M12 12h8M4 18h12M20 18h0"/><circle cx="16" cy="6" r="2"/><circle cx="10" cy="12" r="2"/><circle cx="18" cy="18" r="2"/></svg>
        </span>
        <div class="min-w-0 flex-1">
          <p class="font-mono text-sm font-semibold text-slate-800">{p.clave}</p>
          <p class="text-xs text-slate-500">{p.descripcion}</p>
        </div>
        <div class="flex w-full items-center gap-2 sm:ml-auto sm:w-auto">
          {#if p.clave === 'NOTIFICAR_CORREO'}
            <select class="campo min-w-0 flex-1 sm:w-48 sm:flex-none" bind:value={p.valor}><option value="false">false</option><option value="true">true</option></select>
          {:else}
            <input class="campo min-w-0 flex-1 sm:w-48 sm:flex-none" bind:value={p.valor} required />
          {/if}
          <button class="btn-secundario shrink-0">Guardar</button>
        </div>
      </form>
    {/each}
  </div>
</div>
