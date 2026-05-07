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
        muted: "var(--muted)",
        destructive: "var(--destructive)",
      },
      boxShadow: {
        sm: "0 1px 2px rgba(15, 23, 42, 0.08)",
        md: "0 6px 18px rgba(15, 23, 42, 0.08)",
        lg: "0 10px 25px rgba(15, 23, 42, 0.12)",
        xl: "0 18px 40px rgba(15, 23, 42, 0.16)",
      },
    },
  },
  plugins: [],
}