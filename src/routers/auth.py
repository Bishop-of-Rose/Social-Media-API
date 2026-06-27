from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..config import settings
from ..util import passwordUtil, jwtUtil
from .. import database, schema, model

route = APIRouter(
    prefix='/auth',
    tags=['Authentication']
)

@route.post("/login", response_model=schema.Auth.Token)
def login(response: Response, credentials: OAuth2PasswordRequestForm = Depends(),
          session: Session = Depends(database.get_session)):
    query = session.query(model.User).filter(model.User.username == credentials.username).all()
    user = None
    if not query:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Invalid Credentials")

    for current in query:
        if passwordUtil.verify(credentials.password, str(current.password)):
            user = current

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Invalid Credentials")

    tokens = jwtUtil.create_tokens(str(user.id))
    to_whitelist = {
        "jti": tokens.get("refresh_jti"),
        "expire": str(tokens.get("refresh_expire"))
    }

    to_whitelist = model.Whitelist(**to_whitelist)
    session.add(to_whitelist)
    session.commit()

    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False
    )

    return {"access_token": tokens.get("access_token")}

@route.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response, refresh_payload: dict = Depends(jwtUtil.verify_refresh_token),
           session: Session = Depends(database.get_session), current_user = Depends(jwtUtil.get_current_user)):
    jti = refresh_payload.get("jti")
    user_id = refresh_payload.get("sub")

    if not str(current_user.id) == user_id:
        print(current_user.id, user_id, type(current_user.id), type(user_id))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized Logout Attempted")

    whitelisted = session.query(model.Whitelist).filter(model.Whitelist.jti == str(jti))
    whitelisted.delete(synchronize_session=False)
    session.commit()

    response.delete_cookie("refresh_token")
    return

@route.post("/refresh")
def refresh_access_token(response: Response, refresh_payload: dict = Depends(jwtUtil.verify_refresh_token),
                         session: Session = Depends(database.get_session)):
    user_id = refresh_payload.get("sub")
    jti = refresh_payload.get("jti")

    whitelisted = session.query(model.Whitelist).filter(model.Whitelist.jti == str(jti))
    whitelisted.delete()

    tokens = jwtUtil.create_tokens(str(user_id))
    to_whitelist = {
        "jti": tokens.get("refresh_jti"),
        "expire": str(tokens.get("refresh_expire"))
    }

    to_whitelist = model.Whitelist(**to_whitelist)
    session.add(to_whitelist)
    session.commit()

    response.set_cookie(
        key="refresh_token",
        value=tokens.get("refresh_token"),
        httponly=True,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        secure=False
    )

    return {"access_token": tokens.get("access_token")}