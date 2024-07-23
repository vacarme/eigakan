from typing import Annotated

from fastapi import Depends, Query

from eigakan.core.updaters import Pagination as _Pagination


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
