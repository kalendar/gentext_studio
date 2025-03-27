from __future__ import annotations

import datetime
import uuid
from typing import Literal, Union

from leaflock.sqlalchemy_tables.base import Base
from pydantic import BaseModel, Field
from sqlalchemy import (
    Dialect,
    String,
    TypeDecorator,
)
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column


class Message(BaseModel):
    content: str


class SystemMessage(Message):
    role: Literal["system"] = "system"


class UserMessage(Message):
    role: Literal["user"] = "user"


class AssistantMessage(Message):
    role: Literal["assistant"] = "assistant"


ChatMessage = Union[SystemMessage, UserMessage, AssistantMessage]


class ChatMessages(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list)


class ChatMessagesType(TypeDecorator):  # type: ignore
    impl = String
    cache_ok = True

    def process_bind_param(self, value: ChatMessages, dialect: Dialect):  # type: ignore
        return value.model_dump_json()

    def process_result_value(self, value: str, dialect: Dialect):  # type: ignore
        return ChatMessages.model_validate_json(value)


class Chat(MappedAsDataclass, Base):
    __tablename__ = "chat"

    guid: Mapped[uuid.UUID] = mapped_column(
        init=False, primary_key=True, insert_default=uuid.uuid4
    )

    start_time: Mapped[datetime.datetime]

    textbook_guid: Mapped[uuid.UUID]
    topic_guid: Mapped[uuid.UUID]
    activity_guid: Mapped[uuid.UUID]

    chat_data: Mapped[ChatMessages] = mapped_column(ChatMessagesType)

    def __hash__(self) -> int:
        return hash(self.guid)
