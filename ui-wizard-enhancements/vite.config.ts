import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";
import path from "path";
import { componentTagger } from "lovable-tagger";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  server: {
    host: "::",
    port: 8080,
    proxy: {
      // Proxy API requests to Flask backend during development
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      // Proxy video stream requests
      '/video': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      // Proxy index route for starting yoga practice sessions
      '/index': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      // Proxy static assets (images, css, etc.)
      '/static': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
      // Proxy chart data route
      '/charts': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      }
    },
  },
  plugins: [
    react(),
    mode === 'development' &&
    componentTagger(),
  ].filter(Boolean),
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
}));
