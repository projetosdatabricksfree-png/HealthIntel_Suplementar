import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/v1": {
        target: process.env.VITE_API_BASE_URL || "http://localhost:8080",
        changeOrigin: true
      },
      "/saude": {
        target: process.env.VITE_API_BASE_URL || "http://localhost:8080",
        changeOrigin: true
      },
      "/prontidao": {
        target: process.env.VITE_API_BASE_URL || "http://localhost:8080",
        changeOrigin: true
      }
    }
  }
});
