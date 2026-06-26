import jwt
import uuid
from datetime import datetime, timedelta, UTC

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException, Request
from sqlalchemy.orm import Session

from ..database import get_session
from .. import schema, database, model
from ..config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def create_tokens(user_id: str):
    access_expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    access_jti = str(uuid.uuid4())
    refresh_jti = str(uuid.uuid4())

    access_payload = {
        "sub": user_id,
        "jti": access_jti,
        "exp": access_expire,
        "type": "access"
    }

    refresh_payload = {
        "sub": user_id,
        "jti": refresh_jti,
        "exp": refresh_expire,
        "type": "refresh"
    }

    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "refresh_token": refresh_token, "refresh_jti": refresh_jti, "refresh_expire": refresh_expire}

def decode_token(token: str, token_type: str):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Invalid credentials",
                                          headers={"WWW-Authenticate": "Bearer"})

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

        if not payload.get("type") == token_type:
            raise credentials_exception

    except jwt.PyJWTError:
        raise credentials_exception

    return payload

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(database.get_session)):
    payload = decode_token(token, "access")

    user_id = payload.get("sub")
    user = session.query(model.User).filter(model.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    return user

def verify_refresh_token(request: Request, session: Session = Depends(get_session)):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    payload = decode_token(refresh_token, "refresh")

    jti = payload.get("jti")
    is_whitelisted = session.query(model.Whitelist).filter(model.Whitelist.jti == jti).first()

    if not is_whitelisted:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has been revoked")

    return payload