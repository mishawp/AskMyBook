"""Taskiq broker configuration for RabbitMQ."""

from taskiq_aio_pika import AioPikaBroker

from .config import get_rabbitmq_settings


def create_broker() -> AioPikaBroker:
    """Создаёт и возвращает Taskiq брокер для RabbitMQ.

    Returns:
        AioPikaBroker: Настроенный брокер для работы с RabbitMQ.
    """
    settings = get_rabbitmq_settings()
    return AioPikaBroker(url=settings.RABBITMQ_URL)
