import uuid
from typing import List

from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import model, database, dependencies
from src.schemas import post_schema

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.get("", response_model=List[post_schema.Response])
def filter_post(session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user),
                skip: int = 0, limit: int = 10, search: str = ""):
    stmt = (select(model.Post)
            .where(model.Post.content.contains(search))
            .limit(limit)
            .offset(skip))
    posts = session.scalars(stmt).all()
    return posts

@router.post("", status_code=status.HTTP_201_CREATED, response_model=post_schema.Response)
def create_post(post: post_schema.Create,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    post = model.Post(**post.model_dump())
    post.user_id = current_user.id
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.get("/{post_id}", response_model=post_schema.Response)
def read_post(post_id: uuid.UUID,
              session: Session = Depends(database.get_session),
              current_user = Depends(dependencies.get_current_user)):

    post = session.get(model.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post not found")

    return post

@router.put("/{post_id}", status_code=status.HTTP_202_ACCEPTED, response_model=post_schema.Response)
def update_post(post_id: uuid.UUID, edit: post_schema.Update,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    post = session.get(model.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Unauthorised to update post")

    post.content = edit.content
    session.commit()
    session.refresh(post)
    return post

@router.delete("/{post_id}", status_code=status.HTTP_202_ACCEPTED)
def delete_post(post_id: uuid.UUID,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    post = session.get(model.Post, post_id)
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Unauthorised to delete post")

    session.delete(post)
    session.commit()
    return {"message": "Post successfully deleted"}