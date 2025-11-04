from datetime import datetime
from uuid import UUID, uuid8

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, registry

from src.security.hash import hash_password, verify_password

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

    def hash_password(self):
        self.password = hash_password(self.password)

    def verify_password(self, password: str) -> bool:
        return verify_password(password, self.password)
