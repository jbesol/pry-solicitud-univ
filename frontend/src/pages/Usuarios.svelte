<script>
  import { onMount } from 'svelte'
  import { api, qs } from '../lib/api.js'
  import { avisar, sesion } from '../lib/stores.js'
  import { ROLES, fechaCorta } from '../lib/formato.js'
  import Encabezado from '../components/Encabezado.svelte'
  import Modal from '../components/Modal.svelte'

  let lista = []
  let f = { q: '', rol: '', activo: '' }
  let modal = false
  let editando = null
  let form = {}
  let mostrarPassword = false

  const vacio = () => ({ documento: '', nombres: '', apellidos: '', email: '', password: '', telefono: '', dependencia: '', rol: 'ESTUDIANTE' })
  async function cargar() { lista = await api('/usuarios' + qs(f)).catch((e) => (avisar(e.message, 'error'), [])) }
  onMount(cargar)

  function nuevo() { editando = null; form = vacio(); modal = true }
  function editar(u) {
    editando = u
    form = { nombres: u.nombres, apellidos: u.apellidos, email: u.email, telefono: u.telefono || '', dependencia: u.dependencia || '', password: '' }
    modal = true
  }
  async function guardar() {
    try {
      if (editando) {
        const body = { ...form }
        if (!body.password) delete body.password
        await api(`/usuarios/${editando.id}`, { method: 'PUT', body })
        avisar('Usuario actualizado')
      } else {
        await api('/usuarios', { method: 'POST', body: form })
        avisar('Usuario creado')
      }
      modal = false
      cargar()
    } catch (e) { avisar(e.message, 'error') }
  }
  async function cambiarRol(u, rol) {
    try { await api(`/usuarios/${u.id}/rol`, { method: 'PATCH', body: { rol } }); avisar(`Rol de ${u.nombres} actualizado`) } catch (e) { avisar(e.message, 'error') }
    cargar()
  }
  async function alternarActivo(u) {
    try { await api(`/usuarios/${u.id}/activo`, { method: 'PATCH', body: { activo: !u.activo } }); cargar() } catch (e) { avisar(e.message, 'error') }
  }
</script>

<Encabezado titulo="Usuarios y roles" subtitulo="Registro, consulta, edición y asignación de roles">
  <button class="btn-primario" on:click={nuevo}>+ Nuevo usuario</button>
</Encabezado>

