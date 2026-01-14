from datetime import timedelta
from sqlmodel import select
from models import User
from schemas import (
    UserCreateRequest,
    UserCreateDB,
    UserPublic,
    UserUpdate,
)
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from security import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_auth_settings,
    UserLogin,
    Token,
)


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        stmt = select(User).order_by(User.id)
        result: Result = await self.session.execute(stmt)
        users = result.scalars().all()
        return list(users)

    async def create(self, user: UserCreateDB) -> User:
        user_data = user.model_dump()
        user_data["password"] = get_password_hash(user_data["password"])
        db_user = User.model_validate(user_data)
        self.session.add(db_user)
        await self.session.commit()
        return db_user

    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def authenticate_user(
        self, email: str, password: str
    ) -> User | None:
        """Аутентифицирует пользователя по email и паролю.

        Args:
            email: Email пользователя
            password: Пароль в открытом виде

        Returns:
            Объект User если аутентификация успешна, иначе None
        """
        user = await self.get_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user

    async def login(self, login_data: UserLogin) -> Token:
        """Выполняет вход пользователя и возвращает JWT токен.

        Args:
            login_data: Данные для входа (email и password)

        Returns:
            Token с access_token

        Raises:
            ValueError: Если email или пароль неверны
        """
        user = await self.authenticate_user(
            login_data.email, login_data.password
        )
        if not user:
            raise ValueError("Неверный email или пароль")

        auth_settings = get_auth_settings()
        access_token_expires = timedelta(
            minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        return Token(access_token=access_token)
