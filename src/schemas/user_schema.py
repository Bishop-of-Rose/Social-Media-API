from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, model_validator

class Create(BaseModel):
    username: str
    password: str

class Update(BaseModel):
    username: str | None = None
    password: str | None = None

    @model_validator(mode='after')
    def user_update(self):
        no_username = self.username is None
        no_password = self.password is None

        print(self.password, type(self.password))
        if no_username and no_password:
            raise ValueError('Username and password fields can not both be empty')

        return self

class Response(BaseModel):
    id: UUID
    username: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True