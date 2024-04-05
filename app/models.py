import pytz
from sqlalchemy import TIMESTAMP, Column, ForeignKey, func
from datetime import datetime
from sqlmodel import Field, Relationship, SQLModel  # type: ignore
from .schemas import PostBase, UserBase


class User(UserBase, table=True):
    hashed_password: str = Field()
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
        ),
        default=datetime.now(pytz.timezone("Asia/Kolkata")),
    )
    posts: list["Post"] = Relationship(back_populates="user")


class Post(PostBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True), server_default=func.now(), nullable=False
        ),
        default=datetime.now(pytz.timezone("Asia/Kolkata")),
    )
    user_id: int = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    user: User = Relationship(back_populates="posts")


class Vote(SQLModel, table=True):
    post_id: int = Field(
        sa_column=Column(ForeignKey("post.id", ondelete="CASCADE"), primary_key=True)
    )
    user_id: int = Field(
        sa_column=Column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    )
