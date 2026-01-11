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


class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all(self) -> list[User]:
        stmt = select(User).order_by(User.id)
        result: Result = await self.session.execute(stmt)
        users = result.scalars().all()
        return list(users)

    async def create(self, user: UserCreateDB) -> User:
        db_user = User.model_validate(user)
        # TODO: password hash
        self.session.add(db_user)
        await self.session.commit()
        return db_user
