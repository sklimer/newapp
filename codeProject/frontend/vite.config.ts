import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
// export default defineConfig({
//   plugins: [react()],
//   server: {
//     host: true,
//     port: 3000
//   }
// })
export default defineConfig({
  server: {
    host: '0.0.0.0',
    port: 5173,
    allowedHosts: [
      'dev.proxy.example.com',
      'localhost.proxy.example.com',
      'nks.proxy.example.com',
      'w0c.proxy.example.com',
      '0g5.proxy.example.com',
      'proxy.example.com' // Основной домен
    ]
  },
});