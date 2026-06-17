from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..util import passwordUtil, jwtUtil
from .. import database, schema, model

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post("/login", response_model=schema.Auth.Token)
def login(credentials: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(database.get_session)):
    user = session.query(model.User).filter(model.User.username == credentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")

    if not passwordUtil.verify(credentials.password, str(user.password)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")

    token = jwtUtil.create_access_token({"user_id": user.id})

    return {"access_token": token}