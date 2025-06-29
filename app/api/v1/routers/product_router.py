from decimal import Decimal
from typing import Optional, Dict

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies.repository_dep import get_session_with_commit
from app.schemas.product_schema import SProductsList
from app.services.product_service import ProductService
from app.services.wb_parser import WildberriesParser

router = APIRouter()


@router.post("/parse")
async def parsing(query: str,
                  limit: int,
                  session: AsyncSession = Depends(get_session_with_commit), ) -> Dict:
    """
    Эндпоинт выполняет парсинг данных с сайта wildberries и сохраняет их в БД

    :param query: Поисковый запрос (например, "телефон").
    :param limit: Максимальное количество товаров для парсинга.
    :param session: Асинхронная сессия БД (автоматически внедряется).
    :return: сообщение об успешном парсинге и сохранении товаров в БД

    Raises:
        HTTPException: 500 - При возникновении внутренних ошибок сервера.
    """
    service = ProductService(session=session)
    parser = WildberriesParser(product_service=service, limit=limit)
    try:
        result = await parser.parse_and_save(query)
    except Exception as e:
        logger.error(f"Ошибка в /products: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

    return {"message": f"Сохранено {result} товаров"}


@router.get("/products", response_model=SProductsList)
async def get_product_list(
    query: str,
    limit: int,
    session: AsyncSession = Depends(get_session_with_commit),
    category: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    min_rating: Optional[float] = None,
    min_reviews_count: Optional[int] = None,
):
    """Получение  товаров с Wildberries из БД.

    Эндпоинт выполняет поиск товаров по заданному запросу в БД и возвращает отфильтрованный список.

    Args:
        query: Поисковый запрос (например, "телефон").
        limit: Максимальное количество товаров для вывода.
        session: Асинхронная сессия БД (автоматически внедряется).
        category: Фильтр по категории товара (опционально).
        min_price: Минимальная цена товара (опционально).
        max_price: Максимальная цена товара (опционально).
        min_rating: Минимальный рейтинг товара (опционально).
        min_reviews_count: Минимальное количество отзывов (опционально).

    Returns:
        SProductsList: Объект со списком товаров

    Raises:
        HTTPException: 500 - При возникновении внутренних ошибок сервера.

    Examples:
        GET /products?query=телефон&limit=10&min_price=30000&min_rating=4
        {
          "products": [
              {
                    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                    "product_name": "samsung",
                    "price": "30000",
                    "discount_price": "25999",
                    "rating": 4,
                    "reviews_count": 15
                    }
                ]
                }
                ...
            ]
        }
    """
    try:
        service = ProductService(session=session)

        products = await service.product_list(
            search_query=query,
            category=category,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            min_reviews_count=min_reviews_count,
            limit=limit
        )

        return SProductsList(products=products)

    except Exception as e:
        logger.error(f"Ошибка в /products: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
