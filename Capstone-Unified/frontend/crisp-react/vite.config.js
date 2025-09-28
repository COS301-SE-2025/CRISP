import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react({
    // PERFORMANCE: Disable strict development features for faster performance
    fastRefresh: true,
    babel: {
      compact: false, // Disable compact mode for faster builds
      minified: false // Disable minification in dev for speed
    }
  })],
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        manualChunks: undefined,
      }
    }
  },
  base: '/',
  // PERFORMANCE: Development optimizations
  esbuild: {
    logOverride: { 'this-is-undefined-in-esm': 'silent' }, // Reduce warning spam
  },
  optimizeDeps: {
    include: ['react', 'react-dom', 'd3', 'react-router-dom'], // Pre-bundle heavy deps
    force: false // Don't force re-optimization
  },
  server: {
    hmr: {
      overlay: false // Disable error overlay for performance
    },
    headers: {
      'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; connect-src 'self' http://localhost:8000 ws://localhost:8000 ws://localhost:5173 ws://localhost:3000; img-src 'self' data: blob:; font-src 'self' data:;"
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/admin': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/taxii2': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  }
})
