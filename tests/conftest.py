import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import StaticPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import database_url
from app.db.database import Base
from app.main import app
from app.services.product_service import ProductService
from app.services.wb_parser import WildberriesParser

# Установка правильного event loop для Windows
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


# Фикстура для event_loop
@pytest.fixture(scope="function")
def event_loop():
    policy = asyncio.WindowsSelectorEventLoopPolicy()
    loop = policy.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


# Асинхронный движок БД
@pytest.fixture(scope="function")
async def async_engine():
    engine = create_async_engine(
        database_url,
        poolclass=StaticPool,  # важно для тестов
        echo=False,
    )
    yield engine
    await engine.dispose()


# Создание/очистка таблиц перед каждым тестом
@pytest.fixture(scope="function", autouse=True)
async def setup_db(async_engine):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# Асинхронная сессия
@pytest.fixture(scope="function")
async def async_session(async_engine):
    session_maker = async_sessionmaker(bind=async_engine, expire_on_commit=False)
    async with session_maker() as session:
        yield session


# Клиент для тестирования API
@pytest.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


# Мокаем парсер Wildberries
@pytest.fixture
def mock_wb_api():
    with patch("app.services.wb_parser.WildberriesParser.search_products") as mock:
        mock.return_value = [
            {
                "product_id": "213ca78c-bca9-4e9b-aaae-935f0a113322",
                "product_name": "Сумка кросс-боди маленькая",
                "price": 4990.00,
                "discount_price": 1436.00,
                "rating": 5,
                "reviews_count": 287,
            },
            {
                "product_id": "ac99c0da-b9c8-4b69-80b3-a9064415d5e2",
                "product_name": "сумка багет на плечо маленькая",
                "price": 5000.00,
                "discount_price": 1597.00,
                "rating": 5,
                "reviews_count": 5894,
            },
        ]
        yield mock


# Мокаем ProductService
@pytest.fixture
def mock_product_service():
    return AsyncMock(spec=ProductService)


# Инициализируем парсер
@pytest.fixture
def wb_parser(mock_product_service):
    return WildberriesParser(product_service=mock_product_service, limit=10)
