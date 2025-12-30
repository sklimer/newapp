import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    
    // Standard HMR configuration for direct connection
    hmr: {
      overlay: true,
    },

    // If you need WebSocket configuration for special network setups
    // ws: true  // Enable WebSocket (default behavior)
  },

  // Для правильных путей в продакшене
  base: '/',

  // Переменные окружения для API
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api')
  }
})