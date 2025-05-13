/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          lighter: '#1e2735', // Add this new, slightly lighter navy color
          light: '#121922',
          DEFAULT: '#080d13',
        },
        gold: {
          DEFAULT: '#FFC000',
        }
      },
    },
  },
  plugins: [],
}