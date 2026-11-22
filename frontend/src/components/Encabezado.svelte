<script>
  export let titulo
  export let subtitulo = ''
</script>

<div class="mb-6 flex flex-wrap items-end justify-between gap-3">
  <div>
    <h1 class="text-2xl font-semibold tracking-tight text-slate-900">{titulo}</h1>
    {#if subtitulo}<p class="mt-1 text-sm text-slate-500">{subtitulo}</p>{/if}
  </div>
  <div class="flex items-center gap-2"><slot /></div>
</div>
