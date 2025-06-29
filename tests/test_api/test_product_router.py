import pytest


@pytest.mark.asyncio
async def test_get_product_list_success(async_client):
    """Тест успешного получения списка товаров"""

    response = await async_client.get(
        "/api/products", params={"query": "велосипеды", "limit": 10}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_product_list_by_filter(async_client):
    """Тест успешного получения списка товаров с фильтрами"""

    response = await async_client.get(
        "/api/products",
        params={
            "query": "велосипеды",
            "limit": 10,
            "min_price": 10000,
            "min_rating": 5,
        },
    )
    assert response.status_code == 200
