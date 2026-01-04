import uuid
from sqlmodel import Field, SQLModel, text
from pydantic import EmailStr


class UserBase(SQLModel):
    email: EmailStr = Field(index=True)


class User(UserBase, table=True):
    id: uuid.UUID | None = Field(
        default=None,
        primary_key=True,
        sa_column_kwargs={"server_default": text("uuidv7()")},
    )
    password: str  # TODO: password type?


class UserCreateRequest(UserBase):
    password: str  # TODO: password type?


class UserCreateDB(UserBase):
    password: str  # TODO: password type?


class UserPublic(UserBase):
    id: uuid.UUID


class UserUpdate(UserBase):
    email: EmailStr | None
    password: str | None  # TODO: password type?
