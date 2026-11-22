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

<div class="tarjeta divide-y divide-slate-100">
  {#each lista as p}
    <form class="flex flex-wrap items-center gap-4 p-5" on:submit|preventDefault={() => guardar(p)}>
      <div class="min-w-0 flex-1">
        <p class="font-mono text-sm font-semibold text-slate-800">{p.clave}</p>
        <p class="text-xs text-slate-500">{p.descripcion}</p>
      </div>
      {#if p.clave === 'NOTIFICAR_CORREO'}
        <select class="campo w-48" bind:value={p.valor}><option value="false">false</option><option value="true">true</option></select>
      {:else}
        <input class="campo w-48" bind:value={p.valor} required />
      {/if}
      <button class="btn-secundario">Guardar</button>
    </form>
  {/each}
</div>
