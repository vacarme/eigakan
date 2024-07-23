from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eigakan.database.core import Base
from eigakan.models import RandomIdMixin

if TYPE_CHECKING:
    from eigakan.theater.models import Theater

class Owner(Base, AsyncAttrs, RandomIdMixin):
    """Mapped class representing an owner."""

    siret: Mapped[str] = mapped_column(Text)
    theaters: Mapped[list[Theater]] = relationship(
        primaryjoin="Owner.siret == foreign(Theater.siret)",
        uselist=True,
    )
