"""Database module for ingestion service (without FastAPI dependencies)."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from shared.core.database import create_db_manager, DatabaseManager
from shared.core.config import get_db_settings


# Глобальный экземпляр DatabaseManager
_db_manager: DatabaseManager | None = None


def get_db_manager() -> DatabaseManager:
    """Получить глобальный экземпляр DatabaseManager (singleton).

    Returns:
        DatabaseManager: Менеджер базы данных
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = create_db_manager()
    return _db_manager


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить асинхронную сессию БД через контекстный менеджер.

    Yields:
        AsyncSession: Асинхронная сессия для работы с БД
    """
    db_manager = get_db_manager()
    async with db_manager.SessionMaker() as session:
        yield session


@asynccontextmanager
async def get_scoped_session() -> AsyncGenerator[AsyncSession, None]:
    """Получить scoped сессию БД через контекстный менеджер.

    Yields:
        AsyncSession: Scoped асинхронная сессия для работы с БД
    """
    db_manager = get_db_manager()
    session = db_manager.ScopedSessionMaker()
    try:
        yield session
    finally:
        await db_manager.ScopedSessionMaker.remove()
