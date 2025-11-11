/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          red: '#DC2626', // Red-600 - primary brand color
          white: '#FFFFFF',
        },
        secondary: {
          'red-light': '#F87171', // Red-400 - lighter accent
          'red-dark': '#991B1B', // Red-800 - darker accent
          'gray': '#6B7280', // Gray-500 - neutral text
        },
      },
      minHeight: {
        'touch': '44px', // Minimum touch target size per constitution
      },
      minWidth: {
        'touch': '44px', // Minimum touch target size per constitution
      },
    },
  },
  plugins: [],
}
