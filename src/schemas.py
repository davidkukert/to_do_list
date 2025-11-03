import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BasicModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, from_attributes=True, alias_generator=to_camel
    )


class MessageResponse(BasicModel):
    message: str


class UserCreateInput(BasicModel):
    username: str
    password: str


class UserUpdateInput(BasicModel):
    username: str | None = None
    password: str | None = None


class UserSchema(BasicModel):
    id: uuid.UUID
    username: str
    created_at: datetime
    updated_at: datetime


class UserResponse(BasicModel):
    data: UserSchema


class UserList(BasicModel):
    data: list[UserSchema]
