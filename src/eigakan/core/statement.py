from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Type, final

from sqlalchemy import func, inspect, select
from sqlalchemy.dialects import postgresql

from eigakan.logger import logger
from eigakan.types import M

from .exc import (
    ColumnCannotbeUsedToReadOne,
    ResourceNotFound,
)
from .updaters.commons import ScalarUpdater

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Type

    from sqlalchemy import Select
    from sqlalchemy.ext.asyncio import AsyncSession
    from sqlalchemy.sql.base import ExecutableOption

    from .updaters import Updater


class Statement(ABC):
    def __init__(self, model, *updaters: Updater | None) -> None:
        self._model = model
        self._updaters = [
            updater for updater in updaters if updater is not None
        ]

    @abstractmethod
    async def __call__(self, session: AsyncSession): ...

    @abstractmethod
    def _base_statement(self) -> Select: ...

    @property
    def statement(self) -> Select:
        """Return the final statement that will be executed."""
        statement = self._base_statement()
        for updater in self._updaters:
            statement = updater.update(statement)
        return statement

    @final
    def __str__(self) -> str:
        """Return a user-friendly representation of the statement."""
        return str(
            self.statement.compile(
                dialect=postgresql.dialect(),
                compile_kwargs={"literal_binds": True},
            )
        )

    def _log_statement(self) -> None:
        """Log the SQL emitted by the statement."""
        logger.debug("SQL emitted by %s\n%s", self.__class__.__name__, self)

    def _get_pk(self):
        """
        Model's primary key.

        Currently unsafe for multi-pk models.
        """
        columns = inspect(self._model).columns
        return next(c for c in columns if c.primary_key)


class RealAll[Model: M](Statement):
    def __init__(
        self,
        model: Type[Model],
        *updaters: Updater | None,
    ) -> None:
        super().__init__(model, *updaters)

    def _base_statement(self) -> Select[tuple[Model]]:
        """Return the base statement."""
        return select(self._model)

    async def __call__(self, session: AsyncSession) -> Sequence[Model]:
        self._log_statement()
        result = await session.scalars(self.statement)
        return result.all()


class ReadAllLines[Model: M](Statement):
    """TODO Cache system ?"""

    def __init__(self, model: Type[Model], *updaters: Updater | None) -> None:
        super().__init__(model, *updaters)

    def _base_statement(self) -> Select[tuple[int]]:
        """Return the base statement."""
        return select(func.count(self._get_pk()))

    async def __call__(self, session: AsyncSession) -> int:
        self._log_statement()
        result = await session.scalar(self.statement)
        return result or 0


class ReadOneBy[Model: M](Statement):
    def __init__(
        self,
        column: str,
        value,
        model: Type[Model],
        *updaters: Updater | None,
        strategy: ExecutableOption | None = None,
    ) -> None:
        if not self._is_unique_column(model, column):
            raise ColumnCannotbeUsedToReadOne(column, model.__name__)
        super().__init__(model, *updaters, ScalarUpdater(column, value, model))
        self._strategy = strategy
        self._rec = column, value

    def _base_statement(self) -> Select[tuple[Model]]:
        return (
            select(self._model).options(self._strategy)
            if self._strategy is not None
            else select(self._model)
        )

    async def __call__(self, session: AsyncSession) -> Model:
        self._log_statement()
        if (resource := await session.scalar(self.statement)) is None:
            raise ResourceNotFound(*self._rec)
        return resource

    @staticmethod
    def _is_unique_column(model: Type[Model], column: str) -> bool:
        """Check if column with this name is a pk or unique."""
        columns = inspect(model).columns
        return column in tuple(
            c.name for c in columns if c.unique or c.primary_key
        )
