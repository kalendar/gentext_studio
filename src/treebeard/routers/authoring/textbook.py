import tempfile
import uuid

from fastapi import Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from leaflock.conversion import sqla_to_pydantic
from leaflock.sqlalchemy_tables.textbook import Textbook, TextbookStatus
from pydantic import BaseModel
from sqlalchemy.orm import Session

from treebeard.dependencies import (
    ReadSession,
    Templates,
    WriteSession,
    get_current_user,
)

router = APIRouter(prefix="/authoring")


class TextbookModel(BaseModel):
    title: str

    status: TextbookStatus
    edition: str

    prompt: str

    authors: str
    reviewers: str


async def user_textbook_authorized(
    session: Session,
    request: Request,
    textbook_ident: uuid.UUID,
) -> bool:
    user = await get_current_user(request=request, session=session)

    if not user:
        raise ValueError("User does not exist!")

    textbook = session.get(Textbook, textbook_ident)
    if not textbook:
        raise ValueError(f"Textbook {textbook_ident} does not exist!")

    if textbook not in user.owned_textbooks:
        return False
    else:
        return True


@router.get("/textbooks", response_class=HTMLResponse)
async def textbooks(
    request: Request,
    session: ReadSession,
    templates: Templates,
):
    current_user = await get_current_user(request=request, session=session)

    if not current_user:
        return RedirectResponse(request.url_for("root"))

    textbooks = current_user.owned_textbooks

    return templates.TemplateResponse(
        request=request,
        name="authoring/textbooks.jinja",
        context={"textbooks": textbooks},
    )


@router.get("/get/textbook/{ident}", response_class=HTMLResponse)
async def textbook_details(
    request: Request,
    ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    is_authorized: bool = await user_textbook_authorized(
        session=session,
        request=request,
        textbook_ident=ident,
    )

    if not is_authorized:
        return HTTPException(status_code=401, detail="Not Authorized")

    textbook = session.get(Textbook, ident)

    return templates.TemplateResponse(
        request=request,
        name="authoring/get/textbook.jinja",
        context={"textbook": textbook},
    )


@router.get("/create/textbook", response_class=HTMLResponse)
async def create_textbook_get(
    request: Request,
    session: ReadSession,
    templates: Templates,
):
    current_user = await get_current_user(request=request, session=session)

    if not current_user:
        return RedirectResponse(request.url_for("root"))

    return templates.TemplateResponse(
        request=request,
        name="authoring/form/textbook.jinja",
        context={"hx_post": request.url_for("create_textbook_post")},
    )


@router.post("/create/textbook", response_class=HTMLResponse)
async def create_textbook_post(
    request: Request,
    session: WriteSession,
    textbook_model: TextbookModel = Form(),
):
    current_user = await get_current_user(request=request, session=session)

    if not current_user:
        return HTTPException(status_code=401, detail="Not Authorized")

    new_textbook = Textbook(**textbook_model.model_dump())
    owned_textbooks = current_user.owned_textbooks.copy()
    owned_textbooks.add(new_textbook)
    current_user.owned_textbooks = owned_textbooks

    session.add(new_textbook)

    return HTMLResponse(headers={"HX-Location": str(request.url_for("textbooks"))})


@router.get("/update/textbook/{ident}", response_class=HTMLResponse)
async def update_textbook_get(
    request: Request,
    ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    is_authorized: bool = await user_textbook_authorized(
        session=session,
        request=request,
        textbook_ident=ident,
    )

    if not is_authorized:
        return HTTPException(status_code=401, detail="Not Authorized")

    textbook = session.get(Textbook, ident)

    return templates.TemplateResponse(
        request=request,
        name="authoring/form/textbook.jinja",
        context={
            "textbook": textbook,
            "hx_post": request.url_for("update_textbook_post", ident=ident),
            "submission_text": "Update Generative Textbook",
        },
    )


@router.post("/update/textbook/{ident}", response_class=HTMLResponse)
async def update_textbook_post(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
    textbook_model: TextbookModel = Form(),
):
    is_authorized: bool = await user_textbook_authorized(
        session=session,
        request=request,
        textbook_ident=ident,
    )

    if not is_authorized:
        return HTTPException(status_code=401, detail="Not Authorized")

    textbook = session.get(Textbook, ident)

    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")

    textbook.title = textbook_model.title
    textbook.status = textbook_model.status
    textbook.edition = textbook_model.edition
    textbook.prompt = textbook_model.prompt
    textbook.authors = textbook_model.authors
    textbook.reviewers = textbook_model.reviewers

    # Ensure dirty
    session.add(textbook)

    return HTMLResponse(
        headers={"HX-Location": str(request.url_for("textbook_details", ident=ident))}
    )


@router.post("/delete/textbook/{ident}", response_class=HTMLResponse)
async def delete_textbook(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
):
    is_authorized: bool = await user_textbook_authorized(
        session=session,
        request=request,
        textbook_ident=ident,
    )

    if not is_authorized:
        return HTTPException(status_code=401, detail="Not Authorized")

    textbook = session.get(Textbook, ident)

    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")

    session.delete(textbook)

    return HTMLResponse(headers={"HX-Location": str(request.url_for("textbooks"))})


@router.get("/export/textbook/{ident}")
async def export_textbook(
    request: Request,
    ident: uuid.UUID,
    session: ReadSession,
):
    is_authorized: bool = await user_textbook_authorized(
        session=session,
        request=request,
        textbook_ident=ident,
    )

    if not is_authorized:
        return HTTPException(status_code=401, detail="Not Authorized")

    textbook = session.get(Textbook, ident)

    if textbook is None:
        raise ValueError(f"Textbook with guid: {ident} not found.")

    model = sqla_to_pydantic(sqla_textbook=textbook)
    json = model.model_dump_json()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".gt") as tmp_file:
        tmp_file.write(json.encode("utf-8"))
        tmp_file_path = tmp_file.name

    return FileResponse(
        path=tmp_file_path,
        media_type="application/json",
        filename=f"{textbook.title}.gt",
    )
