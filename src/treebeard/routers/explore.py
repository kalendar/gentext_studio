from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter

from treebeard.database.queries import all_textbooks
from treebeard.dependencies import ReadSession, Templates

router = APIRouter(prefix="/explore")


@router.get("/textbooks", response_model=None)
async def get_textbooks(
    request: Request,
    read_session: ReadSession,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    textbooks = all_textbooks(session=read_session)

    return templates.TemplateResponse(
        request=request,
        name="select_textbook.jinja",
        context={"textbooks": textbooks},
    )
