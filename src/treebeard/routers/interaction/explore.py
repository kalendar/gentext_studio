import uuid
from dataclasses import dataclass

from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from leaflock.sqlalchemy_tables import Activity

from treebeard.database.queries import all_textbooks
from treebeard.database.queries import get_chat as get_chat_
from treebeard.database.queries import get_textbook as get_textbook_
from treebeard.database.user import ChatService
from treebeard.dependencies import CurrentUser, ReadSession, Templates
from treebeard.utils import initial_prompt, token_estimate

router = APIRouter(prefix="/learning/explore")


@dataclass
class ActivityModel:
    activity: Activity
    tokens: int
    price: float
    initial_prompt: str


@router.get("/textbooks", response_model=None)
async def get_textbooks(
    request: Request,
    read_session: ReadSession,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    textbooks = all_textbooks(session=read_session)

    return templates.TemplateResponse(
        request=request,
        name="interaction/explore/textbooks.jinja",
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
        name="interaction/details/textbook.jinja",
        context={"textbook": textbook},
    )


@router.get("/details/chat/{chat_guid}", response_model=None)
async def get_chat(
    request: Request,
    read_session: ReadSession,
    chat_guid: str,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    try:
        chat_uuid = uuid.UUID(chat_guid)
    except ValueError:
        raise ValueError(f"Invalid chat GUID format: {chat_guid}")

    chat = get_chat_(session=read_session, guid=chat_uuid)
    if chat is None:
        raise ValueError(f"No chat with GUID: {chat_guid} found!")

    return templates.TemplateResponse(
        request=request,
        name="interaction/details/chat.jinja",
        context={"messages": chat.chat_data.messages},
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
        name="interaction/explore/textbook_topics.jinja",
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
    current_user: CurrentUser,
) -> HTMLResponse | RedirectResponse:
    textbook = get_textbook_(session=read_session, guid=textbook_guid)
    topic = next(
        filter(lambda topic: topic.guid == topic_guid, list(textbook.topics)), None
    )
    if topic is None:
        raise ValueError(
            f"No topic with GUID: {topic_guid} found for textbook with GUID: {textbook_guid}"
        )

    activities = sorted(topic.activities, key=lambda activity: activity.name)

    activity_models: list[ActivityModel] = list()

    for activity in activities:
        initial_prompt_str = initial_prompt(topic=topic, activity=activity)
        tokens = token_estimate(string=initial_prompt_str)

        activity_models.append(
            ActivityModel(
                activity=activity,
                tokens=tokens,
                price=0,
                initial_prompt=initial_prompt_str,
            )
        )

    return templates.TemplateResponse(
        request=request,
        name="interaction/explore/topic_activities.jinja",
        context={
            "textbook": textbook,
            "topic": topic,
            "activity_models": activity_models,
            "chat_service": current_user.chat_service
            if current_user
            else ChatService.chatgpt,
        },
    )


@router.get("/view/activity/{activity_guid}", response_model=None)
async def view_activity(
    request: Request,
    read_session: ReadSession,
    activity_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    # Find the activity by searching through all textbooks
    textbooks = all_textbooks(session=read_session)
    activity = None
    topic = None
    textbook = None

    for tb in textbooks:
        for t in tb.topics:
            for a in t.activities:
                if a.guid == activity_guid:
                    activity = a
                    topic = t
                    textbook = tb
                    break
            if activity:
                break
        if activity:
            break

    if activity is None:
        raise ValueError(f"No activity with GUID: {activity_guid} found!")

    return templates.TemplateResponse(
        request=request,
        name="interaction/view/activity.jinja",
        context={"textbook": textbook, "topic": topic, "activity": activity},
    )


@router.get("/view/textbook/{textbook_guid}", response_model=None)
async def view_textbook(
    request: Request,
    read_session: ReadSession,
    textbook_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    textbook = get_textbook_(session=read_session, guid=textbook_guid)

    return templates.TemplateResponse(
        request=request,
        name="interaction/view/textbook.jinja",
        context={"textbook": textbook},
    )


@router.get("/view/textbook-form/{textbook_guid}", response_model=None)
async def view_textbook_form(
    request: Request,
    read_session: ReadSession,
    textbook_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    """Read-only view of textbook form content"""
    textbook = get_textbook_(session=read_session, guid=textbook_guid)

    return templates.TemplateResponse(
        request=request,
        name="interaction/view/textbook_form.jinja",
        context={"textbook": textbook},
    )


@router.get("/view/topic-form/{topic_guid}", response_model=None)
async def view_topic_form(
    request: Request,
    read_session: ReadSession,
    topic_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    """Read-only view of topic form content"""
    # Find the topic by searching through all textbooks
    textbooks = all_textbooks(session=read_session)
    topic = None
    textbook = None

    for tb in textbooks:
        for t in tb.topics:
            if t.guid == topic_guid:
                topic = t
                textbook = tb
                break
        if topic:
            break

    if topic is None:
        raise ValueError(f"No topic with GUID: {topic_guid} found!")

    return templates.TemplateResponse(
        request=request,
        name="interaction/view/topic_form.jinja",
        context={"textbook": textbook, "topic": topic},
    )


@router.get("/view/activity-form/{activity_guid}", response_model=None)
async def view_activity_form(
    request: Request,
    read_session: ReadSession,
    activity_guid: uuid.UUID,
    templates: Templates,
) -> HTMLResponse | RedirectResponse:
    """Read-only view of activity form content"""
    # Find the activity by searching through all textbooks
    textbooks = all_textbooks(session=read_session)
    activity = None
    topic = None
    textbook = None

    for tb in textbooks:
        for t in tb.topics:
            for a in t.activities:
                if a.guid == activity_guid:
                    activity = a
                    topic = t
                    textbook = tb
                    break
            if activity:
                break
        if activity:
            break

    if activity is None:
        raise ValueError(f"No activity with GUID: {activity_guid} found!")

    return templates.TemplateResponse(
        request=request,
        name="interaction/view/activity_form.jinja",
        context={"textbook": textbook, "topic": topic, "activity": activity},
    )
