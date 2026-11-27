<script>
  import { fly } from 'svelte/transition'
  import { toasts } from '../lib/stores.js'
</script>

<div class="pointer-events-none fixed inset-x-4 bottom-4 z-50 flex flex-col gap-2 sm:inset-x-auto sm:right-4 sm:w-80" aria-live="polite">
  {#each $toasts as t (t.id)}
    <div transition:fly={{ x: 40, duration: 200 }}
      class="pointer-events-auto rounded-xl border px-4 py-3 text-sm shadow-xl shadow-brand-900/10 backdrop-blur-xl {t.tipo === 'error' ? 'border-rose-200/80 bg-rose-50/90 text-rose-800' : 'border-brand-200/80 bg-brand-50/90 text-brand-800'}">
      {t.texto}
    </div>
  {/each}
</div>
