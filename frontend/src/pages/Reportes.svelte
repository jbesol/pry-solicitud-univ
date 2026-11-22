<script>
  import { onMount } from 'svelte'
  import { api, qs } from '../lib/api.js'
  import { avisar } from '../lib/stores.js'
  import Encabezado from '../components/Encabezado.svelte'
  import Barras from '../components/Barras.svelte'

  let r = null
  let categorias = []
  let f = { desde: '', hasta: '', categoria_id: '', prioridad: '' }

  async function cargar() { r = await api('/reportes/resumen' + qs(f)).catch((e) => (avisar(e.message, 'error'), null)) }
  onMount(async () => { categorias = await api('/categorias').catch(() => []); cargar() })

  async function exportar() {
    try {
      const res = await api('/reportes/exportar' + qs(f), { raw: true })
      const url = URL.createObjectURL(await res.blob())
      const a = Object.assign(document.createElement('a'), { href: url, download: 'reporte_solicitudes.csv' })
      a.click()
      URL.revokeObjectURL(url)
    } catch (e) { avisar(e.message, 'error') }
  }
  function periodo(dias) {
    const h = new Date()
    const d = new Date(Date.now() - dias * 864e5)
    f.hasta = h.toISOString().slice(0, 10)
    f.desde = d.toISOString().slice(0, 10)
    cargar()
  }

  const COLORES_ESTADO = { REGISTRADA: '#94a3b8', ASIGNADA: '#0ea5e9', EN_PROCESO: '#f59e0b', RESUELTA: '#10b981', CERRADA: '#52525b', RECHAZADA: '#e11d48', REABIERTA: '#8b5cf6' }
  const COLORES_PRIO = { BAJA: '#94a3b8', MEDIA: '#0ea5e9', ALTA: '#f59e0b', URGENTE: '#e11d48' }
</script>

<Encabezado titulo="Reportes y estadísticas" subtitulo="Estado general de las solicitudes e indicadores de tiempos de respuesta">
  <button class="btn-secundario" on:click={exportar}>Exportar CSV</button>
</Encabezado>

<div class="tarjeta mb-6 flex flex-wrap items-end gap-3 p-4">
  <div><label class="etiqueta" for="rd">Desde</label><input id="rd" type="date" class="campo" bind:value={f.desde} on:change={cargar} /></div>
  <div><label class="etiqueta" for="rh">Hasta</label><input id="rh" type="date" class="campo" bind:value={f.hasta} on:change={cargar} /></div>
  <div><label class="etiqueta" for="rc">Categoría</label>
    <select id="rc" class="campo" bind:value={f.categoria_id} on:change={cargar}><option value="">Todas</option>{#each categorias as c}<option value={c.id}>{c.nombre}</option>{/each}</select></div>
  <div class="flex gap-1">
    {#each [[7, '7 días'], [30, '30 días'], [90, '90 días']] as [d, t]}<button class="btn-fantasma px-3 text-xs" on:click={() => periodo(d)}>{t}</button>{/each}
    <button class="btn-fantasma px-3 text-xs" on:click={() => { f = { desde: '', hasta: '', categoria_id: '', prioridad: '' }; cargar() }}>Todo</button>
  </div>
</div>

{#if r}
  <div class="grid grid-cols-2 gap-4 lg:grid-cols-5">
    {#each [
      ['Total', r.total, ''],
      ['Abiertas', r.abiertas, ''],
      ['Vencidas', r.vencidas, r.vencidas ? 'text-rose-600' : ''],
      ['Cumplimiento SLA', r.cumplimiento_sla === null ? '—' : r.cumplimiento_sla + ' %', ''],
      ['Tiempo prom. resolución', r.tiempo_promedio_resolucion_horas === null ? '—' : r.tiempo_promedio_resolucion_horas + ' h', '']
    ] as [t, v, c]}
      <div class="tarjeta p-5">
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">{t}</p>
        <p class="mt-2 text-2xl font-semibold text-slate-900 {c}">{v}</p>
      </div>
    {/each}
  </div>

  <div class="mt-6 grid gap-6 lg:grid-cols-2">
    <Barras titulo="Por estado" datos={r.por_estado} colores={COLORES_ESTADO} />
    <Barras titulo="Por prioridad" datos={r.por_prioridad} colores={COLORES_PRIO} />
    <Barras titulo="Por categoría" datos={r.por_categoria} />
    <Barras titulo="Por responsable" datos={r.por_responsable} />
    <div class="lg:col-span-2"><Barras titulo="Solicitudes registradas por mes" datos={r.por_mes} /></div>
  </div>
{:else}
  <p class="text-slate-400">Cargando…</p>
{/if}
