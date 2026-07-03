from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from .. import model, schema, database
from ..util import passwordUtil, jwtUtil

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post(path='' , status_code=status.HTTP_201_CREATED, response_model=schema.User.UserResponse)
def create_user(user: schema.User.UserCreate, session: Session = Depends(database.get_session)):
    user.password = passwordUtil.hash(user.password)
    user = model.User(**user.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{user_id}", response_model=schema.User.UserResponse)
def read_user(user_id: int, session: Session = Depends(database.get_session)):
    user = session.query(model.User).filter(model.User.id == user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with <id: {user_id}> not found")

@router.put("/{user_id}", response_model=schema.User.UserResponse)
def update_user(user_id, edit: schema.User.UserUpdate, session: Session = Depends(database.get_session),
                current_user = Depends(jwtUtil.get_current_user)):
    query = session.query(model.User).filter(model.User.id == user_id)
    user = query.first()
    if user is not None:
        if user.id == current_user.id:
            query.filter(model.User.id == user_id).update(edit.model_dump(), synchronize_session=False)
            session.commit()
            session.refresh(user)
            return user
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"Unauthorized to update user with <id: {user_id}>")

    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with <id: {user_id}> not found")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(database.get_session),
                current_user = Depends(jwtUtil.get_current_user)):
    query = session.query(model.User).filter(model.User.id == user_id)
    user = query.first()
    if user is not None:
        if user.id == current_user.id:
            query.delete(synchronize_session=False)
            session.commit()
            return
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail=f"Unauthorised to delete user with <id: {user_id}>")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with <id: {user_id}> not found")
