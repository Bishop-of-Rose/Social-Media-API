import jwt
import uuid
from datetime import datetime, timedelta, UTC

from fastapi.security import OAuth2PasswordBearer
from fastapi import status, HTTPException
from src.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_DAYS = settings.REFRESH_TOKEN_EXPIRE_DAYS

def tokenize(user_id: uuid.UUID):
    jti = uuid.uuid4()
    access_expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_payload = {
        "sub": str(user_id),
        "jti": str(jti),
        "exp": access_expire,
        "type": "Access"
    }

    refresh_payload = {
        "sub": str(user_id),
        "jti": str(jti),
        "exp": refresh_expire,
        "type": "Refresh"
    }

    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm=ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": access_token, "refresh_token": refresh_token}

def detokenize(token: str | None, token_type: str, suppress: bool = False):
    token_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail=f'Invalid {token_type} token')

    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"{token_type} token not found")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)

        if payload.get("sub") is None:
            raise token_exception

        if payload.get("type") != token_type:
            raise token_exception

    except jwt.ExpiredSignatureError:
        if suppress:
            return jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_exp": False})

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"{token_type} token has expired")


    except jwt.InvalidTokenError:
        raise token_exception

    return payload