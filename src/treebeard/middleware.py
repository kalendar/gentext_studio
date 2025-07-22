import starlette.status as status
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


def unauthorized_path(path: str) -> bool:
    return (
        path.startswith("/login")
        or path.startswith("/auth")
        or path.startswith("/learning/explore")
        or path.startswith("/static/img")
        or path == "/static/css/main.css"
    )


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore
        if unauthorized_path(path=request.url.path):
            return await call_next(request)

        if "session" not in request.scope:
            raise RuntimeError("SessionMiddleware did not process this request!")

        user_email = request.session.get("user_email", False)

        if user_email:
            return await call_next(request)
        else:
            return RedirectResponse(
                url=request.url_for("login"),
                status_code=status.HTTP_302_FOUND,
            )
