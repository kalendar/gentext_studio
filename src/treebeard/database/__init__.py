from leaflock.database import create_database
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from treebeard.database.chat import Base, Chat
from treebeard.database.joins import (
    UsersOwnedTextbooks,
    UsersSavedTextbooks,
)
from treebeard.database.user import User

__all__ = [
    "get_sessionmaker",
    "Base",
    "Chat",
    "UsersOwnedTextbooks",
    "UsersSavedTextbooks",
    "User",
]


def get_sessionmaker(database_url: str) -> sessionmaker[Session]:
    create_database(database_url=database_url)
    engine = create_engine(url=database_url)
    # Inject our own tables on top of leaflock tables.
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine)
