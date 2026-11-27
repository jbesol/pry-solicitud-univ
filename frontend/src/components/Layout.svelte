<script>
  import { onDestroy, onMount } from 'svelte'
  import { link, navigate, useLocation } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { avisar, noLeidas, sesion } from '../lib/stores.js'
  import { ROLES, iniciales, relativo } from '../lib/formato.js'
  import Modal from './Modal.svelte'

  const ICONOS = {
    inicio: 'M3 10.5 12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1z',
    solicitudes: 'M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2M9 5a2 2 0 0 0 2 2h2a2 2 0 0 0 2-2M9 5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2m-6 9 2 2 4-4',
    reportes: 'M4 20V10m6 10V4m6 16v-7m4 7H2',
    usuarios: 'M17 20h5v-2a3 3 0 0 0-5.36-1.86M17 20H7m10 0v-2c0-.66-.13-1.28-.36-1.86M7 20H2v-2a3 3 0 0 1 5.36-1.86M7 20v-2c0-.66.13-1.28.36-1.86m0 0a5 5 0 0 1 9.28 0M15 7a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
    categorias: 'M7 7h.01M7 3h5c.51 0 1.02.2 1.41.59l7 7a2 2 0 0 1 0 2.82l-7 7a2 2 0 0 1-2.82 0l-7-7A2 2 0 0 1 3 12V7a4 4 0 0 1 4-4',
    parametros: 'M10.3 4.3c.4-1.7 2.9-1.7 3.4 0a1.7 1.7 0 0 0 2.6 1c1.5-.9 3.3.8 2.4 2.4a1.7 1.7 0 0 0 1 2.6c1.7.4 1.7 2.9 0 3.4a1.7 1.7 0 0 0-1 2.6c.9 1.5-.8 3.3-2.4 2.4a1.7 1.7 0 0 0-2.6 1c-.4 1.7-2.9 1.7-3.4 0a1.7 1.7 0 0 0-2.6-1c-1.5.9-3.3-.8-2.4-2.4a1.7 1.7 0 0 0-1-2.6c-1.7-.4-1.7-2.9 0-3.4a1.7 1.7 0 0 0 1-2.6c-.9-1.5.8-3.3 2.4-2.4a1.7 1.7 0 0 0 2.6-1zM15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0',
    campana: 'M15 17h5l-1.4-1.4A2 2 0 0 1 18 14.2V11a6 6 0 0 0-4-5.66V5a2 2 0 1 0-4 0v.34A6 6 0 0 0 6 11v3.2c0 .53-.21 1.04-.59 1.41L4 17h5m6 0v1a3 3 0 1 1-6 0v-1m6 0H9'
  }

  $: rol = $sesion?.rol?.codigo
  $: menu = [
    { href: '/inicio', texto: 'Inicio', icono: 'inicio' },
    { href: '/solicitudes', texto: rol === 'FUNCIONARIO' ? 'Mis asignaciones' : rol === 'ESTUDIANTE' ? 'Mis solicitudes' : 'Solicitudes', icono: 'solicitudes' },
    ...(['ADMINISTRADOR', 'SUPERVISOR'].includes(rol) ? [{ href: '/reportes', texto: 'Reportes', icono: 'reportes' }] : []),
    ...(rol === 'ADMINISTRADOR'
      ? [
          { href: '/usuarios', texto: 'Usuarios y roles', icono: 'usuarios' },
          { href: '/categorias', texto: 'Categorías', icono: 'categorias' },
          { href: '/parametros', texto: 'Parámetros', icono: 'parametros' }
        ]
      : [])
  ]

  const ubicacion = useLocation()
  $: ruta = $ubicacion.pathname
  $: ruta, (menuMovil = false)
  const activo = (href, r) => r === href || (href !== '/inicio' && r.startsWith(href)) || (href === '/inicio' && r === '/')

  // ----- notificaciones (consulta periódica cada 30 s)
  let panel = false
  let recientes = []
  let menuMovil = false
  async function contar() {
    try { noLeidas.set((await api('/notificaciones/no-leidas')).total) } catch {}
  }
  async function abrirPanel() {
    panel = !panel
    if (panel) recientes = await api('/notificaciones?no_leidas=false').then((l) => l.slice(0, 6)).catch(() => [])
  }
  async function abrirNotif(n) {
    panel = false
    if (!n.leida) { await api(`/notificaciones/${n.id}/leida`, { method: 'PATCH' }).catch(() => {}); contar() }
    if (n.solicitud_id) navigate(`/solicitudes/${n.solicitud_id}`)
  }
  let timer
  onMount(() => { contar(); timer = setInterval(contar, 30000) })
  onDestroy(() => clearInterval(timer))

  // ----- cambio de contraseña
  let modalClave = false
  let clave = { actual: '', nueva: '', confirmar: '' }
  let cambiandoClave = false
  let mostrarActual = false
  let mostrarNueva = false
  let mostrarConfirmar = false
  async function cambiarClave() {
    if (clave.nueva.length < 8) return avisar('La nueva contraseña debe tener al menos 8 caracteres', 'error')
    if (clave.nueva !== clave.confirmar) return avisar('Las contraseñas no coinciden', 'error')
    cambiandoClave = true
    try {
      await api('/auth/cambiar-password', { method: 'POST', body: { actual: clave.actual, nueva: clave.nueva } })
      avisar('Contraseña actualizada')
      modalClave = false
      clave = { actual: '', nueva: '', confirmar: '' }
    } catch (e) { avisar(e.message, 'error') }
    finally { cambiandoClave = false }
  }
  function salir() {
    sesion.cerrar()
    noLeidas.set(0)
    window.location.assign('/')
  }
