from __future__ import annotations

from enum import StrEnum

from leaflock.sqlalchemy_tables.base import Base
from leaflock.sqlalchemy_tables.textbook import Textbook
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship


class Authorizer(StrEnum):
    google = "google"
    github = "github"


class User(MappedAsDataclass, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    authorizer: Mapped[Authorizer] = mapped_column(primary_key=True)

    owned_textbooks: Mapped[set[Textbook]] = relationship(
        secondary="users_owned_textbooks",
        default_factory=set,
    )

    saved_textbooks: Mapped[set[Textbook]] = relationship(
        secondary="users_saved_textbooks",
        default_factory=set,
    )

    def __hash__(self) -> int:
        return hash(self.email)
