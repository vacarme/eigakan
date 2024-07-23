import uuid
from datetime import datetime
from typing import ClassVar

from sqlalchemy import BigInteger, DateTime, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from eigakan.database.enums import CORE_SCHEMA


class CoreMixin:
    """define a series of common elements that may be applied to mapped
    classes using this class as a mixin class."""

    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    __table_args__: ClassVar[dict[str, str]] = {"schema": CORE_SCHEMA}

class SequentialIdMixin(CoreMixin):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

class RandomIdMixin(CoreMixin):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        sort_order=-999,
    )


class TimeStampMixin:
    """Timestamping mixin"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now
    )

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.now()

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._updated_at)
