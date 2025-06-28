from decimal import Decimal
from typing import Optional, List

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.repositories.product_repo import ProductRepository


class ProductService:
    """
    Сервис для работы с товарами в базе данных.

    Обеспечивает бизнес-логику по обработке товаров, включая:
    - Пакетное сохранение/обновление товаров
    - Получение отфильтрованных списков товаров
    - Взаимодействие с репозиторием товаров

    Attributes:
        session (AsyncSession): Асинхронная сессия для работы с БД
        repo (ProductRepository): Репозиторий для операций с товарами
    """
    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса товаров.
        :param session: Асинхронная сессия SQLAlchemy для работы с БД
        """
        self.session = session
        self.repo = ProductRepository(session)

    async def process_products(self, products_data: list[dict]) -> int:
        """
        Пакетная обработка и сохранение товаров.

        Принимает сырые данные товаров, валидирует и сохраняет в БД.
        Если товар существует - обновляет его данные.
        :param products_data: Список словарей с данными товаров. Каждый словарь должен содержать:
                - product_id (str): Уникальный ID товара
                - name (str): Название товара
                - price (Decimal): Цена
                - rating (float): Рейтинг
                - reviews_count (int): Количество отзывов
                - и другие обязательные поля
        :return:
            int: Количество успешно обработанных товаров

        Raises:
            ValueError: При отсутствии обязательных полей
            SQLAlchemyError: При ошибках работы с БД
            Exception: При других непредвиденных ошибках
        """
        try:
            logger.info(f"Начинаем сохранение {len(products_data)} товаров")
            return await self.repo.bulk_create_or_update(products_data)
        except Exception as e:
            logger.error(f"Ошибка обработки товаров: {str(e)}")
            raise

    async def product_list(
            self,
            category: Optional[str] = None,
            min_price: Optional[Decimal] = None,
            max_price: Optional[Decimal] = None,
            min_rating: Optional[float] = None,
            min_reviews_count: Optional[int] = None
    ) -> List[Product]:
        """
        Получение отфильтрованного списка товаров из БД.
        :param category: Фильтр по категории товара (точное совпадение)
        :param min_price: Минимальная цена товара (включительно)
        :param max_price: Максимальная цена товара (включительно)
        :param min_rating: Минимальный рейтинг товара (от 0 до 5)
        :param min_reviews_count: Минимальное количество отзывов

        :return: List[Product]: Список ORM-моделей товаров, удовлетворяющих фильтрам

        Raises:
            SQLAlchemyError: При ошибках запроса к БД
            Exception: При других непредвиденных ошибках

        Notes:
            - Если все параметры None, возвращает все товары
            - Фильтры комбинируются через AND
        """
        try:
            logger.info(f"Получаем список товаров по фильтрам: category - {category},"
                        f"min_price - {min_price},"
                        f"max_price - {max_price},"
                        f"min_rating - {min_rating},"
                        f"min_reviews_count - {min_reviews_count}")
            return await self.repo.find_all_by_filters(
                category=category,
                min_price=min_price,
                max_price=max_price,
                min_rating=min_rating,
                min_reviews_count=min_reviews_count
            )
        except Exception as e:
            logger.error(f"Ошибка получения списка товаров: {str(e)}")
            raise
