from datetime import datetime

import pytest

from app.repositories.product_repo import ProductRepository


@pytest.mark.asyncio
async def test_create_product(async_session):
    repo = ProductRepository(async_session)
    data = {
        "product_id": "123",
        "product_name": "Test Product",
        "price": 1000,
        "discount_price": 555.55,
        "rating": 4.3,
        "reviews_count": 8,
        "product_url": "test_url",
        "category": "Category",
        "search_query": "Test_query",
        "created_at": datetime.now()
    }
    product = await repo.create_or_update(data)
    assert product.id is not None
    assert product.product_id == "123"

    data = {
        "product_id": product.id,
        "product_name": "Test Product",
        "price": 1000,
        "discount_price": 555.55,
        "rating": 5,
        "reviews_count": 8,
        "product_url": "test_url",
        "category": "Category",
        "search_query": "Test_query",
        "created_at": datetime.now()
    }

    product = await repo.create_or_update(data)
    assert product.rating == 5
