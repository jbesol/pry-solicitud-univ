<script>
  import { navigate } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { sesion } from '../lib/stores.js'

  let email = ''
  let password = ''
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

<div class="grid min-h-screen lg:grid-cols-2">
  <div class="relative hidden overflow-hidden bg-brand-900 lg:flex lg:flex-col lg:justify-between lg:p-12">
    <div class="absolute -right-24 -top-24 h-96 w-96 rounded-full bg-brand-700/40"></div>
    <div class="absolute -bottom-32 -left-16 h-96 w-96 rounded-full bg-brand-800"></div>
    <div class="relative flex items-center gap-3 text-white">
      <div class="flex h-10 w-10 items-center justify-center rounded-lg bg-white/10">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h9"/></svg>
      </div>
      <span class="font-semibold">Sistema de Solicitudes</span>
    </div>
    <div class="relative max-w-md">
      <h2 class="text-4xl font-semibold leading-tight text-white">Todas las solicitudes de la universidad, en un solo lugar.</h2>
      <p class="mt-4 text-brand-100">Registre, asigne, atienda y haga seguimiento a cada caso con trazabilidad completa y tiempos de respuesta medibles.</p>
    </div>
    <p class="relative text-xs text-brand-200">Proyecto final · Ingeniería del Software · 2026</p>
  </div>

  <div class="flex items-center justify-center p-6">
    <div class="w-full max-w-sm">
      <h1 class="text-2xl font-semibold text-slate-900">Iniciar sesión</h1>
      <p class="mt-1 text-sm text-slate-500">Ingrese con su correo institucional.</p>

      <form class="mt-8 space-y-4" on:submit|preventDefault={entrar}>
        <div>
          <label class="etiqueta" for="email">Correo</label>
          <input id="email" class="campo" type="email" bind:value={email} autocomplete="username" required />
        </div>
        <div>
          <label class="etiqueta" for="pw">Contraseña</label>
          <input id="pw" class="campo" type="password" bind:value={password} autocomplete="current-password" required />
        </div>
        {#if error}<p class="rounded-lg bg-rose-50 px-3 py-2 text-sm text-rose-700">{error}</p>{/if}
        <button class="btn-primario w-full" disabled={cargando}>{cargando ? 'Ingresando…' : 'Ingresar'}</button>
      </form>

      <div class="mt-8 rounded-xl border border-dashed border-slate-300 p-4">
        <p class="text-xs font-medium uppercase tracking-wide text-slate-500">Cuentas de demostración · clave Demo1234*</p>
        <div class="mt-3 grid grid-cols-2 gap-2">
          {#each DEMO as [rol, correo]}
            <button type="button" class="btn-secundario py-1.5 text-xs" on:click={() => { email = correo; password = 'Demo1234*' }}>{rol}</button>
          {/each}
        </div>
      </div>
    </div>
  </div>
</div>
