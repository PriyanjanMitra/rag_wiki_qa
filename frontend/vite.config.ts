import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [tailwindcss(), react()],
  preview: {
    host: "0.0.0.0",
    port: 4173,
  },
  server: {
    host: "0.0.0.0",
    port: 5173,
    proxy: {
      "/ask": "http://localhost:8000",
      "/health": "http://localhost:8000",
      "/upload": "http://localhost:8000",
      "/uploads": "http://localhost:8000",
    },
  },
});
