from sqlmodel import Field, SQLModel
from pydantic import EmailStr


class UserBase(SQLModel):
    email: EmailStr = Field(index=True)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    password: str  # TODO: password type?


class UserCreate(UserBase):
    password: str  # TODO: password type?


class UserPublic(UserBase):
    id: int


class UserUpdate(UserBase):
    email: str | None
    password: str | None  # TODO: password type?
