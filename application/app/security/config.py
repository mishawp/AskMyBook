from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class AuthSettings(BaseSettings):
    """Класс настроек аутентификации и JWT."""

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Cookie settings
    COOKIE_NAME: str = "access_token"
    COOKIE_MAX_AGE: int = 60 * 60 * 24 * 7  # 7 дней
    COOKIE_SECURE: bool = False  # True в production (HTTPS)
    COOKIE_HTTPONLY: bool = True
    COOKIE_SAMESITE: str = "lax"

    model_config = SettingsConfigDict(extra="ignore")


@lru_cache()
def get_auth_settings() -> AuthSettings:
    """Фабрика настроек аутентификации с кешированием.

    Использует lru_cache, чтобы гарантировать создание
    единственного экземпляра AuthSettings на всё приложение."""
    return AuthSettings()
