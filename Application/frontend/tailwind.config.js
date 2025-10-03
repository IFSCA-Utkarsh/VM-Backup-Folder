/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}", // Scan all JS/JSX files in src/
    "./index.html", // Include index.html
  ],
  theme: {
    extend: {
      colors: {
        'main-text': 'rgb(0, 43, 49)', // Define custom color
        'primary-blue': 'rgb(146, 179, 202)',
        'primary-orange': 'rgb(243, 195, 177)',
        'error-red': 'rgb(208, 69, 82)',
      },
    },
    fontFamily: {
      sans: ['Open Sans', 'sans-serif'],
      urbanist: ['Urbanist', 'sans-serif'],
    },
  },
  plugins: [],
}