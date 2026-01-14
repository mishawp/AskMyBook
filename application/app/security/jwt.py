from datetime import datetime, timedelta, timezone
from typing import Any
from jose import JWTError, jwt
from .config import get_auth_settings


def create_access_token(
    data: dict[str, Any], expires_delta: timedelta | None = None
) -> str:
    """Создает JWT access token.

    Args:
        data: Данные для включения в токен (обычно {"sub": user_email})
        expires_delta: Время жизни токена (по умолчанию из настроек)

    Returns:
        Закодированный JWT токен
    """
    auth_settings = get_auth_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, auth_settings.SECRET_KEY, algorithm=auth_settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Декодирует JWT access token.

    Args:
        token: JWT токен для декодирования

    Returns:
        Payload токена или None, если токен невалидный
    """
    auth_settings = get_auth_settings()
    try:
        payload = jwt.decode(
            token,
            auth_settings.SECRET_KEY,
            algorithms=[auth_settings.ALGORITHM],
        )
        return payload
    except JWTError:
        return None
