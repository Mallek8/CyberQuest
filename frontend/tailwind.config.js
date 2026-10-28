/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#05080f",
        panel: "#0d1422",
        line: "#1c2a40",
        mint: "#3dffb0",
      },
      fontFamily: {
        sans: ["Outfit", "Segoe UI", "sans-serif"],
        mono: ["IBM Plex Mono", "ui-monospace", "monospace"],
      },
      boxShadow: {
        glow: "0 0 40px rgba(62, 224, 255, 0.12)",
      },
    },
  },
  plugins: [],
};
