from fastapi import Request, UploadFile
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from leaflock.conversion import pydantic_to_sqla
from leaflock.pydantic_models.textbook import Textbook
from starlette import status

from treebeard.dependencies import WriteSession

router = APIRouter(prefix="/import")


@router.post("/textbook", response_model=None)
async def post_import_textbook(
    request: Request,
    write_session: WriteSession,
    textbook_file: UploadFile,
) -> RedirectResponse:
    text = await textbook_file.read()
    model = Textbook.model_validate_json(text.decode("utf-8"))

    write_session.add(pydantic_to_sqla(pydantic_textbook=model))
    write_session.commit()

    return RedirectResponse(
        url=request.url_for("get_textbooks"),
        status_code=status.HTTP_302_FOUND,
    )
