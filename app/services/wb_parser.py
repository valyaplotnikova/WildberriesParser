import aiohttp
import json
from typing import List, Dict
from loguru import logger

from app.services.product_service import ProductService


class WildberriesParser:
    """
    Парсер товаров с маркетплейса Wildberries.

    Осуществляет поиск товаров через API Wildberries, парсинг данных и сохранение в БД.
    Поддерживает асинхронные запросы и обработку ошибок.

    Attributes:
        ua (str): User-Agent для HTTP-запросов.
        base_url (str): Базовый URL сайта Wildberries.
        search_url (str): URL API для поиска товаров.
        product_service (ProductService): Сервис для работы с товарами.
        limit (int): Максимальное количество товаров для парсинга.
    """
    def __init__(self, product_service: ProductService, limit: int):
        """
        Инициализация парсера.

        Args:
            product_service: Сервис для сохранения товаров в БД.
            limit: Максимальное количество товаров для парсинга.
        """
        self.ua = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
                   "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0 Safari/537.36")
        self.base_url = "https://www.wildberries.ru"
        self.search_url = "https://search.wb.ru/exactmatch/ru/common/v4/search"
        self.product_service = product_service
        self.limit = limit

    async def search_products(self, query: str) -> List[Dict]:
        """
        Асинхронный поиск товаров через API Wildberries.

        Выполняет запрос к API Wildberries и возвращает список товаров.

        Args:
            query: Поисковый запрос (например, "телефон").

        Returns:
            Список словарей с данными товаров. Каждый словарь содержит:
                - product_id: Идентификатор товара
                - product_name: Название товара
                - price: Цена
                - discount_price: Цена со скидкой (если есть)
                - rating: Рейтинг
                - reviews_count: Количество отзывов
                - product_url: Ссылка на товар
                - category: Категория товара
                - search_query: Поисковый запрос

        Examples:
            >> products = await parser.search_products("телефон")
            >> len(products)
            100
        """
        params = {
            'TestGroup': 'no_test',
            'TestID': 'no_test',
            'appType': '1',
            'curr': 'rub',
            'dest': '-1257786',
            'resultset': 'catalog',
            'sort': 'popular',
            'spp': '0',
            'suppressSpellcheck': 'false',
            'query': query,
            'page': 1,
            'limit': self.limit
        }

        headers = {
            'User-Agent': self.ua,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }

        try:
            logger.info(f"Поиск товаров: {query}")
            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(self.search_url, params=params, ssl=False, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Ошибка ответа от сервера: {response.status}")
                        return []

                    try:
                        data = await response.json()
                    except aiohttp.ContentTypeError:

                        text = await response.text()
                        try:
                            data = json.loads(text)
                        except json.JSONDecodeError:
                            logger.error("Не удалось распарсить ответ как JSON")
                            logger.debug(f"Текст ответа: {text[:500]}...")
                            return []

                    products_data = data.get("data", {}).get("products", [])

                    logger.info(f"API вернул {len(products_data)} товаров, запрошено: {self.limit}")

                    if len(products_data) > self.limit:
                        products_data = products_data[:self.limit]
                        logger.info(f"Ограничили до {self.limit} товаров")

                    return self._parse_products(products_data)

        except aiohttp.ClientError as e:
            logger.error(f"Ошибка запроса: {e}")
            return []
        except json.JSONDecodeError:
            logger.error("Ошибка парсинга JSON")
            return []
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return []

    def _parse_products(self, products_data: List[Dict]) -> List[Dict]:
        """
        Парсинг сырых данных товаров из API Wildberries.

        Преобразует данные из формата API в унифицированный формат.

        Args:
            products_data: Список сырых данных товаров из API.

        Returns:
            Список словарей с обработанными данными товаров.

        Raises:
            Пропускает товары с ошибками парсинга и логирует ошибки.
        """

        parsed_products = []

        for product in products_data:
            try:
                product_id = product.get('id', '')
                product_name = product.get('name', '').strip() or 'Без названия'

                original_price = product.get('priceU', 0)
                sale_price = product.get('salePriceU', 0)

                original_price_rub = original_price / 100 if original_price else 0
                sale_price_rub = sale_price / 100 if sale_price else 0

                if sale_price_rub > 0 and sale_price_rub < original_price_rub:
                    price = original_price_rub
                    discount_price = sale_price_rub
                else:
                    price = sale_price_rub if sale_price_rub > 0 else original_price_rub
                    discount_price = None

                rating = product.get('rating', 0)
                review_count = product.get('feedbacks', 0)

                product_url = f"{self.base_url}/catalog/{product_id}/detail.aspx"

                parsed_product = {
                    'product_id': str(product_id),
                    'product_name': product_name,
                    'price': price,
                    'discount_price': discount_price,
                    'rating': rating,
                    'reviews_count': review_count,
                    'product_url': product_url,
                    'category': '',
                    'search_query': ''
                }

                parsed_products.append(parsed_product)

            except Exception as e:
                logger.error(f"Ошибка парсинга товара: {e}")
                continue

        return parsed_products

    async def parse_and_save(self, query: str, category: str = "") -> int:
        """
        Полный цикл парсинга и сохранения товаров.

        Args:
            query: Поисковый запрос.
            category: Категория товаров (по умолчанию "").

        Returns:
            Количество успешно сохраненных товаров.

        Examples:
            >> saved_count = await parser.parse_and_save("ноутбук")
            >> saved_count
            50
        """
        products_data = await self.search_products(query)

        if not products_data:
            return 0

        for product in products_data:
            product.update({
                'product_id': str(product['product_id']),
                'search_query': query,
                'category': category,
                'product_url': f"{self.base_url}/catalog/{product['product_id']}/detail.aspx"
            })

        return await self.product_service.process_products(products_data)
