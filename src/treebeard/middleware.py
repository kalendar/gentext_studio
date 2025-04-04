import starlette.status as status
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):  # type: ignore
        path = request.url.path
        if path.startswith("/login") or path.startswith("/auth"):
            return await call_next(request)

        if request.url.path == "/static/css/main.css":
            return await call_next(request)

        if "session" not in request.scope:
            raise RuntimeError("SessionMiddleware did not process this request!")

        email = request.session.get("email", False)

        if email:
            return await call_next(request)
        else:
            return RedirectResponse(
                url=request.url_for("login"),
                status_code=status.HTTP_302_FOUND,
            )
