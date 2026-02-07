"""RabbitMQ broker instance for sending tasks."""

from shared.core.broker import create_broker

# Создаём глобальный экземпляр брокера для отправки задач
_broker = create_broker()


async def init_broker() -> None:
    """Инициализация брокера при старте приложения."""
    await _broker.startup()


async def shutdown_broker() -> None:
    """Остановка брокера при завершении приложения."""
    await _broker.shutdown()
