"""Database module re-exported from shared with FastAPI-specific dependencies."""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlmodel import SQLModel

from shared.core.database import create_db_manager, DatabaseManager
from shared.core.config import get_db_settings


# Глобальный экземпляр DatabaseManager
db_manager = create_db_manager()


# Dependency FastAPI для получения обычной асинхронной сессии БД
AsyncSessionDep = Annotated[
    AsyncSession, Depends(db_manager.get_async_session)
]

# Dependency FastAPI для получения scoped асинхронной сессии БД
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
    Опасно для production (drop_all)."""
    Base = declarative_base(metadata=SQLModel.metadata)
    async with db_manager.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
