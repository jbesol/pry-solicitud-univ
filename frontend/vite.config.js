import { svelte } from '@sveltejs/vite-plugin-svelte'
import { defineConfig } from 'vite'

// En desarrollo las llamadas a /api se redirigen al backend local (uvicorn en el puerto 8000)
export default defineConfig({
  plugins: [svelte()],
  server: {
    port: 5173,
    proxy: { '/api': { target: process.env.VITE_API_TARGET || 'http://localhost:8000', changeOrigin: true } }
  }
})
