from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session


async def test_get_session():
    session = await anext(get_session())
    assert session is not None
    assert isinstance(session, AsyncSession)
