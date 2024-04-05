from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session, select

from ..database import engine
from .. import schemas, models, oauth2

router = APIRouter(prefix="/vote", tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(
    vote: schemas.Vote, current_user: models.User = Depends(oauth2.get_current_user)
):
    with Session(engine) as session:
        post = session.get(models.Post, vote.post_id)
        if not post:
            return HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Post with id: {vote.post_id} not found.",
            )
        found_vote = session.exec(
            select(models.Vote).where(
                models.Vote.post_id == vote.post_id,
                models.Vote.user_id == current_user.id,
            )
        ).first()

        if vote.dir == 1:
            if found_vote:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with id: {current_user.id} has already voted on post with id: {post.id}",
                )
            new_vote = models.Vote(post_id=vote.post_id, user_id=current_user.id)  # type: ignore
            session.add(new_vote)
            session.commit()
            return {"message": f"Successfully voted on the post: {post.id}"}

        else:
            if not found_vote:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vote does not exist.",
                )
            vote_to_delete = session.exec(
                select(models.Vote).where(models.Vote.post_id == vote.post_id)
            ).first()
            session.delete(vote_to_delete)
            session.commit()
            return {"message": f"Successfully deleted the vote on post: {post.id}"}
