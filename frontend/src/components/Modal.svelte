<script>
  import { fade, fly } from 'svelte/transition'
  export let titulo = ''
  export let abierto = false
  export let ancho = 'max-w-lg'
  const cerrar = () => (abierto = false)
</script>

<svelte:window on:keydown={(e) => abierto && e.key === 'Escape' && cerrar()} />

{#if abierto}
  <div class="fixed inset-0 z-40 flex items-end justify-center pb-[env(safe-area-inset-bottom)] sm:items-center sm:p-4" transition:fade={{ duration: 120 }}>
    <button class="absolute inset-0 bg-brand-900/30 backdrop-blur-sm" on:click={cerrar} aria-label="Cerrar"></button>
    <div class="vidrio relative w-full {ancho} max-h-[92vh] overflow-y-auto overscroll-contain rounded-t-2xl sm:max-h-[90vh] sm:rounded-2xl"
      in:fly={{ y: 12, duration: 180 }} role="dialog" aria-modal="true" aria-label={titulo}>
      <div class="flex items-center justify-between gap-3 border-b border-white/60 px-4 py-3.5 sm:px-5">
        <h3 class="min-w-0 truncate text-base font-semibold text-slate-900">{titulo}</h3>
        <button class="rounded-md p-1 text-slate-400 hover:bg-slate-100 hover:text-slate-600" on:click={cerrar} aria-label="Cerrar">
          <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M6 18 18 6M6 6l12 12"/></svg>
        </button>
      </div>
      <div class="p-4 sm:p-5"><slot /></div>
    </div>
  </div>
{/if}
