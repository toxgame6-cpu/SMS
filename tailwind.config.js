 
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './accounts/templates/**/*.html',
    './dashboard/templates/**/*.html',
    './students/templates/**/*.html',
    './staff/templates/**/*.html',
    './notifications/templates/**/*.html',
    './announcements/templates/**/*.html',
    './permissions_app/templates/**/*.html',
    './reports/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#4f46e5',
        secondary: '#64748b',
      },
    },
  },
  plugins: [],
}