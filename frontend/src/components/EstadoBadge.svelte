<script>
  import { ESTADOS } from '../lib/formato.js'
  export let estado
  $: e = ESTADOS[estado] || { etiqueta: estado, clase: 'bg-slate-100 text-slate-700 ring-slate-300' }
</script>

<span class="inline-flex items-center whitespace-nowrap rounded-full px-2.5 py-0.5 text-xs font-medium ring-1 ring-inset {e.clase}">{e.etiqueta}</span>
