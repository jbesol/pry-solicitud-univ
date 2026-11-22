<script>
  import { fly } from 'svelte/transition'
  import { toasts } from '../lib/stores.js'
</script>

<div class="pointer-events-none fixed bottom-4 right-4 z-50 flex w-80 flex-col gap-2" aria-live="polite">
  {#each $toasts as t (t.id)}
    <div transition:fly={{ x: 40, duration: 200 }}
      class="pointer-events-auto rounded-lg border px-4 py-3 text-sm shadow-lg {t.tipo === 'error' ? 'border-rose-200 bg-rose-50 text-rose-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800'}">
      {t.texto}
    </div>
  {/each}
</div>
