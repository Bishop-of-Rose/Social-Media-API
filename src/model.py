import uuid
from datetime import datetime
from typing import List, Literal

from sqlalchemy import ForeignKey, func, Enum, UniqueConstraint, select, JSON, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property

from .database import Base


class Vote(Base):
    __tablename__ = "votes"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", name="fk_vote_user"), nullable=False)
    post_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE", name="fk_vote_post"))
    comment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE", name="fk_vote_comment"))
    type: Mapped[Literal["LIKE", "DISLIKE"]] = mapped_column(
        Enum("LIKE", "DISLIKE", name="vote_type_enum"),
        nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uq_vote_user_post"),
        UniqueConstraint("user_id", "comment_id", name="uq_vote_user_comment"),
        CheckConstraint(
            "(post_id IS NULL) != (comment_id IS NULL)",
            name="xor_vote_src"
        )
    )

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(nullable=False, unique=True)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", name="fk_post_user"))
    content: Mapped[str] = mapped_column(nullable=False)
    tags: Mapped[List[str]] = mapped_column(JSON, default=[])
    media: Mapped[List[str]] = mapped_column(JSON, default=[])
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped["User"] = relationship()
    comments: Mapped[List["Comment"]] = relationship(passive_deletes=True)

    likes: Mapped[List[uuid.UUID]] = column_property(
        select(func.array_agg(Vote.user_id))
        .where(Vote.post_id == id)
        .where(Vote.type == "LIKE")
        .correlate_except(Vote)
        .scalar_subquery()
    )
    dislikes: Mapped[List[uuid.UUID]] = column_property(
        select(func.array_agg(Vote.user_id))
        .where(Vote.post_id == id)
        .where(Vote.type == "DISLIKE")
        .correlate_except(Vote)
        .scalar_subquery()
    )

class Comment(Base):
    __tablename__ =  "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE", name="fk_comment_user"), nullable=False)
    commented: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE", name="fk_comment_post"))
    replied: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("comments.id", ondelete="CASCADE", name="fk_comment_comment"))
    content: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author: Mapped["User"] = relationship()
    replies: Mapped[List["Comment"]] = relationship(passive_deletes=True)

    likes: Mapped[List[uuid.UUID]] = column_property(
        select(func.array_agg(Vote.user_id))
        .where(Vote.comment_id == id)
        .where(Vote.type == "LIKE")
        .correlate_except(Vote)
        .scalar_subquery()
    )
    dislikes: Mapped[List[uuid.UUID]] = column_property(
        select(func.array_agg(Vote.user_id))
        .where(Vote.comment_id == id)
        .where(Vote.type == "DISLIKE")
        .correlate_except(Vote)
        .scalar_subquery()
    )

    __table_args__ = (
        CheckConstraint(
            "(commented IS NULL) != (replied IS NULL)",
            name="xor_comment_src"
        ),
    )