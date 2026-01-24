import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      components: path.resolve(__dirname, "src/components"),
      contexts: path.resolve(__dirname, "src/contexts"),
      interfaces: path.resolve(__dirname, "src/interfaces"),
      pages: path.resolve(__dirname, "src/pages"),
      scripts: path.resolve(__dirname, "src/scripts"),
      styles: path.resolve(__dirname, "src/styles"),
    },
  },
});
