from fastapi import APIRouter, Depends
from models import User, UserCreate, UserPublic, UserUpdate
import services.user as crud
from core.database import AsyncSessionDep, ScopedSessionDep

router = APIRouter(tags=["User"])


@router.get("/", response_model=list[UserPublic])
async def get_users(session: AsyncSessionDep):
    return await crud.get_users(session)


@router.post("/", response_model=UserPublic)
async def create_user(session: AsyncSessionDep, user: UserCreate):
    return await crud.create_user(session, user)
