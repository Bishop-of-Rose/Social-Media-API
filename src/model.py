from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False)
    password = Column(String, nullable=False)

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    post_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("User")
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    likes = Column(Integer, server_default="0", nullable=False)
    dislikes = Column(Integer, server_default="0", nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text('NOW()'), nullable=False)

class Vote(Base):
    __tablename__ = "votes"

    vote_post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key= True, nullable=False)
    vote_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key= True, nullable=False)
    type = Column(String, nullable=False)

class Whitelist(Base):
    __tablename__ = "whitelist"

    jti = Column(String, primary_key=True, nullable=False, index=True)
    expire = Column(String, nullable=False)