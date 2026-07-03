from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security import oauth2
from sqlalchemy.orm import Session

from .. import schema, database, model
from ..util import jwtUtil

router = APIRouter(
    prefix="/comment",
    tags=["Comments"],
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_comment(comment, session: Session = Depends(database.get_session), current_user = Depends(jwtUtil.get_current_user),
                   ):
