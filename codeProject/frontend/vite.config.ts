import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  plugins: [react()],
    server: {
        host: '0.0.0.0',
        port: 5173,
        allowedHosts: [
          'localhost',
          '127.0.0.1',
          '::1',
          '0.0.0.0',
          'dev.proxy.example.com'
        ],

    // ВАЖНО: ВАША ОСОБЕННОСТЬ
    // Так как sish уже работает как прокси, не нужно proxy в Vite
    // Весь трафик будет идти через nginx -> sish -> ваши сервисы

    // Для работы HMR через туннель

    hmr: {
     overlay: true,
    },
    proxy: {
      '/api': {

    target: 'http://localhost:8000',
    changeOrigin: true,
    secure: false,
    rewrite: (path) => path.replace(/^\/api/, '/api/v1'), // Add /v1 to the API path
    },

    },
    // Отключаем встроенный прокси, так как у вас есть nginx + sish
    // proxy: {} - не нужно!
  },

  // Для правильных путей в продакшене
  base: '/',

  // Переменные окружения для API
  define: {
    'import.meta.env.VITE_API_URL': JSON.stringify(process.env.VITE_API_URL || '/api')
  }
})