import uuid
from sqlmodel import SQLModel
from pydantic import EmailStr


class UserBase(SQLModel):
    email: EmailStr


class UserCreateRequest(UserBase):
    password: str  # TODO: password type?


class UserCreateDB(UserBase):
    password: str  # TODO: password type?


class UserPublic(UserBase):
    id: uuid.UUID


class UserUpdate(UserBase):
    email: EmailStr | None
    password: str | None  # TODO: password type?
