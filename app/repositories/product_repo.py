from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from loguru import logger
from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product


class ProductRepository:
    """
    Репозиторий для работы с товарами в базе данных.

    Обеспечивает низкоуровневые операции с товарами:
        - Поиск товаров по различным критериям
        - Создание и обновление товаров
        - Пакетные операции с товарами

    Attributes:
        session (AsyncSession): Асинхронная сессия SQLAlchemy для работы с БД
    """

    def __init__(self, session: AsyncSession):
        """
        Инициализация репозитория.
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session

    async def find_one_or_none_by_id(self, product_id: str) -> Optional[Product]:
        """
        Поиск товара по ID Wildberries.

        Args:
            product_id: Идентификатор товара в системе Wildberries

        Returns:
            Optional[Product]: Найденный товар или None, если не найден

        Raises:
            SQLAlchemyError: При ошибках выполнения запроса

        """
        try:
            result = await self.session.execute(
                select(Product).where(Product.product_id == product_id)
            )
            return result.scalars().first()
        except SQLAlchemyError as e:
            logger.error(f"Ошибка при поиске товара: {str(e)}")
            raise

    async def find_all_by_filters(
        self,
        search_query: str,
        limit: int,
        category: Optional[str] = None,
        min_price: Optional[Decimal] = None,
        max_price: Optional[Decimal] = None,
        min_rating: Optional[float] = None,
        min_reviews_count: Optional[int] = None,
    ) -> List[Product]:
        """
         Поиск товаров с применением фильтров.

        Args:
            search_query: Поисковый запрос(Содержится в названии продукта)
            limit: Ограничение по количеству выводимых товаров
            category: Фильтр по категории (точное совпадение)
            min_price: Минимальная цена (включительно)
            max_price: Максимальная цена (включительно)
            min_rating: Минимальный рейтинг (от 0 до 5)
            min_reviews_count: Минимальное количество отзывов

        Returns:
            List[Product]: Список товаров, удовлетворяющих условиям

        Raises:
            SQLAlchemyError: При ошибках выполнения запроса

        Notes:
            - Фильтры комбинируются через логическое И
            - Если все фильтры None, возвращаются все товары
        """

        try:
            query = select(Product).where(Product.product_name.ilike(f"%{search_query}%"))

            if category:
                query = query.where(Product.category == category)
            if min_price:
                query = query.where(Product.price >= min_price)
            if max_price:
                query = query.where(Product.price <= max_price)
            if min_rating:
                query = query.where(Product.rating >= min_rating)
            if min_reviews_count:
                query = query.where(Product.reviews_count >= min_reviews_count)

            result = await self.session.execute(query)
            return list(result.scalars().all())[:limit]

        except SQLAlchemyError as e:
            logger.error(f"Ошибка при фильтрации товаров: {str(e)}")
            raise

    async def create_or_update(self, product_data: dict) -> Product:
        """
        Создание или обновление товара.

        Если товар с таким product_id существует - обновляет его данные,
        иначе создает новую запись.

        Args:
            product_data: Словарь с данными товара. Должен содержать:
                - product_id (str): Обязательное
                - product_name (str): Обязательное
                - price (Decimal/str): Обязательное
                - rating (float): Обязательное
                - reviews_count (int): Обязательное
                - product_url (str): Обязательное
                - discount_price (Decimal/str): Опциональное
                - category (str): Опциональное
                - search_query (str): Опциональное

        Returns:
            Product: Созданный или обновленный товар

        Raises:
            ValueError: При отсутствии обязательных полей
            SQLAlchemyError: При ошибках работы с БД
            Exception: При других непредвиденных ошибках
        """

        try:
            product_id = str(product_data["product_id"])
            product = await self.find_one_or_none_by_id(product_id)

            if product is None:
                # Создаем новый товар
                product = Product(
                    product_id=product_id,
                    product_name=str(product_data["product_name"]),
                    price=Decimal(str(product_data["price"])),
                    discount_price=(
                        Decimal(str(product_data["discount_price"]))
                        if product_data.get("discount_price")
                        else None
                    ),
                    rating=float(product_data["rating"]),
                    reviews_count=int(product_data["reviews_count"]),
                    product_url=str(product_data["product_url"]),
                    category=str(product_data.get("category", "")),
                    search_query=str(product_data.get("search_query", "")),
                    created_at=datetime.now(),
                )
                self.session.add(product)
            else:
                # Обновляем существующий товар
                await self.session.execute(
                    update(Product)
                    .where(Product.product_id == product_id)
                    .values(
                        product_name=str(product_data["product_name"]),
                        price=Decimal(str(product_data["price"])),
                        discount_price=(
                            Decimal(str(product_data["discount_price"]))
                            if product_data.get("discount_price")
                            else None
                        ),
                        rating=float(product_data["rating"]),
                        reviews_count=int(product_data["reviews_count"]),
                        product_url=str(product_data["product_url"]),
                        category=str(product_data.get("category", "")),
                        search_query=str(product_data.get("search_query", "")),
                        updated_at=datetime.now(),
                    )
                )

            await self.session.commit()
            return product

        except KeyError as e:
            await self.session.rollback()
            logger.error(f"Отсутствует обязательное поле: {str(e)}")
            raise ValueError(f"Отсутствует обязательное поле: {str(e)}")
        except SQLAlchemyError as e:
            await self.session.rollback()
            logger.error(f"Ошибка БД: {str(e)}")
            raise
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Неожиданная ошибка: {str(e)}")
            raise

    async def bulk_create_or_update(self, products_data: list[dict]) -> int:
        """
        Пакетное создание/обновление товаров.

        Args:
           products_data: Список словарей с данными товаров

        Returns:
           count: Количество успешно обработанных товаров

        Notes:
           - Пропускает товары с ошибками, продолжая обработку остальных
           - Возвращает только количество успешных операций
        """
        count = 0
        for data in products_data:
            try:
                await self.create_or_update(data)
                count += 1
                logger.info(f"Успешно сохраненено {count} товаров")
            except Exception:
                continue
        return count
