import uuid
from decimal import Decimal
from typing import List

from pydantic import BaseModel, ConfigDict


class SProductResponse(BaseModel):
    id: uuid.UUID
    product_name: str
    price: Decimal
    discount_price: Decimal
    rating: float
    reviews_count: int

    model_config = ConfigDict(arbitrary_types_allowed=True, from_attributes=True)


class SProductsList(BaseModel):
    products: List[SProductResponse]
