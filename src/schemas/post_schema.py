from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel, computed_field
from pygments.styles import default

from src.schemas import user_schema, comment_schema


class Base(BaseModel):
    content: str

class Create(Base):
    pass

class Update(Base):
    pass

class Response(Base):
    id: UUID
    likes: List[UUID] | None
    dislikes: List[UUID] | None
    created_at: datetime
    updated_at: datetime
    author: user_schema.Response
    comments: List[comment_schema.Response]

    @computed_field
    @property
    def likes_count(self) -> int:
        return len(self.likes) if self.likes is not None else 0

    @computed_field
    @property
    def dislikes_count(self) -> int:
        return len(self.dislikes) if self.dislikes is not None else 0

    class Config:
        from_attributes = True