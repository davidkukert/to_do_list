from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from src.db import Session
from src.models import User
from src.schemas import TokenResponse, UserResponse
from src.security.auth import CurrentUser, create_access_token

router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)
OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.get('/me', response_model=UserResponse)
async def get_current_user(user: CurrentUser):
    return dict(data=user)


@router.post('/token', response_model=TokenResponse)
async def login_for_access_token(form_data: OAuth2Form, session: Session):
    user = await session.execute(
        select(User).filter_by(username=form_data.username)
    )

    user = user.scalar_one_or_none()

    if user is None or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect username or password',
        )

    access_token = create_access_token(data={'sub': str(user.id)})

    return {'access_token': access_token, 'token_type': 'bearer'}


@router.post('/refresh_token', response_model=TokenResponse)
async def refresh_access_token(user: CurrentUser):
    new_access_token = create_access_token(data={'sub': str(user.id)})

    return {'access_token': new_access_token, 'token_type': 'bearer'}
