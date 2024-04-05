from typing import List
from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, col, or_, select
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from .. import models, schemas, oauth2
from ..database import engine

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(  # type: ignore
    current_user: models.User = Depends(oauth2.get_current_user),
    limit: int = 10,
    skip: int = 0,
    search: str | None = "",
):
    with Session(engine) as session:
        # posts = session.exec(
        #     select(models.Post).where(models.Post.user_id == current_user.id)
        # ).all()
        # query = (
        #     select(models.Post)
        #     .options(joinedload(models.Post.user))  # type: ignore
        #     .where(
        #         or_(
        #             models.Post.title.like(search_keyword), models.Post.description.like(search_keyword)  # type: ignore
        #         ),
        #     )
        #     .limit(limit)
        #     .offset(skip)
        # )
        # posts = session.exec(query).all()

        # query = (
        #     select(models.Post, func.count(models.Vote.post_id).label("votes"))  # type: ignore
        #     .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)  # type: ignore
        #     .group_by(models.Post.id)  # type: ignore
        #     .order_by(models.Post.id)  # type: ignore
        # )
        search_keyword = f"%{search}%"
        query = (
            select(models.Post, func.count(models.Vote.post_id).label("votes"))  # type: ignore
            .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)  # type: ignore
            .where(
                or_(
                    models.Post.title.like(search_keyword),  # type: ignore
                    models.Post.description.like(search_keyword),  # type: ignore
                )
            )
            .group_by(models.Post.id)  # type: ignore
            .order_by(models.Post.id)  # type: ignore
            .limit(limit)
            .offset(skip)
        )
        posts_with_votes = session.exec(query).all()

        if not posts_with_votes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No posts to show.",
            )
        user_ids = {post.user_id for post, _ in posts_with_votes}
        users = session.exec(select(models.User).where(models.User.id.in_(user_ids))).all()  # type: ignore
        users_dict = {user.id: user for user in users}

        final_response = []

        for post, votes in posts_with_votes:
            user_read = users_dict.get(post.user_id)
            if user_read:
                post_out = schemas.PostOut(
                    Post=schemas.PostRead(
                        id=post.id,  # type: ignore
                        title=post.title,
                        description=post.description,
                        published=post.published,
                        user_id=post.user_id,
                        created_at=post.created_at,
                    ),
                    user=schemas.UserRead(
                        id=user_read.id,  # type: ignore
                        email=user_read.email,
                        created_at=user_read.created_at,
                    ),
                    votes=votes,
                )
                final_response.append(post_out)  # type: ignore
        return final_response  # type: ignore


# give latest post where
@router.get("/latest", response_model=schemas.PostRead)
def get_latest_post(current_user: models.User = Depends(oauth2.get_current_user)):
    with Session(engine) as session:
        max_id_query = select(func.max(col(models.Post.id))).where(
            models.Post.user_id == current_user.id
        )
        result = session.execute(max_id_query)  # type: ignore
        max_id = result.scalar()
        if max_id is None:
            raise HTTPException(
                status_code=status.HTTP_204_NO_CONTENT,
                detail="There are no posts to show.",
            )
        # latest_post = session.get(models.Post,max_id)
        latest_post: models.Post = session.query(models.Post).options(joinedload(models.Post.user)).get(max_id)  # type: ignore
        if latest_post.user_id != current_user.id:  # type: ignore
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the following action",
            )
        return latest_post


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int, current_user: models.User = Depends(oauth2.get_current_user)):
    with Session(engine) as session:
        # post = session.get(models.Post, id)
        # post = session.query(models.Post).options(joinedload(models.Post.user)).get(id)  # type: ignore
        query = (
            select(models.Post, func.count(models.Vote.post_id).label("votes"))  # type: ignore
            .join(models.Vote, models.Post.id == models.Vote.post_id, isouter=True)  # type: ignore
            .where(models.Post.id == id)
            .group_by(models.Post.id)  # type: ignore
            .order_by(models.Post.id)  # type: ignore
        )
        post_with_votes = session.exec(query).first()

        if not post_with_votes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find a post with id: {id}",
            )

        post, votes = post_with_votes

        if post.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform requested action",
            )

        user = session.exec(
            select(models.User).where(models.User.id == post.user_id)
        ).first()
        if not user:
            # This is unlikely but adds robustness to your code
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User data not found for post with id: {id}",
            )

        post_out = schemas.PostOut(
            Post=schemas.PostRead(
                id=post.id,  # type: ignore
                title=post.title,
                description=post.description,
                published=post.published,
                user_id=post.user_id,
                created_at=post.created_at,
            ),
            user=schemas.UserRead(
                id=user.id,  # type: ignore
                email=user.email,
                created_at=user.created_at,
            ),
            votes=votes,
        )

        return post_out


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostRead)
def create_post(
    post: schemas.PostCreate,
    current_user: models.User = Depends(oauth2.get_current_user),
):
    with Session(engine) as session:
        # print(current_user.email)
        extra_data = {"user_id": current_user.id}
        db_post = models.Post.model_validate(post, update=extra_data)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)
        _ = db_post.user  # type: ignore
        return db_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: models.User = Depends(oauth2.get_current_user)):
    with Session(engine) as session:
        post = session.get(models.Post, id)
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find a post with id: {id}",
            )
        if post.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the following action",
            )
        session.delete(post)
        session.commit()


@router.patch("/{id}", response_model=schemas.PostRead)
def update_post(
    id: int,
    post: schemas.PostUpdate,
    current_user: models.User = Depends(oauth2.get_current_user),
):
    with Session(engine) as session:
        # db_post = session.get(models.Post, id)
        db_post = session.query(models.Post).options(joinedload(models.Post.user)).get(id)  # type: ignore
        if not db_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Cannot find post with id: {id}.",
            )
        if db_post.user_id != current_user.id:
            print(db_post.id)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to perform the following action",
            )
        post_data = post.model_dump(exclude_unset=True)
        db_post.sqlmodel_update(post_data)
        session.add(db_post)
        session.commit()
        session.refresh(db_post)
        return db_post
