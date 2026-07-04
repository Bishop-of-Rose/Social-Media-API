from fastapi import Depends, HTTPException, status, APIRouter
from psycopg2.errors import UniqueViolation, ForeignKeyViolation
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import model, database, dependencies
from src.schemas import vote_schema

router = APIRouter(
    prefix="/votes",
    tags=["Votes"],
)

@router.post("", status_code=status.HTTP_201_CREATED)
def create_vote(vote: vote_schema.Create,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    vote = model.Vote(**vote.model_dump())
    vote.user_id = current_user.id
    ref_type = "post" if vote.comment_id is None else "comment"

    try:
        session.add(vote)
        session.commit()
        session.refresh(vote)
        session.close()

    except IntegrityError as e:
        print(e)

        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"User already has a vote on this {ref_type}")

        elif isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Vote reference {ref_type} not found")

    return {"message": "Vote successfully created"}

@router.put("", status_code=status.HTTP_202_ACCEPTED)
def update_vote(vote: vote_schema.Update,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    ref_type = "post" if vote.comment_id is None else "comment"
    stmt = (select(model.Vote)
            .where(model.Vote.user_id == current_user.id)
            .where(model.Vote.post_id == vote.post_id)
            .where(model.Vote.comment_id == vote.comment_id)
            )
    result = session.scalars(stmt).one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User has no vote on this {ref_type}")

    result.type = vote.type
    session.commit()
    session.close()
    return {"message": "Vote successfully updated"}

@router.delete("", status_code=status.HTTP_202_ACCEPTED)
def delete_vote(vote: vote_schema.Base,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    ref_type = "post" if vote.comment_id is None else "comment"
    stmt = (select(model.Vote)
            .where(model.Vote.user_id == current_user.id)
            .where(model.Vote.post_id == vote.post_id)
            .where(model.Vote.comment_id == vote.comment_id)
            )

    result = session.scalars(stmt).one_or_none()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User has no vote on this {ref_type}")

    session.delete(result)
    session.commit()
    session.close()
    return {"message": "Vote successfully deleted"}