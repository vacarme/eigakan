from __future__ import annotations

from typing import Protocol

from sqlalchemy.sql.expression import Select


class Updater(Protocol):
    def update(self, statement: Select) -> Select: ...
