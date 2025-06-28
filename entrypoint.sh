#!/bin/bash
set -e

# Ждём готовности БД
until psql postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@db/$POSTGRES_DB -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

# Применяем миграции
alembic upgrade head

# Запускаем приложение
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload