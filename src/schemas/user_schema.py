from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class Base(BaseModel):
    username: str

class Create(Base):
    password: str

class Update(Base):
    password: str

class Response(Base):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True