from typing import List
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator, computed_field

from src.schemas import user_schema

class Base(BaseModel):
    commented: UUID | None = None
    replied: UUID | None = None
    content: str

    @model_validator(mode="after")
    def comment_src(self):
        has_commented = self.commented is not None
        has_replied = self.replied is not None

        if has_commented == has_replied:
            raise ValueError("Comment reference <commented | replied> can not be both or neither.")

        return self

class Create(Base):
    pass

class Update(BaseModel):
    content: str

class Response(Base):
    id: UUID
    likes: List[UUID] | None
    dislikes: List[UUID] | None
    created_at: datetime
    updated_at: datetime
    author: user_schema.Response
    replies: List[Response]

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