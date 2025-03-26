from pathlib import Path
from typing import Annotated

import jinjax
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session as SQLASession

from treebeard.database import get_sessionmaker
from treebeard.settings import SETTINGS

__TREEBEARD_ROOT = Path(__file__).parent.resolve()

__TEMPLATES = Jinja2Templates(directory=str(__TREEBEARD_ROOT / "templates"))
__TEMPLATES.env.add_extension(jinjax.JinjaX)  # type: ignore
__CATALOG = jinjax.Catalog(jinja_env=__TEMPLATES.env)  # type: ignore
__CATALOG.add_folder(root_path=str(__TREEBEARD_ROOT / "templates/components"))

__SESSIONMAKER = get_sessionmaker(
    database_url=f"sqlite:///{SETTINGS.sqlite_database_path}"
)


def get_templates() -> Jinja2Templates:
    return __TEMPLATES


def get_read_session() -> SQLASession:
    with __SESSIONMAKER() as session:
        return session


def get_write_session() -> SQLASession:
    with __SESSIONMAKER.begin() as session:
        return session


Templates = Annotated[Jinja2Templates, Depends(get_templates)]
ReadSession = Annotated[SQLASession, Depends(get_read_session)]
WriteSession = Annotated[SQLASession, Depends(get_write_session)]
