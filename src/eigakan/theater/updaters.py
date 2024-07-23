from __future__ import annotations

from typing import TYPE_CHECKING, Type

from sqlalchemy import func

from eigakan.core.updaters import Updater

from .models import Theater

type T = Theater

if TYPE_CHECKING:
    from sqlalchemy.sql.expression import Select


class ClosestUpdater[Model: T](Updater):
    def __init__(self, model: Type[Model], location) -> None:
        self._location = location
        self._model = model

    def update(self, statement: Select) -> Select:
        return statement.order_by(
            func.ST_Distance(self._model.geometry, self._location).asc()
        )


# class UserOwnership(Updater[T]):
#     def __init__(self, owner) -> None:
#         self.owner = owner
#         self(Theater)

#     def update(self, statement: Select) -> Select:
#         return statement.where(self._model.siret == Owner.siret)
