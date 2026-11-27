<script>
  import { createEventDispatcher } from 'svelte'
  import { navigate } from 'svelte-routing'
  import { api } from '../lib/api.js'
  import { avisar } from '../lib/stores.js'
  import { CANALES, PRIORIDADES } from '../lib/formato.js'
  import Modal from './Modal.svelte'

  export let abierto = false
  const dispatch = createEventDispatcher()
  let categorias = []
  let form = vacio()
  let enviando = false

  function vacio() {
    return { asunto: '', descripcion: '', categoria_id: '', prioridad: 'MEDIA', canal: 'WEB' }
  }
  $: if (abierto && categorias.length === 0) api('/categorias').then((c) => (categorias = c)).catch(() => {})
  $: catSel = categorias.find((c) => c.id === +form.categoria_id)

  async function enviar() {
    enviando = true
    try {
      const s = await api('/solicitudes', { method: 'POST', body: { ...form, categoria_id: +form.categoria_id } })
      avisar(`Solicitud ${s.codigo} registrada`)
      abierto = false
      form = vacio()
      dispatch('creada', s)
      navigate(`/solicitudes/${s.id}`)
    } catch (e) {
      avisar(e.message, 'error')
    } finally {
      enviando = false
    }
  }
</script>

<Modal titulo="Registrar nueva solicitud" bind:abierto ancho="max-w-xl">
  <form class="space-y-4" on:submit|preventDefault={enviar}>
    <div>
      <label class="etiqueta" for="cat">Categoría *</label>
      <select id="cat" class="campo" bind:value={form.categoria_id} required>
        <option value="" disabled>Seleccione el tipo de servicio…</option>
        {#each categorias as c}<option value={c.id}>{c.nombre}</option>{/each}
      </select>
      {#if catSel}
        <p class="mt-1 text-xs text-slate-500">{catSel.descripcion || ''} · Responde: {catSel.dependencia || '—'} · Tiempo estimado: {catSel.tiempo_respuesta_horas} h</p>
      {/if}
    </div>
    <div>
      <label class="etiqueta" for="asunto">Asunto *</label>
      <input id="asunto" class="campo" bind:value={form.asunto} minlength="5" maxlength="150" required placeholder="Ej. Certificado de notas 2026-1" />
    </div>
    <div>
      <label class="etiqueta" for="desc">Descripción *</label>
      <textarea id="desc" class="campo" rows="5" bind:value={form.descripcion} minlength="10" maxlength="5000" required placeholder="Explique su solicitud con el mayor detalle posible"></textarea>
    </div>
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
      <div>
        <label class="etiqueta" for="prio">Prioridad</label>
        <select id="prio" class="campo" bind:value={form.prioridad}>
          {#each Object.entries(PRIORIDADES) as [k, p]}<option value={k}>{p.etiqueta}</option>{/each}
        </select>
      </div>
      <div>
        <label class="etiqueta" for="canal">Canal de origen</label>
        <select id="canal" class="campo" bind:value={form.canal}>
          {#each Object.entries(CANALES) as [k, v]}<option value={k}>{v}</option>{/each}
        </select>
      </div>
    </div>
    <div class="flex flex-col-reverse gap-2 pt-2 sm:flex-row sm:justify-end">
      <button type="button" class="btn-secundario" on:click={() => (abierto = false)}>Cancelar</button>
      <button class="btn-primario" disabled={enviando}>{enviando ? 'Registrando…' : 'Registrar solicitud'}</button>
    </div>
  </form>
</Modal>
