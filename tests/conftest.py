import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.app import app
from src.db import get_session
from src.models import User, table_register


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
    user = User(username='test', password='12345678')
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.fixture(scope='session')
async def another_user(session):
    user = User(username='test2', password='12345678')
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
