/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: "var(--primary)",
        border: "var(--border)",
        card: "var(--card)",
      },
      boxShadow: {
        // These are the "hard" shadows from the theme you shared
        sm: "3px 3px 0px 0px hsl(0 0% 0% / 1.00)",
        md: "3px 3px 0px 0px hsl(0 0% 0% / 1.00), 3px 2px 4px -1px hsl(0 0% 0% / 1.00)",
        lg: "3px 3px 0px 0px hsl(0 0% 0% / 1.00), 3px 4px 6px -1px hsl(0 0% 0% / 1.00)",
        xl: "3px 3px 0px 0px hsl(0 0% 0% / 1.00), 3px 8px 10px -1px hsl(0 0% 0% / 1.00)",
      },
    },
  },
  plugins: [],
}