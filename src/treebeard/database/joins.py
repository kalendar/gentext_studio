import uuid

from leaflock.sqlalchemy_tables.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class UsersSavedTextbooks(MappedAsDataclass, Base):
    __tablename__ = "users_saved_textbooks"

    user_email: Mapped[str] = mapped_column(
        ForeignKey("users.email"),
        primary_key=True,
    )

    textbook_guid: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("textbooks.guid"),
        primary_key=True,
    )


class UsersOwnedTextbooks(MappedAsDataclass, Base):
    __tablename__ = "users_owned_textbooks"

    user_email: Mapped[str] = mapped_column(
        ForeignKey("users.email"),
        primary_key=True,
    )

    textbook_guid: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("textbooks.guid"),
        primary_key=True,
    )
