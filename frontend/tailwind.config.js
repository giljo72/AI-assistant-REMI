/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Primary Colors
        background: '#0E1C2D',
        white: '#FFFFFF',
        'white-gray': '#C2C1C1',
        'dark-gray': '#706E6E',
        
        // Yellows
        yellow: {
          DEFAULT: '#FCC000',
          dark: '#66500E',
        },
        
        // Blues
        'faded-blue': {
          DEFAULT: '#315074',
          2: '#182739',
          3: '#1E3147',
        },
        'faded-bright-blue': '#8F97B7',
        'bright-blue': '#32CEFF',
        'dark-bright-blue': '#2b38dd',
        
        // Greens
        green: {
          DEFAULT: '#67BD6D',
          dark: '#3A703E',
        },
        
        // Reds
        red: {
          DEFAULT: '#CF5362',
          dark: '#79202B',
        },
        
        // Oranges
        orange: {
          DEFAULT: '#FF8B21',
          dark: '#8F520C',
        },
        
        // Purples
        purple: {
          DEFAULT: '#BD46EF',
          dark: '#6C238B',
        },
        
        // Legacy colors
        navy: {
          lighter: '#1e2735',
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