import { writable } from 'svelte/store'

function crearSesion() {
  const guardado = localStorage.getItem('usuario')
  const { subscribe, set } = writable(guardado ? JSON.parse(guardado) : null)
  return {
    subscribe,
    iniciar(token, usuario) {
      localStorage.setItem('token', token)
      localStorage.setItem('usuario', JSON.stringify(usuario))
      set(usuario)
    },
    cerrar() {
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      set(null)
    }
  }
}

export const sesion = crearSesion()
export const noLeidas = writable(0)

// Mensajes emergentes (toast)
export const toasts = writable([])
let n = 0
export function avisar(texto, tipo = 'ok') {
  const id = ++n
  toasts.update((t) => [...t, { id, texto, tipo }])
  setTimeout(() => toasts.update((t) => t.filter((x) => x.id !== id)), 4000)
}
