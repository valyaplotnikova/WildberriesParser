# Wildberries Parser

Парсер товаров с Wildberries с сохранением данных в PostgreSQL и API интерфейсом на FastAPI.

## 📌 О проекте

Этот проект предоставляет:
- Парсинг товаров с Wildberries по ключевым словам
- Сохранение данных в базу PostgreSQL
- REST API для доступа к данным
- Документацию API через Swagger UI

## 🛠 Технологии

- **Python 3.12**
- **FastAPI** - веб-фреймворк
- **SQLAlchemy + asyncpg** - работа с БД
- **Alembic** - миграции базы данных
- **PostgreSQL 16** - база данных
- **Docker** - контейнеризация
- **Uvicorn** - ASGI сервер

## 🚀 Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.12 (если запускаете без Docker)

### Запуск с Docker (рекомендуется)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/valyaplotnikova/WildberriesParser.git
   cd WildberriesParser
   ```

2. Создайте файл `.env` на основе `.env.example`:
   ```bash
   cp .env.example .env
   ```

3. Запустите сервисы:
   ```bash
   docker-compose up --build
   ```

4. Приложение будет доступно по адресу: [http://localhost:8000](http://localhost:8000)

### Ручная установка (без Docker)

1. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

2. Настройте PostgreSQL и обновите строку подключения в `.env`

3. Примените миграции:
   ```bash
   alembic upgrade head
   ```

4. Запустите сервер:
   ```bash
   uvicorn app.main:app --reload
   ```

## 🌐 API Endpoints

Доступные API endpoints (Swagger UI):
- `GET /docs` - интерактивная документация
- `GET /api/products` - список товаров и запуск парсинга


Пример запроса:
```bash
curl -X 'GET' \
  'http://localhost:8000/api/products?query=сумка&limit=50&min_price=1000&min_rating=5' \
  -H 'accept: application/json'
```