</script>

<div class="min-h-[100dvh] lg:flex">
  <!-- Manchas de color de fondo: dan profundidad a las superficies de vidrio -->
  <div class="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
    <div class="flotante absolute -left-24 top-8 h-80 w-80 rounded-full bg-brand-500/25 blur-3xl"></div>
    <div class="flotante-lenta absolute -right-24 top-1/3 h-96 w-96 rounded-full bg-brand-200/70 blur-3xl"></div>
    <div class="flotante absolute -bottom-32 left-1/3 h-96 w-96 rounded-full bg-brand-900/10 blur-3xl"></div>
  </div>

  <!-- Barra lateral -->
  <aside class="fixed inset-y-0 left-0 z-30 flex w-64 max-w-[85vw] transform flex-col border-r border-white/10 bg-gradient-to-b from-brand-900/95 via-brand-900/92 to-brand-800/95 text-brand-100 shadow-2xl shadow-brand-900/40 backdrop-blur-xl transition duration-300 lg:static lg:w-64 lg:max-w-none lg:translate-x-0 {menuMovil ? 'translate-x-0' : '-translate-x-full'}">
    <div class="flex h-16 shrink-0 items-center gap-3 px-5">
      <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-white/10">
        <svg class="h-5 w-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M5 7h14M5 12h14M5 17h16"/></svg>
      </div>
      <div class="leading-tight">
        <p class="text-sm font-semibold leading-tight text-white">Solicitudes CUL</p>
        <p class="text-[11px] leading-tight text-brand-200">Corporación Universitaria Latinoamericana</p>
      </div>
    </div>
    <nav class="mt-4 flex-1 space-y-1 overflow-y-auto overscroll-contain px-3 pb-4">
      {#each menu as m}
        <a href={m.href} use:link
          class="flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition duration-200 {activo(m.href, ruta) ? 'bg-white/15 font-medium text-white shadow-inner shadow-white/10 ring-1 ring-white/15' : 'hover:bg-white/10 hover:text-white'}">
          <svg class="h-5 w-5 shrink-0" fill="none" stroke="currentColor" stroke-width="1.7" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={ICONOS[m.icono]}/></svg>
          {m.texto}
        </a>
      {/each}
    </nav>
    <div class="shrink-0 border-t border-white/10 p-4 pb-[calc(1rem+env(safe-area-inset-bottom))]">
      <p class="truncate text-sm font-medium text-white">{$sesion.nombre_completo}</p>
      <p class="truncate text-xs text-brand-200">{ROLES[rol]}</p>
      <div class="mt-3 flex flex-wrap gap-2">
        <button class="rounded-md bg-white/10 px-2.5 py-1 text-xs hover:bg-white/20" on:click={() => (modalClave = true)}>Contraseña</button>
        <button class="rounded-md bg-white/10 px-2.5 py-1 text-xs hover:bg-white/20" on:click={salir}>Cerrar sesión</button>
      </div>
    </div>
  </aside>
  {#if menuMovil}<button class="fixed inset-0 z-20 bg-brand-900/30 backdrop-blur-sm lg:hidden" on:click={() => (menuMovil = false)} aria-label="Cerrar menú"></button>{/if}

  <div class="flex min-w-0 flex-1 flex-col">
    <header class="sticky top-0 z-10 flex h-16 items-center justify-between gap-2 border-b border-white/60 bg-white/60 px-4 shadow-sm shadow-brand-900/5 backdrop-blur-xl lg:px-8">
      <button class="rounded-md p-2 text-slate-600 hover:bg-slate-100 lg:hidden" on:click={() => (menuMovil = true)} aria-label="Abrir menú">
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
      </button>
      <div class="hidden text-sm text-slate-500 lg:block">Bienvenido(a), <span class="font-medium text-slate-800">{$sesion.nombres}</span></div>
      <div class="relative flex items-center gap-3">
        <button class="relative rounded-full p-2 text-slate-600 hover:bg-slate-100" on:click={abrirPanel} aria-label="Notificaciones">
          <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.7" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d={ICONOS.campana}/></svg>
          {#if $noLeidas > 0}
            <span class="absolute -right-0.5 -top-0.5 flex h-5 min-w-5 items-center justify-center rounded-full bg-rose-600 px-1 text-[10px] font-bold text-white">{$noLeidas > 99 ? '99+' : $noLeidas}</span>
          {/if}
        </button>
        <div class="flex h-9 w-9 items-center justify-center rounded-full bg-brand-100 text-sm font-semibold text-brand-800">{iniciales($sesion.nombre_completo)}</div>

        {#if panel}
          <button class="fixed inset-0 z-10 cursor-default" on:click={() => (panel = false)} aria-label="Cerrar"></button>
          <div class="vidrio absolute right-0 top-12 z-20 w-[min(24rem,calc(100vw_-_2rem))] overflow-hidden rounded-2xl">
            <div class="flex items-center justify-between border-b border-white/60 px-4 py-3">
              <p class="text-sm font-semibold text-slate-900">Notificaciones</p>
              <a href="/notificaciones" use:link class="text-xs font-medium text-brand-600 hover:underline" on:click={() => (panel = false)}>Ver todas</a>
            </div>
            {#each recientes as n}
              <button class="block w-full border-b border-slate-100/70 px-4 py-3 text-left transition hover:bg-white/70 {n.leida ? '' : 'bg-brand-50/60'}" on:click={() => abrirNotif(n)}>
                <p class="text-sm font-medium text-slate-800">{n.titulo}</p>
                <p class="mt-0.5 line-clamp-2 text-xs text-slate-500">{n.mensaje}</p>
                <p class="mt-1 text-[11px] text-slate-400">{relativo(n.fecha)}</p>
              </button>
            {:else}
              <p class="px-4 py-8 text-center text-sm text-slate-400">Sin notificaciones</p>
            {/each}
          </div>
        {/if}
      </div>
    </header>

    <main class="mx-auto w-full max-w-7xl flex-1 px-3 py-5 pb-[calc(1.25rem+env(safe-area-inset-bottom))] sm:px-4 sm:py-6 lg:p-8"><slot /></main>
  </div>
</div>

<Modal titulo="Cambiar contraseña" bind:abierto={modalClave} ancho="max-w-sm">
  <form class="space-y-4" on:submit|preventDefault={cambiarClave}>
    <div>
      <label class="etiqueta" for="c1">Contraseña actual</label>
      <div class="relative">
        <input id="c1" class="campo pr-11" type={mostrarActual ? 'text' : 'password'} value={clave.actual} on:input={(e) => (clave.actual = e.currentTarget.value)} required />
        <button type="button" class="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100" on:click={() => (mostrarActual = !mostrarActual)} aria-label={mostrarActual ? 'Ocultar contraseña' : 'Mostrar contraseña'}>{mostrarActual ? '○' : '◉'}</button>
      </div>
    </div>
    <div>
      <label class="etiqueta" for="c2">Nueva contraseña (mín. 8)</label>
      <div class="relative">
        <input id="c2" class="campo pr-11" type={mostrarNueva ? 'text' : 'password'} value={clave.nueva} on:input={(e) => (clave.nueva = e.currentTarget.value)} minlength="8" required />
        <button type="button" class="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100" on:click={() => (mostrarNueva = !mostrarNueva)} aria-label={mostrarNueva ? 'Ocultar contraseña' : 'Mostrar contraseña'}>{mostrarNueva ? '○' : '◉'}</button>
      </div>
    </div>
    <div>
      <label class="etiqueta" for="c3">Confirmar</label>
      <div class="relative">
        <input id="c3" class="campo pr-11" type={mostrarConfirmar ? 'text' : 'password'} value={clave.confirmar} on:input={(e) => (clave.confirmar = e.currentTarget.value)} required />
        <button type="button" class="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100" on:click={() => (mostrarConfirmar = !mostrarConfirmar)} aria-label={mostrarConfirmar ? 'Ocultar contraseña' : 'Mostrar contraseña'}>{mostrarConfirmar ? '○' : '◉'}</button>
      </div>
    </div>
    <div class="flex justify-end gap-2"><button type="button" class="btn-secundario" on:click={() => (modalClave = false)}>Cancelar</button><button type="submit" class="btn-primario" disabled={cambiandoClave}>{cambiandoClave ? 'Guardando…' : 'Guardar'}</button></div>
  </form>
</Modal>