<div class="panel mb-4">
  <div class="panel-cabecera">
    <div class="panel-titulo">
      <span class="panel-icono">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 5h18M6 12h12M10 19h4"/></svg>
      </span>
      Filtros
      {#if lista.length}<span class="chip-conteo">{lista.length}</span>{/if}
    </div>
  </div>
  <div class="grid gap-3 p-4 sm:grid-cols-4">
    <div class="sm:col-span-2">
      <label class="etiqueta" for="uq">Buscar</label>
      <div class="relative">
        <svg class="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-4.35-4.35M17 11a6 6 0 11-12 0 6 6 0 0112 0z"/></svg>
        <input id="uq" class="campo pl-9" placeholder="Nombre, correo o documento" bind:value={f.q} on:input={cargar} />
      </div>
    </div>
    <div><label class="etiqueta" for="ur">Rol</label>
      <select id="ur" class="campo" bind:value={f.rol} on:change={cargar}><option value="">Todos</option>{#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}</select></div>
    <div><label class="etiqueta" for="ua">Estado</label>
      <select id="ua" class="campo" bind:value={f.activo} on:change={cargar}><option value="">Todos</option><option value="true">Activos</option><option value="false">Inactivos</option></select></div>
  </div>
</div>

<div class="panel">
  <div class="panel-cabecera">
    <div class="panel-titulo">
      <span class="panel-icono">
        <svg class="h-4 w-4" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 19v-1a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v1M12 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zm4 3a4 4 0 0 0 0-7m4 13v-1a4 4 0 0 0-3-3.87"/></svg>
      </span>
      Usuarios
    </div>
    <span class="text-xs text-slate-500">{lista.length} registro(s)</span>
  </div>
  <div class="tabla-escritorio overflow-x-auto">
    <table class="tabla w-full min-w-[820px]">
      <thead><tr><th>Usuario</th><th>Documento</th><th>Dependencia / programa</th><th>Rol</th><th>Estado</th><th>Creado</th><th></th></tr></thead>
      <tbody>
        {#each lista as u}
          <tr class="transition odd:bg-white/25 hover:bg-white/70 {u.activo ? '' : 'opacity-60'}">
            <td><p class="font-medium text-slate-800">{u.nombre_completo}</p><p class="text-xs text-slate-500">{u.email}</p></td>
            <td class="font-mono text-xs">{u.documento}</td>
            <td>{u.dependencia || '—'}</td>
            <td>
              <select class="campo w-40 py-1" value={u.rol.codigo} on:change={(e) => cambiarRol(u, e.target.value)} disabled={u.id === $sesion.id}>
                {#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}
              </select>
            </td>
            <td><span class="rounded-full px-2 py-0.5 text-xs font-medium {u.activo ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-500'}">{u.activo ? 'Activo' : 'Inactivo'}</span></td>
            <td class="text-xs">{fechaCorta(u.fecha_creacion)}</td>
            <td class="whitespace-nowrap text-right">
              <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => editar(u)}>Editar</button>
              {#if u.id !== $sesion.id}<button class="btn-fantasma px-2 py-1 text-xs" on:click={() => alternarActivo(u)}>{u.activo ? 'Desactivar' : 'Activar'}</button>{/if}
            </td>
          </tr>
        {:else}
          <tr>
            <td colspan="7">
              <div class="panel-vacio">
                <span class="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-500 ring-1 ring-brand-100">
                  <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 19v-1a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v1M12 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zm4 3a4 4 0 0 0 0-7m4 13v-1a4 4 0 0 0-3-3.87"/></svg>
                </span>
                <div>
                  <p class="text-sm font-medium text-slate-700">Sin usuarios</p>
                  <p class="mt-1 text-xs text-slate-500">Ajuste los filtros o cree un nuevo usuario.</p>
                </div>
              </div>
            </td>
          </tr>
        {/each}
      </tbody>
    </table>
  </div>

  <!-- Listado en móvil: tarjetas apiladas -->
  <ul class="lista-movil">
    {#each lista as u}
      <li class="px-4 py-3.5 {u.activo ? '' : 'opacity-60'}">
        <div class="flex items-start justify-between gap-2">
          <div class="min-w-0">
            <p class="truncate text-sm font-medium text-slate-800">{u.nombre_completo}</p>
            <p class="truncate text-xs text-slate-500">{u.email}</p>
          </div>
          <span class="shrink-0 rounded-full px-2 py-0.5 text-xs font-medium {u.activo ? 'bg-brand-50 text-brand-700' : 'bg-slate-100 text-slate-500'}">{u.activo ? 'Activo' : 'Inactivo'}</span>
        </div>
        <div class="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-[11px] text-slate-500">
          <span class="font-mono">{u.documento}</span>
          <span class="truncate">{u.dependencia || '—'}</span>
          <span class="ml-auto">{fechaCorta(u.fecha_creacion)}</span>
        </div>
        <div class="mt-2.5 flex items-center justify-between gap-2">
          <select class="campo w-36 py-1 text-xs" value={u.rol.codigo} on:change={(e) => cambiarRol(u, e.target.value)} disabled={u.id === $sesion.id} aria-label="Rol">
            {#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}
          </select>
          <span class="flex gap-1">
            <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => editar(u)}>Editar</button>
            {#if u.id !== $sesion.id}<button class="btn-fantasma px-2 py-1 text-xs" on:click={() => alternarActivo(u)}>{u.activo ? 'Desactivar' : 'Activar'}</button>{/if}
          </span>
        </div>
      </li>
    {:else}
      <li>
        <div class="panel-vacio">
          <span class="flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-50 text-brand-500 ring-1 ring-brand-100">
            <svg class="h-6 w-6" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M16 19v-1a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v1M12 7a4 4 0 1 1-8 0 4 4 0 0 1 8 0zm4 3a4 4 0 0 0 0-7m4 13v-1a4 4 0 0 0-3-3.87"/></svg>
          </span>
          <div>
            <p class="text-sm font-medium text-slate-700">Sin usuarios</p>
            <p class="mt-1 text-xs text-slate-500">Ajuste los filtros o cree un nuevo usuario.</p>
          </div>
        </div>
      </li>
    {/each}
  </ul>
</div>

<Modal titulo={editando ? `Editar ${editando.nombre_completo}` : 'Nuevo usuario'} bind:abierto={modal} ancho="max-w-xl">
  <form class="grid grid-cols-1 gap-4 sm:grid-cols-2" on:submit|preventDefault={guardar}>
    {#if !editando}
      <div><label class="etiqueta" for="fd">Documento *</label><input id="fd" class="campo" bind:value={form.documento} minlength="5" required /></div>
      <div><label class="etiqueta" for="fr">Rol *</label><select id="fr" class="campo" bind:value={form.rol}>{#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}</select></div>
    {/if}
    <div><label class="etiqueta" for="fn">Nombres *</label><input id="fn" class="campo" bind:value={form.nombres} required /></div>
    <div><label class="etiqueta" for="fa">Apellidos *</label><input id="fa" class="campo" bind:value={form.apellidos} required /></div>
    <div class="sm:col-span-2"><label class="etiqueta" for="fe">Correo *</label><input id="fe" type="email" class="campo" bind:value={form.email} required /></div>
    <div><label class="etiqueta" for="ft">Teléfono</label><input id="ft" class="campo" bind:value={form.telefono} /></div>
    <div><label class="etiqueta" for="fdp">Dependencia / programa</label><input id="fdp" class="campo" bind:value={form.dependencia} /></div>
    <div class="sm:col-span-2"><label class="etiqueta" for="fp">{editando ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña inicial * (mín. 8)'}</label>
      <div class="relative">
        <input id="fp" type={mostrarPassword ? 'text' : 'password'} class="campo pr-11" value={form.password || ''} on:input={(e) => (form.password = e.currentTarget.value)} minlength="8" required={!editando} />
        <button type="button" class="absolute right-2 top-1/2 flex h-8 w-8 -translate-y-1/2 items-center justify-center rounded-md text-slate-500 hover:bg-slate-100" on:click={() => (mostrarPassword = !mostrarPassword)} aria-label={mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}>{mostrarPassword ? '○' : '◉'}</button>
      </div>
    </div>
    <div class="flex justify-end gap-2 sm:col-span-2"><button type="button" class="btn-secundario" on:click={() => (modal = false)}>Cancelar</button><button class="btn-primario">Guardar</button></div>
  </form>
</Modal>
