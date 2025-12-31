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
- Автоматическая регистрация пользователей из Telegram
- Хранение корзины в базе данных с привязкой к пользователю
- Профиль пользователя с возможностью редактирования

## Безопасность
Приложение реализует комплексные меры безопасности для обеспечения работы только внутри Telegram Web App:

### 1. Валидация данных инициализации Telegram
- Проверяет все входящие запросы с использованием официального протокола аутентификации Telegram
- Проверяет хэш-подписи для предотвращения подделки
- Проверяет актуальность запроса (истекает через 1 час)

### 2. Проверка окружения
- Промежуточное ПО, ограничивающее доступ к конфиденциальным конечным точкам только из Telegram
- Проверяет user agent, заголовки и referer для подтверждения окружения Telegram
- Настройки CORS ограничены только доменами Telegram

### 3. Безопасная связь
- Автоматическое включение данных инициализации Telegram в API-запросы
- Правильная обработка ошибок без раскрытия конфиденциальной информации

Для получения полной информации смотрите [SECURITY.md](SECURITY.md).

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

ssh -p 2222 -R dev:80:localhost:5173 -o ServerAliveInterval=30 172.24.96.1 
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

# 1. Скачать все обновления
git fetch origin

# 2. Перейти в master
git checkout master

# 3. Объединить изменения из ветки
git merge origin/qwen-code-4461e569-ccfa-415b-820c-a4b99df9c068 --no-ff

# 4. Если попросит сообщение - нажать Esc, затем :wq

# 5. Запушить
git push origin master

git commit -m "Merge qwen-code-4461e569-ccfa-415b-820c-a4b99df9c068 branch"    


DATA/
codeProject/.idea
codeProject/frontend/node_modules
codeProject/README.md

user:password


# Создать файл миграции
alembic revision --autogenerate -m "Create users and cart tables"

# Применить миграцию
alembic upgrade head