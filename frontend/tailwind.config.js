/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{svelte,js}'],
  theme: {
    extend: {
      colors: {
        brand: { 50: '#eef6f6', 100: '#d4e9ea', 200: '#a9d3d5', 500: '#1f7a80', 600: '#17646a', 700: '#124f54', 800: '#0e3d41', 900: '#0b2f32' }
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'] }
    }
  },
  plugins: []
}
