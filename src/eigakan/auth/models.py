from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, LargeBinary, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eigakan.database.core import Base
from eigakan.models import SequentialIdMixin, TimeStampMixin

if TYPE_CHECKING:
    from eigakan.theater.models import Theater


class Owner(Base, AsyncAttrs, SequentialIdMixin, TimeStampMixin):
    """Mapped class representing an owner."""

    siret: Mapped[int] = mapped_column(BigInteger, unique=True)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    disabled: Mapped[bool] = mapped_column(Boolean)
    theaters: Mapped[list[Theater]] = relationship(
        primaryjoin="Owner.siret == foreign(Theater.siret)",
        uselist=True,
    )
