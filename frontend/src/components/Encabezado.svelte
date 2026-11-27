<script>
  export let titulo
  export let subtitulo = ''
</script>

<div class="mb-5 flex flex-wrap items-end justify-between gap-3 sm:mb-6 sm:gap-4">
  <div class="min-w-0">
    <span class="mb-2 block h-1 w-10 rounded-full bg-gradient-to-r from-brand-500 to-brand-200 sm:mb-2.5"></span>
    <h1 class="text-2xl font-semibold leading-tight tracking-tight text-slate-900 sm:text-[1.65rem]">{titulo}</h1>
    {#if subtitulo}<p class="mt-1.5 max-w-2xl text-sm leading-snug text-slate-500">{subtitulo}</p>{/if}
  </div>
  <div class="flex w-full flex-wrap items-center gap-2 sm:w-auto"><slot /></div>
</div>
