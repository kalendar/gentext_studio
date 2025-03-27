from pathlib import Path
from typing import Annotated

import jinjax
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from groq import Groq
from sqlalchemy.orm import Session as SQLASession

from treebeard.database import get_sessionmaker
from treebeard.settings import SETTINGS

__TREEBEARD_ROOT = Path(__file__).parent.resolve()

__TEMPLATES = Jinja2Templates(directory=str(__TREEBEARD_ROOT / "templates"))
__TEMPLATES.env.add_extension(jinjax.JinjaX)  # type: ignore
__TEMPLATES.env.globals.update({"len": len, "sorted": sorted})  # type: ignore
__CATALOG = jinjax.Catalog(jinja_env=__TEMPLATES.env)  # type: ignore
__CATALOG.add_folder(root_path=str(__TREEBEARD_ROOT / "templates/components"))

__SESSIONMAKER = get_sessionmaker(
    database_url=f"sqlite:///{SETTINGS.sqlite_database_path}"
)

__GROQ_CLIENT: Groq = Groq(api_key=SETTINGS.grok_api_key)


def __get_templates() -> Jinja2Templates:
    return __TEMPLATES


def __get_read_session() -> SQLASession:
    with __SESSIONMAKER() as session:
        return session


def __get_write_session() -> SQLASession:
    with __SESSIONMAKER.begin() as session:
        return session


def __get_groq_client():
    global __GROQ_CLIENT
    return __GROQ_CLIENT


Templates = Annotated[Jinja2Templates, Depends(__get_templates)]
ReadSession = Annotated[SQLASession, Depends(__get_read_session)]
WriteSession = Annotated[SQLASession, Depends(__get_write_session)]
GroqClient = Annotated[Groq, Depends(__get_groq_client)]
