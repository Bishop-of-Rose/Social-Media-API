from datetime import datetime, UTC

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from src import model, database, blacklist
from src.schemas import auth_schema
from src.config import settings
from src.utils import jwtUtil

router = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@router.post("/login", response_model=auth_schema.Token)
def login(response: Response,
          credentials: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(database.get_session)):
    stmt = select(model.User).where(model.User.username == credentials.username)
    user: model.User | None = session.scalars(stmt).one_or_none()
    session.close()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid Credentials")

    tokens = jwtUtil.tokenize(user.id)
    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False
    )

    return {"access_token": tokens.get("access_token")}

@router.post("/logout")
def logout(request: Request,
           response: Response):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header"
        )

    access_token = auth_header.split()[1]
    access_payload = jwtUtil.detokenize(access_token, "Access")
    access_jti = access_payload.get("jti")

    if blacklist.get_jti(access_jti):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Already logged out")

    remaining_ttl = int(access_payload.get("exp") - datetime.now(UTC).timestamp())
    if remaining_ttl > 0:
        blacklist.set_jti(access_jti, remaining_ttl)

    response.delete_cookie("refresh_token")
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=auth_schema.Token)
def refresh(request: Request,
            response: Response):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization Header"
        )

    access_token = auth_header.split()[1]
    refresh_token = request.cookies.get("refresh_token")
    access_payload = jwtUtil.detokenize(access_token, "Access", suppress=True)
    refresh_payload = jwtUtil.detokenize(refresh_token, "Refresh")

    access_jti = access_payload.get("jti")
    refresh_jti = refresh_payload.get("jti")
    if access_jti != refresh_jti:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='Access and Refresh tokens not matched')

    remaining_ttl = int(access_payload.get("exp") - datetime.now(UTC).timestamp())
    if remaining_ttl > 0:
        blacklist.set_jti(access_jti, remaining_ttl)

    user_id = access_payload.get("sub")
    tokens = jwtUtil.tokenize(user_id)

    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False
    )

    return {"access_token": tokens.get("access_token")}
