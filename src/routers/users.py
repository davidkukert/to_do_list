from uuid import UUID

from fastapi import APIRouter, HTTPException
from sqlalchemy import exists, select

from src.db import Session
from src.models import User
from src.schemas import (
    MessageResponse,
    UserCreateInput,
    UserList,
    UserResponse,
    UserUpdateInput,
)

router = APIRouter(
    prefix='/users',
    tags=['Users'],
)


@router.get('/', response_model=UserList)
async def index_users(session: Session):
    list_users = await session.execute(select(User))
    list_users = list_users.scalars().all()
    return dict(data=list_users)


@router.get('/{user_id}', response_model=UserResponse)
async def get_user(user_id: UUID, session: Session):
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, 'User not found')

    return dict(data=user)


@router.post('/', status_code=201, response_model=UserResponse)
async def create_user(data: UserCreateInput, session: Session):
    user = (
        await session.execute(
            select(select(User).filter_by(username=data.username).exists())
        )
    ).scalar_one()

    if user:
        raise HTTPException(409, 'Username not available')

    user = User(**data.model_dump())
    user.hash_password()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return dict(data=user)


@router.put('/{user_id}', response_model=UserResponse)
async def update_user(user_id: UUID, data: UserUpdateInput, session: Session):
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, 'User not found')

    if data.username is not None and data.username != user.username:
        username_already_taken = (
            await session.execute(
                select(
                    exists()
                    .where(User.username == data.username)
                    .where(User.id != user_id)
                )
            )
        ).scalar_one()
        if username_already_taken:
            raise HTTPException(409, 'Username not available')

    for key, value in data.model_dump(exclude_none=True).items():
        setattr(user, key, value)

    if data.password is not None:
        user.hash_password()

    session.add(user)
    await session.commit()
    await session.refresh(user)

    return dict(data=user)


@router.delete('/{user_id}', response_model=MessageResponse)
async def delete_user(user_id: UUID, session: Session):
    user = await session.execute(select(User).where(User.id == user_id))
    user = user.scalar_one_or_none()

    if user is None:
        raise HTTPException(404, 'User not found')

    await session.delete(user)
    await session.commit()

    return dict(message='User deleted')
