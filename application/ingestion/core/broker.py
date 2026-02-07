"""RabbitMQ broker instance for worker service (without FastAPI dependencies)."""

from taskiq_aio_pika import AioPikaBroker
from shared.core.broker import create_broker

# Создаём глобальный экземпляр брокера для worker
_broker: AioPikaBroker | None = None


def get_broker() -> AioPikaBroker:
    """Получить глобальный экземпляр брокера (singleton).

    Returns:
        AioPikaBroker: Брокер для обработки задач
    """
    global _broker
    if _broker is None:
        _broker = create_broker()
    return _broker


async def init_broker() -> None:
    """Инициализация брокера при старте приложения."""
    broker = get_broker()
    await broker.startup()


async def shutdown_broker() -> None:
    """Остановка брокера при завершении приложения."""
    broker = get_broker()
    await broker.shutdown()
