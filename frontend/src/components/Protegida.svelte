<script>
  // Control de acceso en la interfaz. La seguridad real está en el backend (dependencias require_roles).
  import { sesion } from '../lib/stores.js'
  export let roles = []
</script>

{#if $sesion && roles.includes($sesion.rol.codigo)}
  <slot />
{:else}
  <div class="tarjeta mx-auto mt-16 max-w-md p-8 text-center">
    <p class="text-lg font-semibold text-slate-900">Acceso restringido</p>
    <p class="mt-2 text-sm text-slate-500">Su rol no tiene permiso para ver esta sección.</p>
  </div>
{/if}
