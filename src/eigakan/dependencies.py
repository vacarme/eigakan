from typing import Annotated, Type
from uuid import UUID

from fastapi import Depends, Query

from eigakan.core.statement import ReadOneBy
from eigakan.core.updaters import Pagination as _Pagination
from eigakan.types import M


def _parse_pagination(
    page: int = Query(1, ge=1, description="*page's number (1 indexed)*"),
    limit: int = Query(
        20, ge=1, le=100, description="*number of items per page.*"
    ),
) -> _Pagination:
    """
    Dependency for parsing optional query parameters associated to pagination.

    Parameters
    ----------
    page: int, optional
        requested page's number (1 indexed).
    limit: int, optional
        page's length.

    Returns
    -------
    Pagination
        A pagination updater initialized with the parsed parameters.

    """
    return _Pagination(page=page, limit=limit)


Pagination = Annotated[_Pagination, Depends(_parse_pagination)]


class ResourceInjecter:
    def __init__(self, model: Type[M]):
        self._model = model

    async def __call__(self, id: UUID):
        """session could be used here, does it damaged performance ?"""
        return ReadOneBy("id", id, self._model)
