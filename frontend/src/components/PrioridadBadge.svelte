<script>
  import { PRIORIDADES } from '../lib/formato.js'
  export let prioridad
  $: p = PRIORIDADES[prioridad] || PRIORIDADES.MEDIA
</script>

<span class="inline-flex items-center gap-1.5 whitespace-nowrap text-xs {p.clase}">
  <span class="h-2 w-2 rounded-full {p.punto}"></span>{p.etiqueta}
</span>
