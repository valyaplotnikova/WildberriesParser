from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Класс настроек для работы проекта."""

    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    model_config = SettingsConfigDict(env_file=(".env", ".test.env"), extra="allow")


settings = Settings()


def get_db_url():
    """
    Формирует строку подключения к базе данных PostgreSQL с использованием asyncpg.

    :return: Строка подключения к базе данных в формате
             'postgresql+asyncpg://<user>:<password>@<host>:<port>/<dbname>'
    :rtype: str
    """
    return (
        f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
    )


database_url = get_db_url()
