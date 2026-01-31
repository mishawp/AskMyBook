"""Shared database manager for all services."""

from asyncio import current_task
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from typing import AsyncGenerator

from .config import get_db_settings, DBSettings


class DatabaseManager:
    """Менеджер работы с базой данных и асинхронными сессиями SQLAlchemy.

    Отвечает за:
    - хранение движка (AsyncEngine)
    - создание SessionMaker
    - создание scoped-сессий
    - корректное закрытие соединений"""

    def __init__(self, settings: DBSettings, engine: AsyncEngine):
        """
        Args:
            settings (DBSettings): Настройки базы данных.
            engine (AsyncEngine): Асинхронный движок SQLAlchemy.
        """
        self.settings = settings
        self.engine = engine
        self.SessionMaker = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
        )
        self.ScopedSessionMaker = async_scoped_session(
            session_factory=self.SessionMaker,
            scopefunc=current_task,
        )

    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Генератор асинхронной сессии SQLAlchemy.

        Yields:
            AsyncSession: Асинхронная сессия БД."""
        async with self.SessionMaker() as session:
            yield session

    async def get_scoped_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Генератор scoped-сессии, привязанной к текущей asyncio-задаче.

        Yields:
            AsyncSession: Scoped асинхронная сессия БД."""
        session = self.ScopedSessionMaker()
        try:
            yield session
        finally:
            await self.ScopedSessionMaker.remove()

    async def dispose(self) -> None:
        """Закрывает соединение с базой данных и освобождает ресурсы."""
        await self.engine.dispose()
        self.engine = None


def create_db_manager(
    settings: DBSettings | None = None,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
) -> DatabaseManager:
    """Фабрика для создания DatabaseManager.

    Args:
        settings: Настройки БД. Если None, используются настройки из окружения.
        echo: Логирование SQL запросов.
        pool_size: Размер пула соединений.
        max_overflow: Максимальное превышение пула.

    Returns:
        DatabaseManager: Инициализированный менеджер БД.
    """
    if settings is None:
        settings = get_db_settings()

    engine = create_async_engine(
        url=settings.DATABASE_URL_asyncpg,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
    )
    return DatabaseManager(settings, engine)
