/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{svelte,js}'],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f1f7f9',
          100: '#dbeaf0',
          200: '#b8d4de',
          500: '#4d96a8',
          600: '#397d91',
          700: '#2f687a',
          800: '#244f5e',
          900: '#173a47'
        }
      },
      fontFamily: { sans: ['Inter', 'system-ui', 'Segoe UI', 'Roboto', 'sans-serif'] }
    }
  },
  plugins: []
}
