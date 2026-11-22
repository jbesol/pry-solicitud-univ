// Cliente HTTP de la API. Adjunta el token JWT y traduce errores a mensajes legibles.
import { navigate } from 'svelte-routing'
import { sesion } from './stores.js'

const BASE = import.meta.env.VITE_API_URL || ''

export async function api(endpoint, { method = 'GET', body, raw = false } = {}) {
  const headers = {}
  const token = localStorage.getItem('token')
  if (token) headers.Authorization = `Bearer ${token}`
  if (body !== undefined) headers['Content-Type'] = 'application/json'

  const res = await fetch(BASE + '/api' + endpoint, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined
  })

  if (res.status === 401 && !endpoint.startsWith('/auth/login')) {
    sesion.cerrar()
    navigate('/', { replace: true })
  }
  if (!res.ok) {
    let detalle = `Error ${res.status}`
    try {
      const j = await res.json()
      if (j.detail) detalle = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)
    } catch {}
    throw new Error(detalle)
  }
  if (raw) return res
  if (res.status === 204) return null
  return res.json()
}

// Construye ?a=1&b=2 omitiendo valores vacíos
export function qs(params) {
  const p = Object.entries(params).filter(([, v]) => v !== '' && v !== null && v !== undefined)
  return p.length ? '?' + new URLSearchParams(p).toString() : ''
}
