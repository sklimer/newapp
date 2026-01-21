import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Проверяем, находимся ли мы на Vercel
const isVercel = process.env.VERCEL === '1'
const isProduction = process.env.NODE_ENV === 'production' || isVercel

export default defineConfig({
  plugins: [react()],

  base: isVercel ? '/' : './',

  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: isProduction ? 'esbuild' : false,
    rollupOptions: isProduction ? {
      output: {
        manualChunks: isVercel ? undefined : {
          vendor: ['react', 'react-dom'],
          ui: ['@reduxjs/toolkit', 'react-redux']
        }
      }
    } : undefined
  },

  server: !isProduction ? {
    allowedHosts: ['dev.proxy.example.com'], // добавьте сюда ваш хост
    host: '0.0.0.0',
    port: 5173,
    hmr: { overlay: true },
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      },
    },
  } : undefined,

  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(
      isVercel
        ? 'https://newapp-c2js.onrender.com/api/v1'
        : process.env.VITE_API_URL || 'http://localhost:8000/api/v1'
    )
  }
})