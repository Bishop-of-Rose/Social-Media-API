from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Literal


class Post:
    class PostBase(BaseModel):
        title: str
        content: str

    class PostCreate(PostBase):
        pass

    class PostUpdate(PostBase):
        pass

    class PostResponse(PostBase):
        id: int
        author: User.UserResponse
        likes: int
        dislikes: int
        created_at: datetime
        updated_at: datetime

        class Config:
            orm_mode = True

class User:
    class UserBase(BaseModel):
        username: str

    class UserCreate(UserBase):
        password: str

    class UserUpdate(UserBase):
        password: str

    class UserResponse(UserBase):
        id: int

        class Config:
            orm_mode = True

class Auth:
    class Token(BaseModel):
        access_token: str

    class TokenData(BaseModel):
        user_id: str

    class Login(BaseModel):
        username: str
        password: str

class Vote:
    class VoteBase(BaseModel):
        post_id: int
        type: Literal["like", "dislike"]
        dir: bool