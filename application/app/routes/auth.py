from fastapi import APIRouter, HTTPException, status, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from schemas import (
    UserCreateRequest,
    UserCreateDB,
    UserPublic,
)
from security import Token, UserLogin, get_auth_settings
from services import UserService
from core import AsyncSessionDep
from dependencies import CurrentUser

router = APIRouter(tags=["Auth"])


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(user: UserCreateRequest, session: AsyncSessionDep):
    """Регистрация нового пользователя.

    Создает нового пользователя с хешированным паролем.

    Args:
        user: Данные для регистрации (email и password)
        session: Сессия базы данных

    Returns:
        Публичные данные созданного пользователя

    Raises:
        HTTPException: Если пользователь с таким email уже существует
    """
    user_service = UserService(session)

    # Проверяем, существует ли уже пользователь с таким email
    existing_user = await user_service.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    user_create_db = UserCreateDB(**user.model_dump())
    created_user = await user_service.create(user_create_db)
    return created_user


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep,
):
    """Вход пользователя (OAuth2 compatible).

    Аутентифицирует пользователя и возвращает JWT токен.
    Токен также устанавливается в HTTP-only cookie для автоматической аутентификации.

    Args:
        response: FastAPI Response для установки cookie
        form_data: Форма с username (email) и password
        session: Сессия базы данных

    Returns:
        JWT токен доступа

    Raises:
        HTTPException: Если email или пароль неверны
    """
    auth_service = UserService(session)
    auth_settings = get_auth_settings()

    try:
        # OAuth2PasswordRequestForm использует поле username, но мы используем его для email
        login_data = UserLogin(
            email=form_data.username, password=form_data.password
        )
        token = await auth_service.login(login_data)

        # Устанавливаем токен в HTTP-only cookie
        response.set_cookie(
            key=auth_settings.COOKIE_NAME,
            value=token.access_token,
            max_age=auth_settings.COOKIE_MAX_AGE,
            httponly=auth_settings.COOKIE_HTTPONLY,
            secure=auth_settings.COOKIE_SECURE,
            samesite=auth_settings.COOKIE_SAMESITE,
        )

        return token
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/logout")
async def logout(response: Response):
    """Выход пользователя.

    Удаляет cookie с токеном аутентификации.

    Args:
        response: FastAPI Response для удаления cookie

    Returns:
        Сообщение об успешном выходе
    """
    auth_settings = get_auth_settings()
    response.delete_cookie(
        key=auth_settings.COOKIE_NAME,
        httponly=auth_settings.COOKIE_HTTPONLY,
        secure=auth_settings.COOKIE_SECURE,
        samesite=auth_settings.COOKIE_SAMESITE,
    )
    return {"message": "Успешный выход"}


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(current_user: CurrentUser):
    """Получить информацию о текущем пользователе.

    Требует аутентификации. Возвращает данные пользователя из токена.

    Args:
        current_user: Текущий аутентифицированный пользователь (из JWT)

    Returns:
        Публичные данные текущего пользователя
    """
    return current_user
