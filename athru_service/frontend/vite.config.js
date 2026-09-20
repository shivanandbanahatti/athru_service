import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import path from "path";

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "../public/frontend",
    emptyOutDir: true,
    target: "esnext",
    rollupOptions: {
      output: {
        entryFileNames: "athru_service.js",
        chunkFileNames: "chunks/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
      },
    },
  },
  server: {
    port: 8080,
  },
  base: "/assets/athru_service/frontend/",
});
