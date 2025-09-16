/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    include: [
      'src/test/integration/**/*.{test,spec}.{js,jsx,ts,tsx}'
    ],
    testTimeout: 30000,
    hookTimeout: 30000
  }
})