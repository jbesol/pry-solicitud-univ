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

<div class="tarjeta mb-4 grid gap-3 p-4 sm:grid-cols-4">
  <div class="sm:col-span-2"><label class="etiqueta" for="uq">Buscar</label><input id="uq" class="campo" placeholder="Nombre, correo o documento" bind:value={f.q} on:input={cargar} /></div>
  <div><label class="etiqueta" for="ur">Rol</label>
    <select id="ur" class="campo" bind:value={f.rol} on:change={cargar}><option value="">Todos</option>{#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}</select></div>
  <div><label class="etiqueta" for="ua">Estado</label>
    <select id="ua" class="campo" bind:value={f.activo} on:change={cargar}><option value="">Todos</option><option value="true">Activos</option><option value="false">Inactivos</option></select></div>
</div>

<div class="tarjeta overflow-x-auto">
  <table class="tabla w-full min-w-[820px]">
    <thead><tr><th>Usuario</th><th>Documento</th><th>Dependencia / programa</th><th>Rol</th><th>Estado</th><th>Creado</th><th></th></tr></thead>
    <tbody>
      {#each lista as u}
        <tr class={u.activo ? '' : 'opacity-60'}>
          <td><p class="font-medium text-slate-800">{u.nombre_completo}</p><p class="text-xs text-slate-500">{u.email}</p></td>
          <td class="font-mono text-xs">{u.documento}</td>
          <td>{u.dependencia || '—'}</td>
          <td>
            <select class="campo w-40 py-1" value={u.rol.codigo} on:change={(e) => cambiarRol(u, e.target.value)} disabled={u.id === $sesion.id}>
              {#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}
            </select>
          </td>
          <td><span class="rounded-full px-2 py-0.5 text-xs font-medium {u.activo ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}">{u.activo ? 'Activo' : 'Inactivo'}</span></td>
          <td class="text-xs">{fechaCorta(u.fecha_creacion)}</td>
          <td class="whitespace-nowrap text-right">
            <button class="btn-fantasma px-2 py-1 text-xs" on:click={() => editar(u)}>Editar</button>
            {#if u.id !== $sesion.id}<button class="btn-fantasma px-2 py-1 text-xs" on:click={() => alternarActivo(u)}>{u.activo ? 'Desactivar' : 'Activar'}</button>{/if}
          </td>
        </tr>
      {:else}
        <tr><td colspan="7" class="py-10 text-center text-slate-400">Sin resultados</td></tr>
      {/each}
    </tbody>
  </table>
</div>

<Modal titulo={editando ? `Editar ${editando.nombre_completo}` : 'Nuevo usuario'} bind:abierto={modal} ancho="max-w-xl">
  <form class="grid grid-cols-2 gap-4" on:submit|preventDefault={guardar}>
    {#if !editando}
      <div><label class="etiqueta" for="fd">Documento *</label><input id="fd" class="campo" bind:value={form.documento} minlength="5" required /></div>
      <div><label class="etiqueta" for="fr">Rol *</label><select id="fr" class="campo" bind:value={form.rol}>{#each Object.entries(ROLES) as [k, v]}<option value={k}>{v}</option>{/each}</select></div>
    {/if}
    <div><label class="etiqueta" for="fn">Nombres *</label><input id="fn" class="campo" bind:value={form.nombres} required /></div>
    <div><label class="etiqueta" for="fa">Apellidos *</label><input id="fa" class="campo" bind:value={form.apellidos} required /></div>
    <div class="col-span-2"><label class="etiqueta" for="fe">Correo *</label><input id="fe" type="email" class="campo" bind:value={form.email} required /></div>
    <div><label class="etiqueta" for="ft">Teléfono</label><input id="ft" class="campo" bind:value={form.telefono} /></div>
    <div><label class="etiqueta" for="fdp">Dependencia / programa</label><input id="fdp" class="campo" bind:value={form.dependencia} /></div>
    <div class="col-span-2"><label class="etiqueta" for="fp">{editando ? 'Nueva contraseña (dejar vacío para no cambiar)' : 'Contraseña inicial * (mín. 8)'}</label>
      <input id="fp" type="password" class="campo" bind:value={form.password} minlength="8" required={!editando} /></div>
    <div class="col-span-2 flex justify-end gap-2"><button type="button" class="btn-secundario" on:click={() => (modal = false)}>Cancelar</button><button class="btn-primario">Guardar</button></div>
  </form>
</Modal>
