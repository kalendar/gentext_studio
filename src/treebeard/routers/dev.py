import uuid
from io import BytesIO

from fastapi import Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.routing import APIRouter
from leaflock.conversion import pydantic_to_sqla, sqla_to_pydantic
from leaflock.pydantic_models.textbook import Textbook
from starlette import status

from treebeard.database.queries import get_textbook
from treebeard.dependencies import ReadSession, Templates, WriteSession

router = APIRouter(prefix="/dev")


@router.get("/import_export_textbook", response_model=None)
async def get_import_textbook(
    request: Request,
    templates: Templates,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dev/import_export_textbook.jinja",
    )


@router.post("/import_textbook", response_model=None)
async def post_import_textbook(
    request: Request,
    write_session: WriteSession,
    textbook_file: UploadFile = Form(),
) -> RedirectResponse:
    text = await textbook_file.read()
    model = Textbook.model_validate_json(text.decode("utf-8"))

    write_session.add(pydantic_to_sqla(pydantic_textbook=model))
    write_session.commit()

    return RedirectResponse(
        url=request.url_for("get_textbooks"),
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/export_textbook", response_model=None)
async def post_export_textbook(
    request: Request,
    read_session: ReadSession,
    textbook_ident: uuid.UUID = Form(),
) -> StreamingResponse:
    textbook = get_textbook(session=read_session, guid=textbook_ident)

    output = BytesIO()
    output.write(sqla_to_pydantic(sqla_textbook=textbook).model_dump_json().encode())
    output.seek(0)

    headers = {"Content-Disposition": 'attachment; filename="textbook.gole"'}

    return StreamingResponse(content=output, headers=headers)
