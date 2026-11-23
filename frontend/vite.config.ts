import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
// import { visualizer } from "rollup-plugin-visualizer";

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    //visualizer({ open: true, gzipSize: true, brotliSize: true }),
  ],
  resolve: { alias: { "@": path.resolve(import.meta.dirname, "./src") } },
  build: {
    outDir: "../backend/static",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules/highlight.js")) {
            return "highlight.js";
          }
          if (id.includes("node_modules/xlsx/xlsx")) {
            return "xlsx";
          }
          // All node_modules go into vendor chunk
          if (id.includes("node_modules")) {
            return "vendor";
          }
        },
      },
    },
  },
  base: "/app",
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000", // FastAPI server
        changeOrigin: true,
      },
      "/login": {
        target: "http://localhost:8000", // FastAPI server
        changeOrigin: true,
      },
      // use a negative lookahead: match "/" but not "/app"
      "^/(?!app)(.*)": {
        target: "http://localhost:8000",
        changeOrigin: true,
        // keep path as-is
        rewrite: (path) => path,
      },
    },
  },
});
