import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from src.db import Session
from src.models import ToDo
from src.schemas import (
    FilterToDo,
    MessageResponse,
    ToDoCreateInput,
    ToDoList,
    ToDoResponse,
    ToDoUpdateInput,
)
from src.security.auth import CurrentUser

router = APIRouter(
    prefix='/todos',
    tags=['ToDos'],
)


@router.post('/', response_model=ToDoResponse)
async def create_todo(
    session: Session,
    data: ToDoCreateInput,
    current_user: CurrentUser,
):
    todo = ToDo(
        title=data.title,
        description=data.description,
        status=data.status,
        user_id=current_user.id,
    )

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return dict(data=todo)


@router.get('/', response_model=ToDoList)
async def list_todos(
    session: Session,
    current_user: CurrentUser,
    todo_filter: Annotated[FilterToDo, Query()],
):
    query = select(ToDo).where(ToDo.user_id == current_user.id)

    if todo_filter.title is not None:
        query = query.filter(ToDo.title.contains(todo_filter.title))

    if todo_filter.description is not None:
        query = query.filter(
            ToDo.description.contains(todo_filter.description)
        )

    if todo_filter.status is not None:
        query = query.filter(ToDo.status == todo_filter.status)

    todos = await session.scalars(query)
    return dict(data=todos.all())


@router.patch('/{todo_id}', response_model=ToDoResponse)
async def patch_todo(
    todo_id: uuid.UUID,
    session: Session,
    current_user: CurrentUser,
    data: ToDoUpdateInput,
):
    todo = await session.scalar(
        select(ToDo).where(ToDo.id == todo_id, ToDo.user_id == current_user.id)
    )

    if todo is None:
        raise HTTPException(404, 'Task not found')

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    if todo.status == 'done':
        todo.done_at = func.now()
    else:
        todo.done_at = None

    session.add(todo)
    await session.commit()
    await session.refresh(todo)

    return dict(data=todo)


@router.delete('/{todo_id}', response_model=MessageResponse)
async def delete_todo(
    todo_id: uuid.UUID,
    session: Session,
    current_user: CurrentUser,
):
    todo = await session.scalar(
        select(ToDo).where(ToDo.id == todo_id, ToDo.user_id == current_user.id)
    )

    if todo is None:
        raise HTTPException(404, 'Task not found')

    await session.delete(todo)
    await session.commit()

    return dict(message='Task has been deleted successfully.')
