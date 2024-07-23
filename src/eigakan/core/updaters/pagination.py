"""Pagination Updater."""

from __future__ import annotations

from math import ceil
from typing import TYPE_CHECKING

from .exc import PaginationInvalidArgument
from .updater import Updater

if TYPE_CHECKING:
    from sqlalchemy.sql.expression import Select


class Pagination(Updater):
    """Update a SQLAlchemy statement with a pagination clause."""

    def __init__(self, page: int, limit: int) -> None:
        """
        Initialize the updater.

        Parameters
        ----------
        page : int
            The page number.
        limit : int
            The number of items per page.

        Raises
        ------
        PaginationInvalidArgument
            If the arguments are invalid.

        """
        self._page = self._validated_argument(page)
        self._limit = self._validated_argument(limit)
        self._offset = (page - 1) * limit

    def __eq__(self, other: object) -> bool:
        """Check if two pagination objects are equal."""
        return (
            (self._page == other._page and self._limit == other._limit)
            if isinstance(other, Pagination)
            else False
        )

    @property
    def page(self):
        """Return the page number."""
        return self._page

    def get_total_number_of_pages(self, total_lines: int) -> int:
        """Compute the total number of pages."""
        return ceil(total_lines / self._limit)

    def update(self, statement: Select) -> Select:
        """Update the statement with the proper clauses."""
        return statement.offset(self._offset).limit(self._limit)

    @staticmethod
    def _validated_argument(arg):
        """Raise an error if the arguments are invalid."""
        if arg < 1:
            raise PaginationInvalidArgument(arg)
        return arg

    def __repr__(self):
        """Return a string representation of the object."""
        return (
            f"{self.__class__.__name__}"
            f"(page={self._page}, limit={self._limit})"
        )

    def __str__(self):
        """Return a human-friendly string representation of the object."""
        return "\n".join(
            (
                "Updater[Pagination] will update a sqlalchemy select.",
                f"LIMIT {self._page}",
                f"OFFSET {self._offset}",
            )
        )
