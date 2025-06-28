import pytest
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_search_products_success(wb_parser, mock_wb_api):
    products = await wb_parser.search_products("сумки")

    assert len(products) == 2
    assert products[0]["product_name"] == "Сумка кросс-боди маленькая"


@pytest.mark.asyncio
async def test_search_products_empty_response(wb_parser):
    """Тест: API возвращает статус 200, но без данных"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        # Мокаем ответ без данных
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={})  # пустой JSON
        mock_get.return_value.__aenter__.return_value = mock_response

        products = await wb_parser.search_products("пустой_запрос")
        assert len(products) == 0


@pytest.mark.asyncio
async def test_search_products_error_response(wb_parser):
    """Тест ошибки от API"""
    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 500

        products = await wb_parser.search_products("тест")
        assert len(products) == 0


@pytest.mark.asyncio
async def test_parse_and_save_success(wb_parser, mock_product_service):
    """Тест успешного парсинга и сохранения"""
    mock_response = {
        "data": {
            "products": [
                {
                    "id": 123,
                    "name": "Тестовый товар",
                    "priceU": 10000,
                    "salePriceU": 8000,
                    "rating": 4.5,
                    "feedbacks": 25
                }
            ]
        }
    }

    with patch('aiohttp.ClientSession.get') as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)

        # Настраиваем мок сервиса
        mock_product_service.process_products.return_value = 1

        saved_count = await wb_parser.parse_and_save("тест", "категория")

        assert saved_count == 1
        mock_product_service.process_products.assert_called_once()


def test_parse_products(wb_parser):
    """Тест парсинга продуктов"""
    test_data = [
        {
            "id": 123,
            "name": "Тестовый товар",
            "priceU": 10000,
            "salePriceU": 8000,
            "rating": 4.5,
            "feedbacks": 25
        }
    ]

    result = wb_parser._parse_products(test_data)

    assert len(result) == 1
    product = result[0]
    assert product['product_id'] == "123"
    assert product['product_name'] == "Тестовый товар"
    assert product['price'] == 100.0
    assert product['discount_price'] == 80.0
    assert product['rating'] == 4.5
    assert product['reviews_count'] == 25
    assert product['product_url'] == "https://www.wildberries.ru/catalog/123/detail.aspx"