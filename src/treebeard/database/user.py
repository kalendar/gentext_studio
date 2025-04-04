from __future__ import annotations

from enum import StrEnum

from leaflock.sqlalchemy_tables.base import Base
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class Authorizer(StrEnum):
    google = "google"
    github = "github"


class User(MappedAsDataclass, Base):
    __tablename__ = "user"

    email: Mapped[str] = mapped_column(primary_key=True)
    authorizer: Mapped[Authorizer] = mapped_column(primary_key=True)

    def __hash__(self) -> int:
        return hash(self.email)
