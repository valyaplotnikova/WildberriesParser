import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.ext.asyncio import (AsyncAttrs, AsyncSession,
                                    async_sessionmaker, create_async_engine)
from sqlalchemy.orm import (DeclarativeBase, Mapped, declared_attr,
                            mapped_column)

from app.core.config import database_url

engine = create_async_engine(url=database_url)
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=True
)


class Base(AsyncAttrs, DeclarativeBase):
    """
    Базовая модель
    """

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    @declared_attr
    def __tablename__(cls) -> str:
        """
        Формирует имя тадлицы атоматически на основе имени класса
        :return: str: имя таблицы в БД
        """
        if cls.__name__.lower()[-1] == "y":
            return cls.__name__.lower()[:-1] + "ies"
        return cls.__name__.lower() + "s"

    def __repr__(self) -> str:
        """Строковое представление объекта для удобства отладки."""
        return f"<{self.__class__.__name__}(id={self.id})>"
