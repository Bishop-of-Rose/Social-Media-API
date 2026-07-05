from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from src import model, database, blacklist
from src.utils.jwtUtil import detokenize

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme),
                     session: Session = Depends(database.get_session)):
    access_payload = detokenize(token, "Access")
    access_jti = access_payload.get("jti")

    if blacklist.get_jti(access_jti):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Already logged out")

    user_id = access_payload.get("sub")
    user = session.get(model.User, user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="User not found")

    return user