# Telegram Mini App для Ресторана

## Описание
Telegram-мини-приложение для ресторанов с возможностью заказа еды с доставкой и самовывозом, онлайн-оплатой, бонусной системой и аналитикой.

## Функциональность
- Просмотр меню
- Оформление заказов (доставка/самовывоз)
- Расчет стоимости доставки
- Управление клиентской базой
- Рассылки
- Бонусная система
- Аналитика заказов

## Технологии
- **Frontend**: React + Vite + TypeScript (на Vercel)
- **Backend**: Python (FastAPI) (на Render)
- **База данных**: PostgreSQL
- **Платежи**: ЮKassa + наличные

## Установка

### 1. Клонирование репозитория
```bash
git clone <your-repo-url>
cd /workspace
```

### 2. Установка зависимостей

#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 3. Настройка окружения

Создайте файл `.env` в папке `backend/`:
```env
DATABASE_URL=postgresql://username:password@localhost/dbname
TELEGRAM_BOT_TOKEN=your_bot_token
YOOKASSA_SHOP_ID=your_shop_id
YOOKASSA_SECRET_KEY=your_secret_key
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Создайте файл `.env` в папке `frontend/`:
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Миграции базы данных
```bash
cd backend
alembic upgrade head
```

### 5. Запуск приложения

#### Backend
```bash
cd backend
uvicorn app.main:app --reload

#### Frontend
```bash
cd frontend
npm run dev
```
### Запуск сервера в git bash 
```bash
cd frontend
ssh -p 2222 dev.proxy.example.com -R dev:80:localhost:5173
```


## Настройка Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен
3. Установите webhook:
   ```
   https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://<your-domain>/webhook
   ```

## Настройка платежей (ЮKassa)

1. Зарегистрируйтесь в [личном кабинете ЮKassa](https://yookassa.ru/)
2. Получите `Shop ID` и `Secret Key`
3. Укажите webhook URL для уведомлений о платежах

## Продакшн-развертывание

- Frontend: разместите на Vercel
- Backend: разместите на Render
- Используйте HTTPS для webhook'ов
- Настройте переменные окружения на сервере

## Структура проекта
```
/workspace
├── backend/              # FastAPI сервер
│   ├── alembic/          # Миграции
│   ├── app/
│   │   ├── api/          # Эндпоинты
│   │   ├── core/         # Конфигурация
│   │   ├── models/       # Модели БД
│   │   └── schemas/      # Pydantic-схемы
│   └── requirements.txt
└── frontend/             # React/Vite приложение
    ├── public/
    ├── src/
    │   ├── components/   # Компоненты UI
    │   ├── pages/        # Страницы приложения
    │   ├── api/          # API запросы
    │   └── store/        # Хранилище Zustand
    └── package.json
```