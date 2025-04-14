from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette import status
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware

from treebeard.middleware import AuthMiddleware
from treebeard.routers import auth, import_, user
from treebeard.routers.authoring import activity, textbook, topic
from treebeard.routers.interaction import chat, explore
from treebeard.settings import SETTINGS

__middlewares: list[Middleware] = []


if SETTINGS.authorization and SETTINGS.session_key:
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
app.include_router(activity.router)
app.include_router(textbook.router)
app.include_router(topic.router)

if SETTINGS.authorization:
    app.include_router(auth.router)
    app.include_router(user.router)


@app.get("/")
async def root(request: Request):
    return RedirectResponse(
        request.url_for("get_textbooks"),
        status_code=status.HTTP_302_FOUND,
    )
