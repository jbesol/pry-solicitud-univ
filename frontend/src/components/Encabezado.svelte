<script>
  export let titulo
  export let subtitulo = ''
</script>

<div class="mb-6 flex flex-wrap items-end justify-between gap-4">
  <div class="min-w-0">
    <span class="mb-2.5 block h-1 w-10 rounded-full bg-gradient-to-r from-brand-500 to-brand-200"></span>
    <h1 class="text-[1.65rem] font-semibold leading-tight tracking-tight text-slate-900">{titulo}</h1>
    {#if subtitulo}<p class="mt-1.5 max-w-2xl text-sm text-slate-500">{subtitulo}</p>{/if}
  </div>
  <div class="flex flex-wrap items-center gap-2"><slot /></div>
</div>
