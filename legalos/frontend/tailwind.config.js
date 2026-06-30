/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f0f4ff',
          100: '#dbe5ff',
          200: '#bfd2ff',
          500: '#3b82f6', // Indigo / Royal blue primary
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          dark: '#0f172a' // Dark navy mode slate
        },
        risk: {
          low: '#10b981',    // Green
          medium: '#f59e0b', // Yellow/Amber
          high: '#ef4444'    // Red
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
