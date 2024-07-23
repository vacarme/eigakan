from __future__ import annotations

from typing import TYPE_CHECKING, Type

from eigakan.types import M

from .updater import Updater

if TYPE_CHECKING:
    from sqlalchemy.sql.expression import Select


class _JoinSupport[Model: M]:
    def __init__(
        self,
        model: Type[Model],
        key: str,
        value: str | float | bool,
    ) -> None:
        self._key = key
        self._value = value
        self._model = model

    @property
    def model(self):
        if self._is_joined():
            relationship_name = self._key.split(".", 1)[0]
            return getattr(
                self._model, relationship_name
            ).property.mapper.class_
        return self._model

    @property
    def key(self):
        if self._is_joined():
            return self._key.split(".", 1)[1]
        return self._key

    def _is_joined(self) -> bool:
        return "." in self._key

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._key!r}, {self._value!r})"


class ScalarUpdater[Model: M](Updater, _JoinSupport[Model]):
    def update(self, statement: Select) -> Select:
        if self._is_joined():
            statement = statement.join(self.model)
        return statement.where(getattr(self.model, self.key) == self._value)

    def __str__(self) -> str:
        return (
            f"・{self.__class__.__name__} ⇢ "
            f"WHERE {self._model.__name__}.{self._key} = {self._value}"
        )


class StartsWithUpdater[Model: M](Updater, _JoinSupport[Model]):
    def update(self, statement: Select) -> Select:
        return statement.where(
            getattr(self._model, self._key).startswith(self._value)
        )

    def __str__(self) -> str:
        return (
            f"・{self.__class__.__name__} ⇢ "
            f"WHERE {self._model.__name__}.{self._key}"
            f" LIKE '{self._value}' || '%%')"
        )
