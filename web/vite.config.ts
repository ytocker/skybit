import { defineConfig } from "vite";

// Skybit web build. We aim for a single self-contained bundle in dist/
// so that opening dist/index.html directly in a browser (no server)
// also works as the "local" version.
export default defineConfig({
  base: "./",
  build: {
    target: "es2022",
    outDir: "dist",
    emptyOutDir: true,
    sourcemap: false,
    cssCodeSplit: false,
    assetsInlineLimit: 0,
    rollupOptions: {
      output: {
        // Single chunk keeps the cold-load HTTP request count low.
        manualChunks: undefined,
      },
    },
  },
  server: {
    port: 5173,
    open: false,
  },
});
