import uuid

from fastapi import Depends, HTTPException, status, APIRouter
from psycopg2.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src import model, database, dependencies
from src.schemas import user_schema
from src.utils import passwordUtil

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post(path='' , status_code=status.HTTP_201_CREATED, response_model=user_schema.Response)
def register(user: user_schema.Create,
             session: Session = Depends(database.get_session)):
    user.password = passwordUtil.hash(user.password)
    user = model.User(**user.model_dump())

    try:
        session.add(user)
        session.commit()
        session.refresh(user)

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with that username already exists")

    return user

@router.get("/{user_id}", response_model=user_schema.Response)
def read_user(user_id: uuid.UUID,
              session: Session = Depends(database.get_session),
              current_user = Depends(dependencies.get_current_user)):
    user = session.get(model.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    return user

@router.put("", response_model=user_schema.Response)
def update_user(edit: user_schema.Update,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    user = session.get(model.User, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    user.username = user.username if edit.username is None else edit.username
    user.password = user.password if edit.password is None else passwordUtil.hash(edit.password)

    try:
        session.commit()
        session.refresh(user)

    except IntegrityError as e:
        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with that username already exists")

    return user

@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    user = session.get(model.User, current_user.id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")
    
    session.delete(user)
    session.commit()
    return