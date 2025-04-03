from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from treebeard.middleware import AuthMiddleware
from treebeard.routers import auth, chat, explore, import_
from treebeard.settings import SETTINGS

__middlewares: list[Middleware] = []

if SETTINGS.google_oauth:
    if not (SETTINGS.google_client_id and SETTINGS.google_client_secret):
        raise ValueError("Missing Google OAuth environment variables!")

if SETTINGS.github_oauth:
    if not (SETTINGS.github_client_id and SETTINGS.github_client_secret):
        raise ValueError("Missing Github OAuth environment variables!")


if SETTINGS.google_oauth or SETTINGS.github_oauth:
    if not SETTINGS.session_key:
        raise ValueError("Missing session environment variable!")

    __middlewares.extend(
        [
            Middleware(SessionMiddleware, secret_key=SETTINGS.session_key),
            Middleware(AuthMiddleware),
        ]
    )

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    middleware=__middlewares,
)

app.mount(
    path="/static",
    app=StaticFiles(directory=str(SETTINGS.root_path / "static")),
    name="static",
)

app.include_router(explore.router)
app.include_router(import_.router)
app.include_router(chat.router)

if SETTINGS.google_oauth or SETTINGS.github_oauth:
    app.include_router(auth.router)


@app.get("/")
async def root(request: Request):
    return RedirectResponse(
        request.url_for("get_textbooks"),
        status_code=status.HTTP_302_FOUND,
    )
