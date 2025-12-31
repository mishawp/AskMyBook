from sqlmodel import select
from models import User, UserCreate, UserPublic, UserUpdate
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


async def get_users(session: AsyncSession) -> list[User]:
    stmt = select(User).order_by(User.id)
    result: Result = await session.execute(stmt)
    users = result.scalars().all()
    return list(users)


async def create_user(session: AsyncSession, user: UserCreate) -> User:
    db_user = User.model_validate(user)
    # TODO: password hash
    session.add(db_user)
    await session.commit()
    return db_user
