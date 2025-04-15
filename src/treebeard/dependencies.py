from pathlib import Path
from typing import Annotated

import jinjax
from fastapi import Depends, Request
from fastapi.templating import Jinja2Templates
from groq import Groq
from pydantic import ValidationError
from sqlalchemy.orm import Session as SQLASession

from treebeard.database import get_sessionmaker
from treebeard.database.queries import get_user
from treebeard.database.user import User
from treebeard.models.request_session import RequestSession
from treebeard.settings import SETTINGS
from treebeard.utils import markdown_to_html

__TREEBEARD_ROOT = Path(__file__).parent.resolve()

__TEMPLATES = Jinja2Templates(directory=str(__TREEBEARD_ROOT / "templates"))
__TEMPLATES.env.add_extension(jinjax.JinjaX)  # type: ignore
__TEMPLATES.env.add_extension("jinja2.ext.do")  # type: ignore
__TEMPLATES.env.globals.update(  # type: ignore
    {
        "SETTINGS": SETTINGS,
        "len": len,
        "sorted": sorted,
        "markdown_to_html": markdown_to_html,
    }
)
__CATALOG = jinjax.Catalog(jinja_env=__TEMPLATES.env)  # type: ignore
__CATALOG.add_folder(
    root_path=str(__TREEBEARD_ROOT / "templates/components"),
    prefix="",
)

__SESSIONMAKER = get_sessionmaker(
    database_url=f"sqlite:///{SETTINGS.sqlite_database_path}"
)

__GROQ_CLIENT: Groq = Groq(api_key=SETTINGS.groq_api_key)


def __get_templates() -> Jinja2Templates:
    return __TEMPLATES


def __get_groq_client():
    global __GROQ_CLIENT
    return __GROQ_CLIENT


async def __get_read_session():
    with __SESSIONMAKER() as session:
        yield session


async def __get_write_session():
    with __SESSIONMAKER.begin() as session:
        yield session


async def __get_current_user(request: Request):
    session = await anext(__get_read_session())

    try:
        request_session = RequestSession.model_validate(
            request.session, from_attributes=True
        )
    except ValidationError:
        return None

    if not request_session.user_email or not request_session.user_authorizer:
        return None

    return get_user(
        session=session,
        email=request_session.user_email,
        authorizer=request_session.user_authorizer,
    )


async def get_current_user(request: Request, session: SQLASession):
    try:
        request_session = RequestSession.model_validate(
            request.session, from_attributes=True
        )
    except ValidationError:
        return None

    if not request_session.user_email or not request_session.user_authorizer:
        return None

    return get_user(
        session=session,
        email=request_session.user_email,
        authorizer=request_session.user_authorizer,
    )


Templates = Annotated[Jinja2Templates, Depends(__get_templates)]
ReadSession = Annotated[SQLASession, Depends(__get_read_session)]
WriteSession = Annotated[SQLASession, Depends(__get_write_session)]
GroqClient = Annotated[Groq, Depends(__get_groq_client)]
CurrentUser = Annotated[User | None, Depends(__get_current_user)]
