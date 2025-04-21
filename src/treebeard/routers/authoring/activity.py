import uuid
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from leaflock.licenses import License
from leaflock.sqlalchemy_tables.activity import Activity
from leaflock.sqlalchemy_tables.topic import Topic
from pydantic import BaseModel
from sqlalchemy import select
from starlette import status

from treebeard.dependencies import ReadSession, Templates, WriteSession

router = APIRouter(prefix="/authoring")


class ActivityModel(BaseModel):
    name: str

    description: str
    prompt: str

    sources: str
    authors: str

    license: License

    textbook_guid: uuid.UUID
    topic_guids: Optional[set[uuid.UUID] | uuid.UUID] = None


@router.get("/create/activity/{textbook_ident}", response_class=HTMLResponse)
def create_activity_get(
    request: Request,
    textbook_ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    topics = session.scalars(
        select(Topic)
        .where(Topic.textbook_guid == textbook_ident)
        .order_by(Topic.position.asc())
    )

    return templates.TemplateResponse(
        request=request,
        name="authoring/form/activity.jinja",
        context={
            "textbook_ident": textbook_ident,
            "topics": topics,
            "hx_post": request.url_for("create_activity_post"),
        },
    )


@router.post("/create/activity", response_class=HTMLResponse)
def create_activity_post(
    request: Request,
    activity_model: ActivityModel,
    session: WriteSession,
):
    activity = Activity(
        name=activity_model.name,
        description=activity_model.description,
        prompt=activity_model.prompt,
        authors=activity_model.authors,
        sources=activity_model.sources,
        license=activity_model.license,
    )

    activity.textbook_guid = activity_model.textbook_guid

    # In the case of one selected topic, it returns int not list[int]
    topic_guids = (
        activity_model.topic_guids
        if isinstance(activity_model.topic_guids, set)
        else set([activity_model.topic_guids])
    )

    activity.topics = set(
        session.scalars(select(Topic).where(Topic.guid.in_(topic_guids))).all()
    )

    session.add(activity)

    return HTMLResponse(
        headers={
            "HX-Location": str(
                request.url_for("textbook_details", ident=activity_model.textbook_guid)
            )
        }
    )


@router.get(
    "/update/activity/{activity_ident}/{textbook_ident}", response_class=HTMLResponse
)
def update_activity_get(
    request: Request,
    activity_ident: uuid.UUID,
    textbook_ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    activity = session.get(Activity, ident=activity_ident)

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    topics = session.scalars(
        select(Topic)
        .where(Topic.textbook_guid == textbook_ident)
        .order_by(Topic.position.asc())
    )

    return templates.TemplateResponse(
        request=request,
        name="authoring/form/activity.jinja",
        context={
            "activity": activity,
            "textbook_ident": textbook_ident,
            "topics": topics,
            "hx_post": request.url_for("update_activity_post", ident=activity_ident),
            "submission_text": "Update Activity",
        },
    )


@router.post("/update/activity/{ident}", response_class=HTMLResponse)
def update_activity_post(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
    activity_model: ActivityModel,
):
    activity = session.get(Activity, ident=ident)

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    # In the case of one selected topic, it returns uuid.UUID not list[uuid.UUID]
    topic_guids = (
        activity_model.topic_guids
        if isinstance(activity_model.topic_guids, set)
        else [activity_model.topic_guids]
    )

    activity.topics = set(
        session.scalars(select(Topic).where(Topic.guid.in_(topic_guids))).all()
    )

    activity.name = activity_model.name
    activity.description = activity_model.description
    activity.prompt = activity_model.prompt
    activity.authors = activity_model.authors
    activity.sources = activity_model.sources
    activity.license = activity_model.license

    # Ensure dirty
    session.add(activity)

    return HTMLResponse(
        headers={
            "HX-Location": str(
                request.url_for("textbook_details", ident=activity.textbook_guid)
            )
        }
    )


@router.post("/delete/activity/{ident}", response_class=HTMLResponse)
def delete_activity(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
):
    activity = session.get(Activity, ident=ident)

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    textbook_guid = activity.textbook_guid

    session.delete(activity)

    return HTMLResponse(
        headers={
            "HX-Location": str(request.url_for("textbook_details", ident=textbook_guid))
        }
    )


@router.post("/reorder/activities/", response_class=HTMLResponse)
def reorder_activities(
    request: Request,
    session: WriteSession,
    activity_idents: list[uuid.UUID],
):
    for index, activity_ident in enumerate(activity_idents):
        topic = session.get(Activity, activity_ident)

        if not topic:
            continue

        topic.position = index
        session.add(topic)

    return HTMLResponse(content="Successful reordering", status_code=status.HTTP_200_OK)
