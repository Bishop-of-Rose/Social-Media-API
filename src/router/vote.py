from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from .. import model, schema, database
from ..util import jwtUtil

router = APIRouter(
    prefix='/votes',
    tags=['Votes']
)

@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def create_vote(vote: schema.Vote.VoteBase, session: Session = Depends(database.get_session), current_user = Depends(jwtUtil.get_current_user)):
    post_query = session.query(model.Post).filter(model.Post.id == vote.post_id)
    if not post_query.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with <id: {vote.post_id}> not found>"
                            )

    query = (session.query(model.Vote)
             .filter(model.Vote.vote_post_id == vote.post_id,
                     model.Vote.vote_user_id == current_user.id))

    if vote.dir:
        if query.first():
            if query.first().type == vote.type:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                    detail=f"User with <id: {current_user.id}> has a {vote.type} on post with <id: {vote.post_id}>")

            elif query.first().type == "like":
                query.update({"type": "dislike"}, synchronize_session=False)
                post_query.update({"likes": post_query.first().likes - 1})

            elif query.first().type == "dislike":
                query.update({"type": "like"}, synchronize_session=False)
                post_query.update({"dislikes": post_query.first().dislikes - 1})

        else:
            session.add(model.Vote(vote_post_id=vote.post_id, vote_user_id=current_user.id, type=vote.type))

        if vote.type == "like":
            post_query.update({"likes": post_query.first().likes + 1}, synchronize_session=False)

        elif vote.type == "dislike":
            post_query.update({"dislikes": post_query.first().dislikes + 1}, synchronize_session=False)

        session.commit()
        return {"message": f"Successfully added {vote.type}"}

    else:
        if not query.first():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with <id: {current_user.id}> has no {vote.type} on post with <id: {vote.post_id}>")

        if vote.type == "like" and query.first().type == "like":
            post_query.update({"likes": post_query.first().likes - 1}, synchronize_session=False)

        elif vote.type == "dislike" and query.first().type == "dislike":
            post_query.update({"dislikes": post_query.first().dislikes - 1}, synchronize_session=False)

        elif vote.type == "like" and query.first().type == "dislike":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with <id: {current_user.id}> has no {vote.type} on post with <id: {vote.post_id}>")

        elif vote.type == "dislike" and query.first().type == "like":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"User with <id: {current_user.id}> has no {vote.type} on post with <id: {vote.post_id}>")

        query.delete(synchronize_session=False)
        session.commit()
        return {"message": f"Successfully deleted {vote.type}"}