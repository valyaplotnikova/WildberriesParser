from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, Numeric, Float, Integer, TIMESTAMP, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.database import Base


class Product(Base):
    """Модель для хранения данных о товарах Wildberries"""

    product_name: Mapped[str] = mapped_column(String(255))
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    discount_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    rating: Mapped[float] = mapped_column(Float)
    reviews_count: Mapped[int] = mapped_column(Integer)
    product_id: Mapped[str] = mapped_column(String(50), unique=True)  # ID из WB
    product_url: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(100))
    search_query: Mapped[str] = mapped_column(String(200))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=False), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP,
                                                 server_default=func.now(),
                                                 onupdate=func.now(),
                                                 nullable=True)
