<script>
  // Gráfico de barras horizontales simple (sin librerías externas)
  export let titulo
  export let datos = []
  export let colores = {}
  $: max = Math.max(1, ...datos.map((d) => d.total))
  $: total = datos.reduce((a, d) => a + d.total, 0)
</script>

<section class="tarjeta p-4 sm:p-5">
  <div class="mb-4 flex items-baseline justify-between">
    <h2 class="font-semibold text-slate-900">{titulo}</h2>
    <span class="text-xs text-slate-400">{total} en total</span>
  </div>
  {#if datos.length === 0 || total === 0}
    <p class="py-6 text-center text-sm text-slate-400">Sin datos en el periodo</p>
  {:else}
    <ul class="space-y-2.5">
      {#each datos as d}
        <li class="grid grid-cols-[5.5rem_minmax(0,1fr)_2.5rem] items-center gap-2 text-sm sm:grid-cols-[9rem_minmax(0,1fr)_3rem] sm:gap-3">
          <span class="truncate text-slate-600" title={d.etiqueta}>{d.etiqueta}</span>
          <span class="h-5 overflow-hidden rounded bg-slate-100">
            <span class="block h-full rounded transition-all duration-500" style="width:{(d.total / max) * 100}%; background:{colores[d.clave] || '#4c82b4'}"></span>
          </span>
          <span class="text-right font-medium tabular-nums text-slate-800">{d.total}</span>
        </li>
      {/each}
    </ul>
  {/if}
</section>
