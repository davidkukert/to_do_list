from datetime import datetime
from uuid import UUID, uuid8

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

table_register = registry()


@table_register.mapped_as_dataclass()
class User:
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default_factory=uuid8, init=False
    )
    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), init=False
    )
