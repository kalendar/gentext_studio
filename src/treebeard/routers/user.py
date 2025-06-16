import uuid

from fastapi import Form, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy import select
from starlette import status

from treebeard.database.joins import UsersSavedTextbooks
from treebeard.database.user import ChatService
from treebeard.dependencies import (
    CurrentUser,
    Templates,
    WriteSession,
    get_current_user,
)

router = APIRouter(prefix="/user")


@router.get("/current")
async def current_user(
    request: Request,
    templates: Templates,
    current_user: CurrentUser,
):
    if not current_user:
        raise ValueError

    return templates.TemplateResponse(
        request=request,
        name="user/page.jinja",
        context={
            "current_user": current_user,
        },
    )


@router.get("/saved_textbooks")
async def saved_textbooks(
    request: Request,
    templates: Templates,
    current_user: CurrentUser,
):
    if not current_user:
        raise ValueError

    textbooks = current_user.saved_textbooks

    return templates.TemplateResponse(
        request=request,
        name="user/textbooks.jinja",
        context={"textbooks": textbooks},
    )


@router.get("/owned_textbooks")
async def owned_textbooks(
    request: Request,
    templates: Templates,
    current_user: CurrentUser,
):
    if not current_user:
        raise ValueError

    textbooks = current_user.owned_textbooks

    return templates.TemplateResponse(
        request=request,
        name="interaction/explore/textbooks.jinja",
        context={"textbooks": textbooks},
    )


@router.post("/save_textbook/{textbook_guid}")
async def save_textbook(
    request: Request,
    current_user: CurrentUser,
    write_session: WriteSession,
    textbook_guid: uuid.UUID,
):
    if not current_user:
        return HTMLResponse(status_code=status.HTTP_401_UNAUTHORIZED)

    existing_save = write_session.scalar(
        select(UsersSavedTextbooks).where(
            UsersSavedTextbooks.user_email == current_user.email,
            UsersSavedTextbooks.textbook_guid == textbook_guid,
        )
    )

    if not existing_save:
        write_session.add(
            UsersSavedTextbooks(
                user_email=current_user.email,
                textbook_guid=textbook_guid,
            )
        )

    return HTMLResponse(status_code=status.HTTP_201_CREATED)


@router.post("/save_chat_service/")
async def save_chat_service(
    request: Request,
    write_session: WriteSession,
    chat_service: ChatService = Form(),
):
    current_user = await get_current_user(request=request, session=write_session)

    if not current_user:
        return HTMLResponse(status_code=status.HTTP_401_UNAUTHORIZED)

    current_user.chat_service = chat_service

    return HTMLResponse(status_code=status.HTTP_201_CREATED)
