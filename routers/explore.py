from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter

from dependencies import LibraryDep, TemplatesDep

router = APIRouter(prefix="/explore")


@router.get("/", response_model=None)
async def select_course(
    request: Request,
    library: LibraryDep,
    templates: TemplatesDep,
) -> HTMLResponse | RedirectResponse:
    return templates.TemplateResponse(
        request=request,
        name="select_course.html",
        context={"courses": library.courses},
    )


@router.get("/{course_name}", response_model=None)
async def select_topic(
    request: Request,
    course_name: str,
    library: LibraryDep,
    templates: TemplatesDep,
) -> HTMLResponse | RedirectResponse:
    selected_course = library.get_course(course_name=course_name)

    if selected_course is None:
        return RedirectResponse(request.url_for("root"))

    return templates.TemplateResponse(
        request=request,
        name="select_topic.html",
        context={"selected_course": selected_course},
    )


@router.get("/{course_name}/{topic_name}", response_model=None)
async def select_activity(
    request: Request,
    course_name: str,
    topic_name: str,
    library: LibraryDep,
    templates: TemplatesDep,
) -> HTMLResponse | RedirectResponse:
    selected_course = library.get_course(course_name=course_name)

    if selected_course is None:
        return RedirectResponse(request.url_for("root"))

    selected_topic = selected_course.topics.get(topic_name, None)

    if selected_topic is None:
        return RedirectResponse(request.url_for("root"))

    return templates.TemplateResponse(
        request=request,
        name="select_activity.html",
        context={
            "course_name": course_name,
            "topic_name": topic_name,
            "selected_course": selected_course,
        },
    )
