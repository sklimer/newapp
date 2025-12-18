# Restaurant Telegram Mini App Backend

Backend API for restaurant Telegram mini application with payment processing capabilities.

## Features
- Menu management
- Order processing with delivery calculation
- User management and loyalty system
- Payment integration
- Notifications
- Analytics

## Tech Stack
- Python (FastAPI)
- PostgreSQL
- Alembic for migrations
- Telegram Bot API integration
- YooKassa for payments

## Setup
```bash
pip install -r requirements.txt
```

## Running the application
```bash
python -m uvicorn app.main:app --reload
```

## Database Migrations
```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```