import uuid

from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from sqlalchemy import select
from starlette import status

from treebeard.database.joins import UsersSavedTextbooks
from treebeard.dependencies import CurrentUser, Templates, WriteSession

router = APIRouter(prefix="/user")


@router.get("/current")
async def current_user(
    request: Request, templates: Templates, current_user: CurrentUser
):
    return templates.TemplateResponse(
        request=request,
        name="user/page.jinja",
    )


@router.get("/saved_textbooks")
async def saved_textbooks(
    request: Request, templates: Templates, current_user: CurrentUser
):
    if not current_user:
        raise ValueError

    textbooks = current_user.saved_textbooks

    return templates.TemplateResponse(
        request=request,
        name="user/textbooks.jinja",
        context={"textbooks": textbooks, "__globals": {"request": request}},
    )


@router.get("/owned_textbooks")
async def owned_textbooks(
    request: Request, templates: Templates, current_user: CurrentUser
):
    if not current_user:
        raise ValueError

    textbooks = current_user.owned_textbooks

    return templates.TemplateResponse(
        request=request,
        name="interaction/explore/textbooks.jinja",
        context={"textbooks": textbooks, "__globals": {"request": request}},
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
