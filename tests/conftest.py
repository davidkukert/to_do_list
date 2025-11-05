from contextlib import contextmanager
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.app import app
from src.db import get_session
from src.models import table_register
from tests.factories import UserFactory


@pytest.fixture(scope='session')
async def engine():
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')

    async with engine.begin() as conn:
        await conn.run_sync(table_register.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(table_register.metadata.drop_all)


@pytest.fixture(scope='session')
async def session(engine):
    async_session = async_sessionmaker(
        engine,
        expire_on_commit=False,
    )

    async with async_session() as session:
        yield session


@pytest.fixture(scope='session')
async def client(session):
    async def get_session_override():
        return session

    async with AsyncClient(
        transport=ASGITransport(app), base_url='http://test'
    ) as client:
        app.dependency_overrides[get_session] = get_session_override
        yield client

    app.dependency_overrides.clear()


@pytest.fixture(scope='session')
async def user(session):
    password = '12345678'
    user = UserFactory(password=password)
    user.hash_password()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@pytest.fixture(scope='session')
async def another_user(session):
    password = '12345678'
    user = UserFactory(password=password)
    user.hash_password()
    session.add(user)
    await session.commit()
    await session.refresh(user)
    user.clean_password = password
    return user


@contextmanager
def _mock_db_time(*, model, time=datetime(2024, 1, 1)):
    def fake_time_handler(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time
        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_handler)

    yield time

    event.remove(model, 'before_insert', fake_time_handler)


@pytest.fixture
def mock_db_time():
    return _mock_db_time


@pytest.fixture
async def token(client, user):
    response = await client.post(
        '/auth/token',
        data={'username': user.username, 'password': user.clean_password},
    )
    return response.json()['access_token']


@pytest.fixture
async def another_token(client, another_user):
    response = await client.post(
        '/auth/token',
        data={
            'username': another_user.username,
            'password': another_user.clean_password,
        },
    )
    return response.json()['access_token']
