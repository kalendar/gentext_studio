import uuid

from fastapi import Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter
from leaflock.licenses import License
from leaflock.sqlalchemy_tables.topic import Topic
from pydantic import BaseModel
from starlette import status

from treebeard.dependencies import ReadSession, Templates, WriteSession

router = APIRouter(prefix="/authoring")


class TopicModel(BaseModel):
    name: str

    outcomes: str
    summary: str

    sources: str
    authors: str

    license: License

    textbook_guid: uuid.UUID


@router.get("/create/topic/{textbook_ident}", response_class=HTMLResponse)
def create_topic_get(
    request: Request,
    textbook_ident: uuid.UUID,
    templates: Templates,
):
    return templates.TemplateResponse(
        request=request,
        name="authoring/form/topic.jinja",
        context={
            "textbook_ident": textbook_ident,
            "hx_post": request.url_for("create_topic_post"),
        },
    )


@router.post("/create/topic", response_class=HTMLResponse)
def create_topic_post(
    request: Request,
    topic_model: TopicModel,
    session: WriteSession,
):
    topic = Topic(
        name=topic_model.name,
        outcomes=topic_model.outcomes,
        summary=topic_model.summary,
        sources=topic_model.sources,
        authors=topic_model.authors,
        license=topic_model.license,
    )

    topic.textbook_guid = topic_model.textbook_guid

    session.add(topic)

    return HTMLResponse(
        headers={
            "HX-Location": str(
                request.url_for("textbook_details", ident=topic_model.textbook_guid)
            )
        }
    )


@router.get("/update/topic/{topic_ident}/{textbook_ident}", response_class=HTMLResponse)
def update_topic_get(
    request: Request,
    topic_ident: uuid.UUID,
    textbook_ident: uuid.UUID,
    session: ReadSession,
    templates: Templates,
):
    topic = session.get(Topic, ident=topic_ident)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    return templates.TemplateResponse(
        request=request,
        name="authoring/form/topic.jinja",
        context={
            "topic": topic,
            "textbook_ident": textbook_ident,
            "hx_post": request.url_for("update_topic_post", ident=topic_ident),
            "submission_text": "Update Topic",
        },
    )


@router.post("/update/topic/{ident}", response_class=HTMLResponse)
def update_topic_post(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
    name: str = Form(),
    outcomes: str = Form(),
    summary: str = Form(),
    sources: str = Form(),
    authors: str = Form(),
    license: License = Form(),
    textbook_guid: uuid.UUID = Form(),
):
    topic = session.get(Topic, ident=ident)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    topic.name = name
    topic.outcomes = outcomes
    topic.summary = summary
    topic.sources = sources
    topic.authors = authors
    topic.license = license
    topic.textbook_guid = textbook_guid

    # Ensure dirty
    session.add(topic)

    return RedirectResponse(
        url=request.url_for("textbook_details", ident=textbook_guid),
        status_code=status.HTTP_302_FOUND,
    )


@router.post("/delete/topic/{ident}", response_class=HTMLResponse)
def delete_topic(
    request: Request,
    ident: uuid.UUID,
    session: WriteSession,
):
    topic = session.get(Topic, ident=ident)

    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")

    textbook_guid = topic.textbook_guid

    session.delete(topic)

    return HTMLResponse(
        headers={
            "HX-Location": str(request.url_for("textbook_details", ident=textbook_guid))
        }
    )


@router.post("/reorder/topics/", response_class=HTMLResponse)
def reorder_topics(
    request: Request,
    session: WriteSession,
    topic_idents: list[uuid.UUID],
):
    for index, topic_ident in enumerate(topic_idents):
        topic = session.get(Topic, topic_ident)

        if not topic:
            continue

        topic.position = index
        session.add(topic)

    return HTMLResponse(content="Successful reordering", status_code=status.HTTP_200_OK)
