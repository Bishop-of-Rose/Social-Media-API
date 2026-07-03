from typing import List, Optional
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from .. import model, schema, database
from ..util import jwtUtil
from ..controllers import post_controller

router = APIRouter(
    prefix='/posts',
    tags = ['Posts']
)

@router.get("", response_model=List[schema.Post.PostResponse])
def filter_post(session: Session = Depends(database.get_session), current_user = Depends(jwtUtil.get_current_user),
                skip: int = 0, limit: int = 10, search: Optional[str] = ""):
    return post_controller.filter_posts(model, session, current_user, skip, limit, search)

@router.post("", status_code=status.HTTP_201_CREATED, response_model=schema.Post.PostResponse)
def create_post(post: schema.Post.PostCreate, session: Session = Depends(database.get_session),
                current_user = Depends(jwtUtil.get_current_user)):
    post = model.Post(**post.dict(), post_user_id = current_user.id)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post

@router.get("/{post_id}", response_model=schema.Post.PostResponse)
def read_post(post_id: int, session: Session = Depends(database.get_session), current_user = Depends(jwtUtil.get_current_user)):
    query = session.query(model.Post).filter(model.Post.id == post_id)
    post = query.first()
    if post is not None:
        return post
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with <id: {post_id}> not found")

@router.put("/{post_id}", status_code=status.HTTP_201_CREATED, response_model=schema.Post.PostResponse)
def update_post(post_id: int, edit: schema.Post.PostUpdate, session: Session = Depends(database.get_session),
                current_user = Depends(jwtUtil.get_current_user)):
    query = session.query(model.Post).filter(model.Post.id == post_id)
    post = query.first()
    if post is not None:
        if post.post_user_id == current_user.id:
            query.filter(model.Post.id == post_id).update(edit.model_dump(), synchronize_session=False)
            session.commit()
            session.refresh(post)
            return post
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"Unauthorised to update post with <id: {post_id}>")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with <id: {post_id}> not found")

@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, session: Session = Depends(database.get_session), current_user = Depends(jwtUtil.get_current_user)):
    query = session.query(model.Post).filter(model.Post.id == post_id)
    post = query.first()
    if post is not None:
        if post.post_user_id == current_user.id:
            query.delete(synchronize_session=False)
            session.commit()
            return
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"Unauthorised to delete post with <id: {post_id}>")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with <id: {post_id}> not found")