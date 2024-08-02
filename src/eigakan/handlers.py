from http import HTTPStatus
from types import MappingProxyType

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from eigakan.core.exc import DuplicatedResource, ResourceNotFound


async def _resource_not_found(request: Request, exc: ResourceNotFound):
    """
    Return a 404 response when an `ResourceNotFound` is raised by the app.

    Parameters
    ----------
    request : Request
        the request object.
    exc : ResourceNotFound
        rhe exception raised.

    Returns
    -------
    JSONResponse
        A JSON response with a 404 status code

    """
    return JSONResponse(
        status_code=HTTPStatus.NOT_FOUND,
        content=exc.args[0],
    )


async def _duplicated_resource(request: Request, exc: DuplicatedResource):
    """
    Return a 404 response when an `ResourceNotFound` is raised by the app.

    Parameters
    ----------
    request : Request
        the request object.
    exc : ResourceNotFound
        rhe exception raised.

    Returns
    -------
    JSONResponse
        A JSON response with a 404 status code

    """
    return JSONResponse(
        status_code=HTTPStatus.CONFLICT,
        content=exc.args[0],
    )


APP_EXC_HANDLERS = {
    RateLimitExceeded: _rate_limit_exceeded_handler,
}

API_EXC_HANDLERS = {
    ResourceNotFound: _resource_not_found,
    DuplicatedResource: _duplicated_resource,
}

EXC_HANDLERS = MappingProxyType(
    {
        "app": APP_EXC_HANDLERS,
        "api": API_EXC_HANDLERS,
    }
)
