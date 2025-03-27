from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette import status

from treebeard.routers import chat, explore, import_
from treebeard.settings import SETTINGS

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.mount(
    path="/static",
    app=StaticFiles(directory=str(SETTINGS.root_path / "static")),
    name="static",
)

app.include_router(explore.router)
app.include_router(import_.router)
app.include_router(chat.router)


@app.get("/")
async def root(request: Request):
    return RedirectResponse(
        request.url_for("get_textbooks"),
        status_code=status.HTTP_302_FOUND,
    )
