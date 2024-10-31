import { defineConfig } from "vite";

export default defineConfig({
  root: "frontend",
  build: {
    Outdir: "dist",
    manifest: "manifest.json",
    rollupOptions: {
      input: ["frontend/index.js", "frontend/styles.scss"],
    },
  },
});