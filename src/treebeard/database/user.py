from __future__ import annotations

from enum import StrEnum

from leaflock.sqlalchemy_tables.base import Base
from leaflock.sqlalchemy_tables.textbook import Textbook
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column, relationship


class ChatService(StrEnum):
    integrated = "integrated"
    chatgpt = "https://chatgpt.com/"
    claude = "https://claude.ai/new"
    gemini = "https://gemini.google.com/app"
    copilot = "https://copilot.microsoft.com/"


class Authorizer(StrEnum):
    google = "google"
    github = "github"


class UserType(StrEnum):
    admin = "admin"
    instructor = "instructor"
    trial = "trial"
    student = "student"


class User(MappedAsDataclass, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    authorizer: Mapped[Authorizer] = mapped_column(primary_key=True)
    chat_service: Mapped[ChatService] = mapped_column(default=ChatService.chatgpt)
    chat_whitelisted: Mapped[bool] = mapped_column(default=False)

    type: Mapped[UserType] = mapped_column(default=UserType.trial)

    owned_textbooks: Mapped[set[Textbook]] = relationship(
        secondary="users_owned_textbooks",
        default_factory=set,
    )

    saved_textbooks: Mapped[set[Textbook]] = relationship(
        secondary="users_saved_textbooks",
        default_factory=set,
    )

    used_tokens: Mapped[int] = mapped_column(default=0)

    def __hash__(self) -> int:
        return hash(self.email)
