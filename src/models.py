from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

from src.enums import ToDoStatus
from src.security.hash import hash_password, verify_password

table_register = registry()


@table_register.mapped_as_dataclass()
class User:
    __tablename__ = 'users'

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default_factory=uuid7, init=False
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

    todos: Mapped[list['ToDo']] = relationship(
        init=False,
        back_populates='user',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def hash_password(self):
        self.password = hash_password(self.password)

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password)


@table_register.mapped_as_dataclass()
class ToDo:
    __tablename__ = 'todos'

    id: Mapped[UUID] = mapped_column(
        primary_key=True, default_factory=uuid7, init=False
    )
    title: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    status: Mapped[ToDoStatus] = mapped_column(String())
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        init=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now(), init=False
    )
    done_at: Mapped[datetime | None] = mapped_column(nullable=True, init=False)

    user_id: Mapped[UUID] = mapped_column(ForeignKey(User.id))
    user: Mapped[User] = relationship(back_populates='todos', init=False)
