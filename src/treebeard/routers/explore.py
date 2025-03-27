import uuid

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter

from treebeard.database.queries import all_textbooks
from treebeard.database.queries import get_textbook as get_textbook_
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
        name="explore/textbooks.jinja",
        context={"textbooks": textbooks},
    )


@router.get("/details/textbook/{textbook_guid}", response_model=None)
async def get_textbook(
    request: Request,
    read_session: ReadSession,
    textbook_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    textbook = get_textbook_(session=read_session, guid=textbook_guid)

    return templates.TemplateResponse(
        request=request,
        name="details/textbook.jinja",
        context={"textbook": textbook},
    )


@router.get("/textbook/{textbook_guid}/topics", response_model=None)
async def get_textbook_topics(
    request: Request,
    read_session: ReadSession,
    textbook_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    textbook = get_textbook_(session=read_session, guid=textbook_guid)

    return templates.TemplateResponse(
        request=request,
        name="explore/textbook_topics.jinja",
        context={"textbook": textbook},
    )


@router.get(
    "/textbook/{textbook_guid}/topic/{topic_guid}/activities", response_model=None
)
async def get_textbook_activities(
    request: Request,
    read_session: ReadSession,
    textbook_guid: uuid.UUID,
    topic_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    textbook = get_textbook_(session=read_session, guid=textbook_guid)
    topic = next(
        filter(lambda topic: topic.guid == topic_guid, list(textbook.topics)), None
    )
    if topic is None:
        raise ValueError(
            f"No topic with GUID: {topic_guid} found for textbook with GUID: {textbook_guid}"
        )

    return templates.TemplateResponse(
        request=request,
        name="explore/topic_activities.jinja",
        context={
            "textbook": textbook,
            "topic": topic,
        },
    )
