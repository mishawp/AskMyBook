from asyncio import current_task
from fastapi import Depends
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
    async_scoped_session,
    AsyncSession,
)
from sqlmodel import SQLModel
from typing import Annotated, AsyncGenerator
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

        Используется как dependency в FastAPI.
        Сессия автоматически закрывается после использования.

        Yields:
            AsyncSession: Асинхронная сессия БД."""
        async with self.SessionMaker() as session:
            yield session

    async def get_scoped_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Генератор scoped-сессии, привязанной к текущей asyncio-задаче.

        Полезно при работе с background tasks и вложенными вызовами.

        Yields:
            AsyncSession: Scoped асинхронная сессия БД."""
        session = self.ScopedSessionMaker()
        try:
            yield session
        finally:
            await self.ScopedSessionMaker.remove()

    async def dispose(self) -> None:
        """Закрывает соединение с базой данных и освобождает ресурсы.

        Вызывается при завершении жизненного цикла приложения."""
        await self.engine.dispose()
        self.engine = None


# Глобальный экземпляр DatabaseManager.
# Используется во всём приложении для:
# - получения сессий
# - управления соединением с БД
db_manager = DatabaseManager(
    get_db_settings(),
    create_async_engine(
        url=get_db_settings().DATABASE_URL_asyncpg,
        echo=False,
        pool_size=5,
        max_overflow=10,
    ),
)

# Dependency FastAPI для получения обычной асинхронной сессии БД.
AsyncSessionDep = Annotated[
    AsyncSession, Depends(db_manager.get_async_session)
]

# Dependency FastAPI для получения scoped асинхронной сессии БД.
ScopedSessionDep = Annotated[
    AsyncSession, Depends(db_manager.get_scoped_session)
]


async def init_db():
    """Инициализирует структуру базы данных.

    Действия:
    - создаёт declarative base
    - удаляет все таблицы
    - создаёт таблицы заново

    Используется при старте приложения.
    ⚠️ Опасно для production (drop_all)."""
    Base = declarative_base(metadata=SQLModel.metadata)
    async with db_manager.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
