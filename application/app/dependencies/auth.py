from typing import Annotated
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from models import User
from security import decode_access_token, TokenData, get_auth_settings
from services import UserService
from core import ScopedSessionDep

# OAuth2 схема для Swagger UI и API клиентов (auto_error=False для fallback на cookie)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


async def get_current_user(
    request: Request,
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: ScopedSessionDep,
) -> User:
    """Получает текущего аутентифицированного пользователя из JWT токена.

    Токен извлекается из:
    1. Заголовка Authorization (Bearer token) — для API клиентов
    2. HTTP-only cookie — для браузеров

    Args:
        request: FastAPI Request для доступа к cookies
        token: JWT токен из заголовка Authorization (может быть None)
        session: Сессия базы данных

    Returns:
        Объект текущего пользователя

    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Если токен не в заголовке, пробуем получить из cookie
    if token is None:
        auth_settings = get_auth_settings()
        token = request.cookies.get(auth_settings.COOKIE_NAME)

    if token is None:
        raise credentials_exception

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    email: str | None = payload.get("sub")
    if email is None:
        raise credentials_exception

    token_data = TokenData(email=email)

    user_service = UserService(session)
    user = await user_service.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception

    return user


# Type alias для использования в роутерах
CurrentUser = Annotated[User, Depends(get_current_user)]
