import uuid

from fastapi import Depends, HTTPException, status, APIRouter
from psycopg2.errors import ForeignKeyViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import model, database, dependencies
from src.schemas import comment_schema

router = APIRouter(
    prefix="/comments",
    tags=["Comments"],
)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=comment_schema.Response)
def create_comment(comment: comment_schema.Create,
                   session: Session = Depends(database.get_session),
                   current_user = Depends(dependencies.get_current_user),
                   ):
    comment = model.Comment(**comment.model_dump())
    comment.user_id = current_user.id
    ref_type = "post" if comment.replied is None else "comment"

    try:
        session.add(comment)
        session.commit()
        session.refresh(comment)
        session.close()

    except IntegrityError as e:
        print(e)
        if isinstance(e.orig, ForeignKeyViolation):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Comment reference {ref_type} not found")

    return comment

@router.get("/{comment_id}", response_model=comment_schema.Response)
def read_comment(comment_id: uuid.UUID,
                 session: Session = Depends(database.get_session),
                 current_user = Depends(dependencies.get_current_user)):
    comment = session.get(model.Comment, comment_id)
    session.close()

    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found")

    return comment

@router.put("/{comment_id}", status_code=status.HTTP_202_ACCEPTED, response_model=comment_schema.Response)
def update_comment(comment_id: uuid.UUID,
                   edit: comment_schema.Update,
                   session: Session = Depends(database.get_session),
                   current_user = Depends(dependencies.get_current_user)):
    comment = session.get(model.Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorised to update comment")

    comment.content = edit.content
    session.commit()
    session.refresh(comment)
    session.close()
    return comment

@router.delete("/{comment_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_comment(comment_id: uuid.UUID,
                   session: Session = Depends(database.get_session),
                   current_user = Depends(dependencies.get_current_user)):
    comment = session.get(model.Comment, comment_id)
    if comment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorised to delete comment")

    session.delete(comment)
    session.commit()
    session.close()
    return {"message": "Comment successfully deleted"}