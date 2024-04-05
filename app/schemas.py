from typing import Annotated
from sqlmodel import SQLModel
from datetime import datetime
from pydantic import EmailStr
from sqlmodel import Field, AutoString  # type: ignore


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, sa_type=AutoString)


class UserCreate(UserBase):
    password: str


class UserRead(SQLModel):
    id: int
    email: EmailStr
    created_at: datetime


class UserUpdate(SQLModel):
    id: int | None = None
    email: EmailStr | None = None
    password: str | None = None


class UserLogin(SQLModel):
    email: EmailStr
    password: str


class PostBase(SQLModel):
    title: str
    description: str
    published: bool = True


class PostRead(PostBase):
    id: int
    user_id: int
    created_at: datetime


class PostOut(SQLModel):
    Post: PostRead
    user: UserRead
    votes: int


class PostCreate(PostBase):
    pass


class PostUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    published: bool | None = None


class Token(SQLModel):
    access_token: str
    token_type: str


class TokenData(SQLModel):
    id: str | None = None


class Vote(SQLModel):
    post_id: int
    dir: Annotated[int, Field(ge=0, le=1)]
