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
    // PERFORMANCE OPTIMIZATION: Code splitting and minification
    rollupOptions: {
      output: {
        manualChunks: {
          // Separate vendor chunks for better caching
          'vendor-react': ['react', 'react-dom', 'react-router-dom'],
          'vendor-d3': ['d3'],
          'vendor-three': ['three', 'ogl'],
          'vendor-animations': ['gsap', 'framer-motion'],
          'vendor-pdf': ['html2pdf.js'],
          'vendor-charts': ['react-countup', 'react-intersection-observer'],
          'vendor-icons': ['@fortawesome/fontawesome-free', 'feather-icons']
        },
        // Optimize chunk file names
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]'
      }
    },
    // Enable minification and tree-shaking
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,  // Remove console.logs in production
        drop_debugger: true, // Remove debugger statements
        pure_funcs: ['console.log', 'console.info', 'console.debug'], // Remove specific console methods
        passes: 2 // Run compression twice for better results
      },
      mangle: {
        safari10: true // Fix Safari 10 issues
      }
    },
    // Chunk size warning
    chunkSizeWarningLimit: 500, // Warn if chunk exceeds 500KB
    // Enable source maps for production debugging (can disable for smaller builds)
    sourcemap: false,
    // Optimize asset inlining
    assetsInlineLimit: 4096, // Inline assets smaller than 4KB
    // Report compressed size
    reportCompressedSize: true,
    // CSS code splitting
    cssCodeSplit: true
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
