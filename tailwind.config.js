/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: {
          DEFAULT: '#F8F6F0',
          subtle: '#F2EFE9',
          card: '#FFFFFF',
        },
        forest: {
          50: '#F0F6F3',
          100: '#DDECE4',
          200: '#BCD9CB',
          300: '#94C0AD',
          400: '#64A189',
          500: '#3D8168',
          600: '#2E6652',
          700: '#235041',
          800: '#1A3D32',
          900: '#132C24',
          950: '#0A1813',
        },
        sand: {
          50: '#FAF8F5',
          100: '#F3EFE8',
          200: '#E7E0D3',
          300: '#D5C9B5',
          400: '#BDB098',
          500: '#9E9077',
          600: '#7F725B',
          700: '#615644',
          800: '#463D31',
          900: '#2D271F',
        },
        charcoal: {
          900: '#171A19',
          800: '#252927',
          700: '#383E3B',
          600: '#525B57',
          500: '#6F7A75',
          400: '#95A09A',
          300: '#BAC2BE',
          200: '#DFE3E1',
          100: '#F0F2F1',
        },
        terracotta: {
          500: '#C25E3E',
          600: '#A94E32',
        }
      },
      fontFamily: {
        sans: ['Plus Jakarta Sans', 'Inter', 'system-ui', '-apple-system', 'sans-serif'],
        serif: ['Newsreader', 'Georgia', 'serif'],
      },
      boxShadow: {
        'subtle': '0 1px 3px 0 rgba(20, 30, 25, 0.04), 0 1px 2px -1px rgba(20, 30, 25, 0.04)',
        'card': '0 2px 8px -2px rgba(20, 30, 25, 0.06), 0 1px 4px -1px rgba(20, 30, 25, 0.04)',
        'elevated': '0 10px 25px -5px rgba(20, 30, 25, 0.08), 0 8px 10px -6px rgba(20, 30, 25, 0.04)',
      }
    },
  },
  plugins: [],
};
