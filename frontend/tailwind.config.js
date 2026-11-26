/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{svelte,js}'],
  theme: {
    extend: {
      colors: {
        // Azul institucional CUL (Barranquilla): corporativo, sobrio y poco saturado.
        brand: {
          50: '#f2f6fb',
          100: '#dfe9f4',
          200: '#bfd3e7',
          500: '#4c82b4',
          600: '#2f6699',
          700: '#27567f',
          800: '#1f4466',
          900: '#17324c'
        }
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'] }
    }
  },
  plugins: []
}
