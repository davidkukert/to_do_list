import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from src.enums import ToDoStatus


class BasicModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, from_attributes=True, alias_generator=to_camel
    )


class MessageResponse(BasicModel):
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = Field(default='bearer')


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


class ToDoCreateInput(BasicModel):
    title: str
    description: str | None = None
    status: ToDoStatus = Field(default=ToDoStatus.TODO)


class ToDoUpdateInput(BasicModel):
    title: str | None = None
    description: str | None = None
    status: ToDoStatus | None = None


class ToDoSchema(BasicModel):
    id: uuid.UUID
    title: str
    description: str | None = None
    status: ToDoStatus
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    done_at: datetime | None = None


class ToDoResponse(BasicModel):
    data: ToDoSchema


class ToDoList(BasicModel):
    data: list[ToDoSchema]


class FilterToDo(BasicModel):
    title: str | None = None
    description: str | None = None
    status: ToDoStatus | None = None
