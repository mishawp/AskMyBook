from fastapi import APIRouter, Depends
from models import User
from schemas import (
    UserCreateRequest,
    UserCreateDB,
    UserPublic,
    UserUpdate,
)
from services import UserService
from core import AsyncSessionDep, ScopedSessionDep

router = APIRouter(tags=["User"])


@router.get("/", response_model=list[UserPublic])
async def get_users(session: AsyncSessionDep):
    user_service = UserService(session)
    return await user_service.get_all()


@router.post("/", response_model=UserPublic)
async def create_user(user: UserCreateRequest, session: AsyncSessionDep):
    user_service = UserService(session)
    return await user_service.create(user)
