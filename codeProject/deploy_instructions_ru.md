# Детальные инструкции по деплою проекта на Vercel и Render

## Общая архитектура проекта

Ваш проект представляет собой Telegram Mini App с:
- Frontend: React + Vite + TypeScript (размещается на Vercel)
- Backend: Python (FastAPI) (размещается на Render)
- База данных: PostgreSQL
- Платежи: ЮKassa + наличные

## Деплой фронтенда на Vercel

### Шаг 1: Подготовка кода

1. Убедитесь, что ваш репозиторий с исходным кодом находится в публичном доступе (GitHub, GitLab или Bitbucket).
2. Убедитесь, что ваш frontend-код находится в папке `/frontend`.

### Шаг 2: Регистрация и настройка на Vercel

1. Зайдите на сайт [vercel.com](https://vercel.com) и создайте аккаунт.
2. Нажмите "Continue with GitHub/GitLab/Bitbucket" для подключения вашего аккаунта.
3. Нажмите "New Project" → "Import Git Repository".
4. Выберите ваш репозиторий с проектом.
5. Vercel автоматически определит, что это React/Vite проект.

### Шаг 3: Конфигурация сборки

1. В настройках проекта (Settings → Build & Development Settings):
   - Framework Preset: `Vite`
   - Root Directory: `/frontend`

2. В разделе Environment Variables добавьте следующие переменные:
   - `VITE_API_URL`: URL вашего backend API (например, `https://your-backend.onrender.com/api`)

3. В разделе Build Commands:
   - Build Command: `npm run build` или `yarn build`
   - Output Directory: `dist`
   - Install Command: `npm install` или `yarn install`

### Шаг 4: Настройка файла `vite.config.ts` для продакшена

Обновите ваш `frontend/vite.config.ts` для корректной работы в продакшене:

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  base: './',

  // Конфигурация для продакшена
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          ui: ['@reduxjs/toolkit', 'react-redux']
        }
      }
    }
  },

  // Для прокси в режиме разработки
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, '/api/v1'),
      }
    }
  }
})
```

### Шаг 5: Деплой

1. После сохранения настроек Vercel автоматически начнет сборку проекта.
2. По завершении вы получите URL для доступа к вашему приложению (например, `https://your-project.vercel.app`).

## Деплой бэкенда на Render

### Шаг 1: Подготовка проекта для Render

1. Создайте файл `Procfile` в корне вашего проекта (в папке `/codeProject`) с содержимым:
   ```
   web: uvicorn backend.app.main:app --host=0.0.0.0 --port=${PORT:-10000}
   ```

2. Убедитесь, что в вашем `backend/app/main.py` настроено правильное подключение к базе данных через переменные окружения.

### Шаг 2: Регистрация и настройка на Render

1. Зайдите на сайт [render.com](https://render.com) и создайте аккаунт.
2. Нажмите "New +" → "Web Service".
3. Выберите ваш репозиторий с проектом.

### Шаг 3: Конфигурация Web Service

1. Name: введите имя вашего сервиса (например, `telegram-mini-app-backend`)
2. Runtime: `Python`
3. Build Command:
   ```
   cd /workspace/codeProject && pip install -r requirements.txt
   ```
4. Start Command:
   ```
   cd /workspace/codeProject && uvicorn backend.app.main:app --host=0.0.0.0 --port=$PORT
   ```

### Шаг 4: Настройка переменных окружения

В разделе Environment Variables добавьте следующие переменные:

```
DATABASE_URL: postgresql://postgres:admin@localhost/res_db
TELEGRAM_BOT_TOKEN: 6700097759:AAHJgbMFkgOBYv13NfTKoYFmhnn9kx-1npo
SECRET_KEY: 6700097759:AAHJgbMFkgOBYv13NfTKoYFmhnn9kx-1npo
ALGORITHM: HS256
ACCESS_TOKEN_EXPIRE_MINUTES: 30
DEBUG: False
LOG_LEVEL: INFO
HOST: 0.0.0.0
PORT: 10000
postgresql://res_db_user:S0ykpH6FI2UAGUSsHVkcGlEMlrhSBFJY@dpg-d5n9nln5r7bs73dkso4g-a/res_db
```

### Шаг 5: Настройка PostgreSQL базы данных на Render

1. На главной странице Render нажмите "New +" → "PostgreSQL".
2. Укажите имя для базы данных.
3. После создания скопируйте строку подключения (Database URL).
4. Вернитесь к вашему Web Service и обновите значение переменной `DATABASE_URL` на полученную строку подключения.

### Шаг 6: Запуск деплоя

1. Нажмите "Create Web Service".
2. Render начнет процесс сборки и деплоя вашего приложения.
3. После завершения вы получите URL для вашего backend (например, `https://your-backend.onrender.com`).

## Дополнительная настройка безопасности

### Настройка CORS для продакшена

Обновите настройки CORS в `backend/app/main.py` для работы с вашим доменом на Vercel:

```python
# 2. CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-project.vercel.app",  # Домен вашего frontend на Vercel
        "https://*.vercel.app",  # Для Preview-деплоев
        "https://yourdomain.com",  # Ваш собственный домен (если используется)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Настройка Webhook для Telegram Bot

После деплоя выполните настройку webhook для вашего Telegram бота:

```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook?url=https://<YOUR_BACKEND_URL>/webhook
```

Замените `<YOUR_BOT_TOKEN>` на токен вашего бота и `<YOUR_BACKEND_URL>` на URL вашего backend на Render.

## Настройка доменного имени (опционально)

### На Vercel:
1. В настройках проекта перейдите в раздел "Domains".
2. Добавьте ваш собственный домен или используйте поддомен Vercel.

### На Render:
1. В настройках Web Service перейдите в раздел "Domains".
2. Добавьте ваш собственный домен или используйте домен Render.

## Тестирование деплоя

1. Проверьте, что frontend доступен по URL Vercel.
2. Проверьте, что backend доступен по URL Render и отдает здоровье сервиса:
   ```
   GET https://your-backend.onrender.com/health
   ```
3. Проверьте работу API endpoints:
   ```
   GET https://your-backend.onrender.com/api/versions
   ```
4. Протестируйте приложение в Telegram Web App с использованием вашего домена Vercel как frontend.

## Возможные проблемы и решения

### Проблемы с CORS:
- Убедитесь, что домен Vercel добавлен в список разрешенных origins в настройках CORS backend.

### Проблемы с подключением к базе данных:
- Проверьте правильность строки подключения DATABASE_URL.
- Убедитесь, что база данных запущена и доступна.

### Проблемы с производительностью:
- Убедитесь, что вы выбрали подходящий план на Render в зависимости от нагрузки.
- Для высоконагруженных приложений рассмотрите использование пула соединений с базой данных.

## Обновление приложения

### Для Vercel:
- Любые изменения в ветке репозитория, связанной с Vercel, будут автоматически триггерить новый деплой.

### Для Render:
- Любые изменения в репозитории будут автоматически триггерить пересборку и деплой.
- Также можно вручную запустить деплой через кнопку "Manual Deploy".

## Мониторинг и логирование

### На Vercel:
- Используйте вкладку "Logs" в интерфейсе проекта для просмотра логов.

### На Render:
- Используйте вкладку "Logs" в интерфейсе Web Service для просмотра логов приложения.
- Для более подробного логирования установите LOG_LEVEL в значение DEBUG (временно, для отладки).

После выполнения этих шагов ваше приложение должно быть успешно развернуто на Vercel (фронтенд) и Render (бэкенд).