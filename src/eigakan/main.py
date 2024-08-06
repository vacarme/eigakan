from fastapi import FastAPI
from starlette.staticfiles import StaticFiles

from .api import router as api_router
from .env import APP
from .handlers import EXC_HANDLERS
from .middleware import MIDDLEWARES
from .slow import limiter

app = FastAPI(
    exception_handlers=EXC_HANDLERS["app"],  # type: ignore
    openapi_url=None,
    middleware=MIDDLEWARES["app"],
)
app.state.limiter = limiter

frontend = FastAPI(openapi_url="", middleware=MIDDLEWARES["frontend"])

api = FastAPI(
    middleware=MIDDLEWARES["api"],
    openapi_url="/docs/openapi.json",
    exception_handlers=EXC_HANDLERS["api"],  # type: ignore
)
api.include_router(api_router)
# we mount the frontend and app
if APP.STATIC_DIR and APP.STATIC_DIR.is_dir():
    frontend.mount("/", StaticFiles(directory=APP.STATIC_DIR), name="app")
app.mount("/api", app=api)
app.mount("/", app=frontend)
