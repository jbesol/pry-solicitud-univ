export const ESTADOS = {
  REGISTRADA: { etiqueta: 'Registrada', clase: 'bg-slate-100 text-slate-700 ring-slate-300' },
  ASIGNADA: { etiqueta: 'Asignada', clase: 'bg-brand-50 text-brand-700 ring-brand-200' },
  EN_PROCESO: { etiqueta: 'En proceso', clase: 'bg-amber-50 text-amber-800 ring-amber-200' },
  RESUELTA: { etiqueta: 'Resuelta', clase: 'bg-brand-50 text-brand-700 ring-brand-200' },
  CERRADA: { etiqueta: 'Cerrada', clase: 'bg-zinc-200 text-zinc-700 ring-zinc-300' },
  RECHAZADA: { etiqueta: 'Rechazada', clase: 'bg-rose-50 text-rose-700 ring-rose-200' },
  REABIERTA: { etiqueta: 'Reabierta', clase: 'bg-violet-50 text-violet-700 ring-violet-200' }
}

export const PRIORIDADES = {
  BAJA: { etiqueta: 'Baja', clase: 'text-slate-500', punto: 'bg-slate-400' },
  MEDIA: { etiqueta: 'Media', clase: 'text-brand-700', punto: 'bg-brand-500' },
  ALTA: { etiqueta: 'Alta', clase: 'text-amber-700', punto: 'bg-amber-500' },
  URGENTE: { etiqueta: 'Urgente', clase: 'text-rose-700 font-semibold', punto: 'bg-rose-600' }
}

export const CANALES = { WEB: 'Web', CORREO: 'Correo', PRESENCIAL: 'Presencial', MENSAJERIA: 'Mensajería' }

export const ROLES = {
  ADMINISTRADOR: 'Administrador',
  ESTUDIANTE: 'Estudiante',
  FUNCIONARIO: 'Funcionario',
  SUPERVISOR: 'Supervisor'
}

export const TIPOS_MOV = {
  REGISTRO: 'Registro',
  ASIGNACION: 'Asignación',
  CAMBIO_ESTADO: 'Cambio de estado',
  OBSERVACION: 'Observación',
  EDICION: 'Edición'
}

const aFecha = (v) => (v ? new Date(v) : null)

export function fecha(v, conHora = true) {
  const d = aFecha(v)
  if (!d) return '—'
  return d.toLocaleString('es-CO', {
    day: '2-digit', month: 'short', year: 'numeric',
    ...(conHora ? { hour: '2-digit', minute: '2-digit' } : {})
  })
}

export function relativo(v) {
  const d = aFecha(v)
  if (!d) return ''
  const s = (Date.now() - d.getTime()) / 1000
  if (s < 60) return 'hace un momento'
  if (s < 3600) return `hace ${Math.floor(s / 60)} min`
  if (s < 86400) return `hace ${Math.floor(s / 3600)} h`
  if (s < 86400 * 30) return `hace ${Math.floor(s / 86400)} d`
  return fecha(v, false)
}

export function iniciales(nombre = '') {
  return nombre.split(' ').filter(Boolean).slice(0, 2).map((p) => p[0]).join('').toUpperCase()
}

export function fechaCorta(v) {
  const d = aFecha(v)
  return d ? d.toLocaleDateString('es-CO', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—'
}
