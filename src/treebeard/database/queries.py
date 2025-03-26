from typing import Sequence

from leaflock.sqlalchemy_tables.textbook import Textbook
from sqlalchemy import select
from sqlalchemy.orm import Session


def all_textbooks(session: Session) -> Sequence[Textbook]:
    return session.scalars(select(Textbook)).all()
