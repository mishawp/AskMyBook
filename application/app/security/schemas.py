from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Схема ответа с токеном доступа."""

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Схема данных, извлеченных из токена."""

    email: EmailStr | None = None


class UserLogin(BaseModel):
    """Схема для входа пользователя."""

    email: EmailStr
    password: str
