from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from .. import model, schema
from ..util import passwordUtil
from ..database import get_session

router = APIRouter(
    prefix='/users',
    tags=['Users']
)

@router.post(path='' ,status_code=status.HTTP_201_CREATED, response_model=schema.User.UserResponse)
def create_user(user: schema.User.UserCreate, session: Session = Depends(get_session)):
    user.password = passwordUtil.hash(user.password)
    user = model.User(**user.dict())
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.get("/{user_id}", response_model=schema.User.UserResponse)
def read_user(user_id: int, session: Session = Depends(get_session)):
    user = session.query(model.User).filter(model.User.id == user_id).first()
    if user:
        return user
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with <id: {user_id}> not found")