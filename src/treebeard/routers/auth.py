import typing

from authlib.integrations.starlette_client import OAuth  # type: ignore
from fastapi import Request
from fastapi.responses import RedirectResponse
from fastapi.routing import APIRouter
from starlette import status

from treebeard.database.queries import get_user
from treebeard.database.user import Authorizer, User, UserType
from treebeard.dependencies import Templates, WriteSession
from treebeard.settings import SETTINGS

router = APIRouter()
__oauth = OAuth()


@router.get("/login")
async def login(request: Request, templates: Templates):
    return templates.TemplateResponse(
        request=request,
        name="auth.jinja",
        context={
            "SETTINGS": SETTINGS,
        },
    )


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()

    return RedirectResponse(request.url_for("login"))


if SETTINGS.google_oauth:
    __oauth.register(  # type: ignore
        "google",
        client_id=SETTINGS.google_client_id,
        client_secret=SETTINGS.google_client_secret,
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email"},
    )

    @router.get("/login/google")
    async def login_via_google(request: Request) -> RedirectResponse:
        google = __oauth.create_client("google")  # type:ignore
        redirect_uri = request.url_for("authorize_google")
        return await google.authorize_redirect(request, redirect_uri)  # type: ignore

    @typing.no_type_check
    @router.get("/auth/google")
    async def authorize_google(request: Request, session: WriteSession):
        google = __oauth.create_client("google")
        token = await google.authorize_access_token(request)

        email: str = token["userinfo"]["email"]

        user = get_user(
            session=session,
            email=email,
            authorizer=Authorizer.google,
        )

        if not user:
            user = User(
                email=email,
                type=UserType.trial,
                authorizer=Authorizer.google,
            )
            session.add(user)

        request.session.update(
            {
                "user_email": email,
                "user_authorizer": Authorizer.google,
            }
        )

        return RedirectResponse(
            url=request.url_for("root"),
            status_code=status.HTTP_302_FOUND,
        )


if SETTINGS.github_oauth:
    __oauth.register(  # type: ignore
        "github",
        client_id=SETTINGS.github_client_id,
        client_secret=SETTINGS.github_client_secret,
        api_base_url="https://api.github.com/",
        access_token_url="https://github.com/login/oauth/access_token",
        authorize_url="https://github.com/login/oauth/authorize",
        userinfo_endpoint="https://api.github.com/user",
        client_kwargs={"scope": "user:email"},
    )

    @router.get("/login/github")
    async def login_via_github(request: Request) -> RedirectResponse:
        github = __oauth.create_client("github")  # type:ignore
        #redirect_uri = request.url_for("authorize_github")
        redirect_uri = "https://generativetextbooks.org/auth/github"
        return await github.authorize_redirect(request, redirect_uri)  # type: ignore

    @typing.no_type_check
    @router.get("/auth/github")
    async def authorize_github(
        request: Request, session: WriteSession
    ) -> RedirectResponse:
        github = __oauth.create_client("github")

        token = await github.authorize_access_token(request)

        # Get user info
        resp = await github.get("user", token=token)
        data = resp.json()

        email = data.get("email")

        # Fetch primary email if email is not already provided
        if not email:
            email_resp = await github.get("user/emails", token=token)
            email_resp.raise_for_status()
            emails = email_resp.json()
            email = next((e["email"] for e in emails if e["primary"]), None)

        user = get_user(
            session=session,
            email=email,
            authorizer=Authorizer.github,
        )

        if not user:
            user = User(
                email=email,
                type=UserType.trial,
                authorizer=Authorizer.github,
            )
            session.add(user)

        request.session.update(
            {
                "user_email": email,
                "user_authorizer": Authorizer.github,
            }
        )

        return RedirectResponse(
            url=request.url_for("root"),
            status_code=status.HTTP_302_FOUND,
        )
