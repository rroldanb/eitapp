/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "../../../**/*.{html,py,js}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#667eea',
        secondary: '#764ba2',
        accent: '#667eea',
      }
    }
  },
  plugins: [],
}
