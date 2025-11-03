from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import Settings

engine = create_async_engine(Settings().DATABASE_URL, echo=True)

async_session = async_sessionmaker(
    engine,
    expire_on_commit=False,
)


async def get_session():
    async with async_session() as session:
        yield session


Session = Annotated[AsyncSession, Depends(get_session)]
