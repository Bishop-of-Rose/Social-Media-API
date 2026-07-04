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
        session.close()

    except IntegrityError as e:
        print(e)

        if isinstance(e.orig, UniqueViolation):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="User with that username already exists")

    return user

@router.get("/{user_id}", response_model=user_schema.Response)
def read_user(user_id: uuid.UUID,
              session: Session = Depends(database.get_session),
              current_user = Depends(dependencies.get_current_user)):
    user = session.get(model.User, user_id)
    session.close()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    return user

@router.put("/{user_id}", response_model=user_schema.Response)
def update_user(user_id: uuid.UUID,
                edit: user_schema.Update,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    user = session.get(model.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    if current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to update user")

    user.username = edit.username
    user.password = passwordUtil.hash(edit.password)
    session.commit()
    session.refresh(user)
    session.close()
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: uuid.UUID,
                session: Session = Depends(database.get_session),
                current_user = Depends(dependencies.get_current_user)):
    user = session.get(model.User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    if current_user.id != user.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized to delete user")

    session.delete(user)
    session.commit()
    session.close()
    return