import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import fs from 'fs'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: ['dev.proxy.example.com'],

    // ВАЖНО: ВАША ОСОБЕННОСТЬ
    // Так как sish уже работает как прокси, не нужно proxy в Vite
    // Весь трафик будет идти через nginx -> sish -> ваши сервисы

    // Для работы HMR через туннель


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