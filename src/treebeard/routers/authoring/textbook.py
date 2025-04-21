import tempfile
import uuid

from fastapi import HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.routing import APIRouter
from leaflock.conversion import sqla_to_pydantic
from leaflock.sqlalchemy_tables.textbook import Textbook, TextbookStatus
from pydantic import BaseModel
from sqlalchemy import select

from treebeard.dependencies import ReadSession, Templates, WriteSession

router = APIRouter(prefix="/authoring")


class TextbookModel(BaseModel):
    title: str

    status: TextbookStatus
    edition: str

    prompt: str

    authors: str
    reviewers: str


@router.get("/textbooks", response_class=HTMLResponse)
def textbooks(
    request: Request,
    session: ReadSession,
    templates: Templates,
):
    textbooks = session.scalars(select(Textbook)).all()

    return templates.TemplateResponse(
        request=request,
        name="authoring/textbooks.jinja",
        context={"textbooks": textbooks},
    )


@router.get("/get/textbook/{ident}", response_class=HTMLResponse)
def textbook_details(
    request: Request,
    ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    textbook = session.get(Textbook, ident=ident)

    return templates.TemplateResponse(
        request=request,
        name="authoring/get/textbook.jinja",
        context={"textbook": textbook},
    )


@router.get("/create/textbook", response_class=HTMLResponse)
def create_textbook_get(
    request: Request,
    templates: Templates,
):
    return templates.TemplateResponse(
        request=request,
        name="authoring/form/textbook.jinja",
        context={"hx_post": request.url_for("create_textbook_post")},
    )


@router.post("/create/textbook", response_class=HTMLResponse)
def create_textbook_post(
    request: Request,
    textbook_model: TextbookModel,
    session: WriteSession,
):
    session.add(Textbook(**textbook_model.model_dump()))

    return HTMLResponse(headers={"HX-Location": str(request.url_for("textbooks"))})


@router.get("/update/textbook/{ident}", response_class=HTMLResponse)
def update_textbook_get(
    request: Request,
    ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    textbook = session.get(Textbook, ident=ident)

    return templates.TemplateResponse(
        request=request,
        name="authoring/form/textbook.jinja",
        context={
            "textbook": textbook,
            "hx_post": request.url_for("update_textbook_post", ident=ident),
            "submission_text": "Update GOLE",
        },
    )


@router.post("/update/textbook/{ident}", response_class=HTMLResponse)
def update_textbook_post(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
    textbook_model: TextbookModel,
):
    textbook = session.get(Textbook, ident=ident)

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
def delete_textbook(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
):
    textbook = session.get(Textbook, ident=ident)

    if not textbook:
        raise HTTPException(status_code=404, detail="Textbook not found")

    session.delete(textbook)

    return HTMLResponse(headers={"HX-Location": str(request.url_for("textbooks"))})


@router.get("/export/textbook/{ident}")
def export_textbook(
    request: Request,
    ident: uuid.UUID,
    session: ReadSession,
):
    textbook = session.get(Textbook, ident=ident)

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
