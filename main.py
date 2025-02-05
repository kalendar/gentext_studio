import logging

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette import status

from routers import activity_selection, chat

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(activity_selection.router)
app.include_router(chat.router)


@app.get("/", response_class=HTMLResponse)
async def root(
    request: Request,
):
    return RedirectResponse(
        request.url_for("select_course"),
        status_code=status.HTTP_302_FOUND,
    )
