<script>
  import { fade, fly } from 'svelte/transition'
  export let titulo = ''
  export let abierto = false
  export let ancho = 'max-w-lg'
  const cerrar = () => (abierto = false)
</script>

<svelte:window on:keydown={(e) => abierto && e.key === 'Escape' && cerrar()} />

{#if abierto}
  <div class="fixed inset-0 z-40 flex items-center justify-center p-4" transition:fade={{ duration: 120 }}>
    <button class="absolute inset-0 bg-slate-900/40" on:click={cerrar} aria-label="Cerrar"></button>
    <div class="relative w-full {ancho} max-h-[90vh] overflow-y-auto rounded-xl bg-white shadow-2xl"
      in:fly={{ y: 12, duration: 180 }} role="dialog" aria-modal="true" aria-label={titulo}>
      <div class="flex items-center justify-between border-b border-slate-200 px-5 py-3.5">
        <h3 class="text-base font-semibold text-slate-900">{titulo}</h3>
        <button class="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600" on:click={cerrar} aria-label="Cerrar">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M6 18 18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="p-5"><slot /></div>
    </div>
  </div>
{/if}
