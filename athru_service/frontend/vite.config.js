import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";
import cssInjectedByJs from "vite-plugin-css-injected-by-js";
import path from "path";

// The SPA is served by Frappe's www/athru-service.html, which loads a single
// JS module (/assets/athru_service/frontend/athru_service.js) and no CSS link.
// So we emit ONE self-contained bundle: CSS is injected by the JS at runtime
// and dynamic imports are inlined. The bench never needs npm — the built
// bundle is committed to the repo.
export default defineConfig({
  plugins: [vue(), cssInjectedByJs()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
    },
  },
  build: {
    outDir: "../public/frontend",
    emptyOutDir: true,
    target: "esnext",
    cssCodeSplit: false,
    rollupOptions: {
      output: {
        inlineDynamicImports: true,
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
