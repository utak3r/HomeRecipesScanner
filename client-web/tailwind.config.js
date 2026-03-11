/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Outfit', 'sans-serif'],
      },
      colors: {
        brand: {
          50: '#fdf8f6',
          100: '#f2e8e5',
          200: '#eaddd7',
          300: '#e0cec7',
          400: '#d2bab0',
          500: '#a37c68',
          600: '#866352',
          700: '#6b4e40',
          800: '#513b31',
          900: '#392922',
        },
        accent: {
          DEFAULT: '#e65c00',
          light: '#ff771a',
          dark: '#b34700',
        }
      },
      boxShadow: {
        'soft': '0 10px 40px -10px rgba(0,0,0,0.08)',
        'lift': '0 20px 50px -20px rgba(230,92,0,0.15)',
      }
    },
  },
  plugins: [],
}
