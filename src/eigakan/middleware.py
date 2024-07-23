from http import HTTPStatus
from types import MappingProxyType

from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import FileResponse

from .env import APP


class StaticMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if response.status_code == HTTPStatus.NOT_FOUND:
            if APP.STATIC_DIR:
                return FileResponse(APP.STATIC_DIR / "index.html")
        return response


frontend_middlewares = [
    Middleware(GZipMiddleware, minimum_size=1000),
    Middleware(StaticMiddleware),
]

app_middlewares = [
    Middleware(GZipMiddleware, minimum_size=1000),
    # Middleware(HTTPSRedirectMiddleware),
]
api_middlewares = [
    Middleware(GZipMiddleware, minimum_size=1000),
]
MIDDLEWARES = MappingProxyType(
    {
        "frontend": frontend_middlewares,
        "app": app_middlewares,
        "api": api_middlewares,
    }
)
