from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from treebeard.dependencies import Templates
from treebeard.routers import explore
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


@app.get("/", response_class=HTMLResponse)
async def root(request: Request, templates: Templates):
    return templates.TemplateResponse(request=request, name="base.jinja")
