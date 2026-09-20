module.exports = {
  content: ["./index.html", "./src/**/*.{vue,js}"],
  theme: {
    extend: {
      colors: {
        athru: {
          ink: "#0f172a",
          muted: "#64748b",
          surface: "#f8fafc",
          panel: "#ffffff",
          accent: "#0f766e",
          accentSoft: "#ccfbf1",
          line: "#e2e8f0",
          warn: "#b45309",
        },
      },
      fontFamily: {
        sans: ["IBM Plex Sans", "Segoe UI", "system-ui", "sans-serif"],
        display: ["IBM Plex Sans", "Segoe UI", "system-ui", "sans-serif"],
      },
      boxShadow: {
        soft: "0 1px 2px rgba(15,23,42,.06), 0 8px 24px rgba(15,23,42,.04)",
      },
    },
  },
  plugins: [],
};
