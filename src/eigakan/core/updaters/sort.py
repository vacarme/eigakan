"""Sorter Updater."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eigakan.types import M

from .updater import Updater

if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Self, Type

    from sqlalchemy.sql.elements import UnaryExpression
    from sqlalchemy.sql.expression import Select


class Sorter[Model: M](Updater):
    """Responsible for generating order_by clauses for SQLAlchemy statement."""

    def __init__(self, asc: Iterable[str] = (), desc: Iterable[str] = ()):
        """
        Initialize the sorter.

        Parameters
        ----------
        asc : Iterable[str], optional
            A list of columns to sort by in ascending order.
        desc : Iterable[str], optional
            A list of columns to sort by in descending order.

        """
        self._asc = asc
        self._desc = desc

    def __call__(self, model: Type[Model]) -> Self:
        """Register the model."""
        return super().__call__(model)

    @property
    def ascending(self) -> tuple[UnaryExpression, ...]:
        """Return a tuple of `model.column.asc()` expressions."""
        self._raise_if_no_model_registered(method_name="@ascending")
        return tuple(getattr(self._model, col).asc() for col in self._asc)

    @property
    def descending(self) -> tuple[UnaryExpression, ...]:
        """Return tuple of `model.column.desc()` expressions."""
        self._raise_if_no_model_registered(method_name="@descending")
        return tuple(getattr(self._model, col).desc() for col in self._desc)

    def update(self, statement: Select) -> Select:
        """Update the statement with the proper `order_by` clauses."""
        if asc := self.ascending:
            statement = statement.order_by(*asc)
        if desc := self.descending:
            statement = statement.order_by(*desc)
        return statement

    def __repr__(self) -> str:
        """Return a string representation of the object."""
        return (
            f"{self.__class__.__name__}"
            f"(asc={self._asc!r}, desc={self._desc!r})"
        )

    def __str__(self) -> str:
        """Return a human-friendly string representation of the object."""
        return "\n".join(
            (
                "Updater[Sorter] will update a sqlalchemy select.",
                f"ORDER BY {','.join(self._asc)} ASC",
                f"ORDER BY {','.join(self._desc)} DESC",
            )
        )
