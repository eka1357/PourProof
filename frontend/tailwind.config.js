/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: '#0b1116',
        surface: {
          DEFAULT: '#111a21',
          raised: '#19242c',
          card: '#141f27',
        },
        border: {
          DEFAULT: '#2a3943',
          light: '#3b4e5b',
          subtle: '#1f2b33',
        },
        brand: {
          text: '#edf3f5',
          muted: '#a0afb8',
          primary: '#65d9c1',
          'primary-foreground': '#071310',
          info: '#81b9ff',
          warning: '#f3bf69',
          danger: '#ff7777',
          success: '#68d6a3',
          focus: '#b3e9ff',
        },
      },
      fontFamily: {
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'Menlo', 'Monaco', 'Consolas', 'monospace'],
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
