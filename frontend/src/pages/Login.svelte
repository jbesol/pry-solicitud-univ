<script>
  import { navigate } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { sesion } from '../lib/stores.js'

  let email = ''
  let password = ''
  let mostrarPassword = false
  let error = ''
  let cargando = false

  const DEMO = [
    ['Estudiante', 'estudiante@universidad.edu.co'],
    ['Funcionario', 'funcionario@universidad.edu.co'],
    ['Supervisor', 'supervisor@universidad.edu.co'],
    ['Administrador', 'admin@universidad.edu.co']
  ]

  async function entrar() {
    error = ''
    cargando = true
    try {
      const r = await api('/auth/login', { method: 'POST', body: { email, password } })
      sesion.iniciar(r.access_token, r.usuario)
      navigate('/inicio', { replace: true })
    } catch (e) {
      error = e.message
    } finally {
      cargando = false
    }
  }
</script>

<div class="grid min-h-[100dvh] lg:grid-cols-2">
  <div class="relative hidden overflow-hidden bg-gradient-to-br from-brand-900 via-brand-800 to-brand-700 lg:flex lg:flex-col lg:justify-between lg:p-12">
    <div class="flotante absolute -right-24 -top-24 h-96 w-96 rounded-full bg-white/15 blur-3xl"></div>
    <div class="flotante-lenta absolute -bottom-32 -left-16 h-96 w-96 rounded-full bg-brand-500/40 blur-3xl"></div>
    <div class="flotante absolute bottom-1/3 right-1/4 h-64 w-64 rounded-full bg-brand-200/20 blur-3xl"></div>
    <div class="relative flex items-center gap-3">
      <div class="rounded-xl bg-white px-3 py-2 shadow-lg shadow-brand-900/25">
        <img src="/logo-cul.png" alt="Corporación Universitaria Latinoamericana" class="h-8 w-auto" width="235" height="90" />
      </div>
      <span class="text-sm font-semibold text-white">Sistema de Solicitudes</span>
    </div>
    <div class="relative max-w-md">
      <p class="mb-3 text-sm font-medium uppercase tracking-[0.18em] text-brand-200">Corporación Universitaria Latinoamericana</p>
      <h2 class="text-4xl font-semibold leading-tight text-white">Todas las solicitudes universitarias, en un solo lugar.</h2>
      <p class="mt-4 text-brand-100">Registre, asigne, atienda y haga seguimiento a cada caso con trazabilidad completa y tiempos de respuesta medibles.</p>
    </div>
    <p class="relative text-xs text-brand-200">Proyecto final · Ingeniería del Software · 2026</p>
  </div>

  <div class="flex flex-col items-center justify-center gap-5 px-4 pb-[calc(1rem+env(safe-area-inset-bottom))] pt-6 sm:p-6 lg:gap-0">
    <!-- Identidad institucional en móvil y tablet (el panel lateral solo se ve desde lg) -->
    <div class="flex w-full max-w-sm flex-col items-center gap-3 lg:hidden">
      <img src="/logo-cul.png" alt="Corporación Universitaria Latinoamericana · Institución de Educación Superior" class="h-16 w-auto drop-shadow-sm" width="235" height="90" />
      <div class="text-center">
        <p class="text-[11px] font-medium uppercase leading-snug tracking-[0.16em] text-brand-700">Sistema de Solicitudes</p>
        <p class="mt-1 text-[11px] leading-snug text-slate-500">Barranquilla, Colombia</p>
      </div>
    </div>

    <div class="vidrio w-full max-w-sm rounded-3xl p-5 sm:p-8">
      <h1 class="text-2xl font-semibold text-slate-900">Iniciar sesión</h1>
      <p class="mt-1 text-sm text-slate-500">Ingrese con su correo institucional.</p>

      <form class="mt-8 space-y-4" on:submit|preventDefault={entrar}>
        <div>
          <label class="etiqueta" for="email">Correo</label>
          <input id="email" class="campo" type="email" bind:value={email} autocomplete="username" required />
        </div>
        <div>
          <label class="etiqueta" for="pw">Contraseña</label>
          <div class="relative">
            <input id="pw" class="campo pr-11" type={mostrarPassword ? 'text' : 'password'} value={password} on:input={(e) => (password = e.currentTarget.value)} autocomplete="current-password" required />
            <button type="button" class="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100 hover:text-brand-700" on:click={() => (mostrarPassword = !mostrarPassword)} aria-label={mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}>
              {#if mostrarPassword}
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 3l18 18M10.6 10.6a2 2 0 002.8 2.8M9.9 5.2A10.7 10.7 0 0112 5c5.5 0 9 7 9 7a18 18 0 01-2.1 3.1M6.6 6.6C4.2 8.2 3 12 3 12s3.5 7 9 7c1.2 0 2.3-.3 3.3-.7"/></svg>
              {:else}
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M2.5 12s3.5-7 9.5-7 9.5 7 9.5 7-3.5 7-9.5 7-9.5-7-9.5-7z"/><circle cx="12" cy="12" r="3"/></svg>
              {/if}
            </button>
          </div>
        </div>
        {#if error}<p class="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>{/if}
        <button class="btn-primario w-full" disabled={cargando}>{cargando ? 'Ingresando…' : 'Ingresar'}</button>
      </form>

      <div class="mt-8 rounded-2xl border border-dashed border-slate-300/70 bg-white/40 p-4 backdrop-blur-sm">
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Cuentas de demostración · clave Demo1234*</p>
        <div class="mt-3 grid grid-cols-2 gap-2">
          {#each DEMO as [rol, correo]}
            <button type="button" class="btn-secundario py-1.5 text-xs" on:click={() => { email = correo; password = 'Demo1234*' }}>{rol}</button>
          {/each}
        </div>
      </div>
    </div>

    <p class="text-center text-[11px] leading-snug text-slate-500 lg:hidden">Proyecto final · Ingeniería del Software · 2026</p>
  </div>
</div>
