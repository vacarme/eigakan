"""Sqlalchemy mapped classes for the core schema."""

from __future__ import annotations

from geoalchemy2 import Geometry
from geoalchemy2.elements import WKBElement
from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    Text,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, relationship

from eigakan.database.core import Base
from eigakan.database.enums import CORE_SCHEMA
from eigakan.models import CoreMixin, RandomIdMixin


class Accessibility(Base, CoreMixin):
    """Mapped class representing an accessibility."""

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    strength: Mapped[int] = mapped_column(SmallInteger)
    name: Mapped[str] = mapped_column(Text)


class Theater(Base, AsyncAttrs, RandomIdMixin):
    """Mapped class representing a theater."""

    osm_id: Mapped[str] = mapped_column(Text, unique=True, index=False)
    cnc_id: Mapped[int] = mapped_column("ref_cnc", Integer, nullable=True)
    name: Mapped[str] = mapped_column(Text, nullable=True)
    org: Mapped[str] = mapped_column("marque", Text, nullable=True)
    accessibility_id: Mapped[int] = mapped_column(
        SmallInteger, ForeignKey(f"{CORE_SCHEMA}.accessibility.id")
    )
    opening_hours: Mapped[str] = mapped_column(Text, nullable=True)
    open_air: Mapped[bool] = mapped_column(Boolean, nullable=True)
    drive_in: Mapped[bool] = mapped_column(Boolean, nullable=True)
    cinema_3d: Mapped[bool] = mapped_column("cinema3d", Boolean, nullable=True)
    nb_screens: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    capacity: Mapped[int] = mapped_column(SmallInteger, nullable=True)
    voice_desc: Mapped[str] = mapped_column(Boolean, nullable=True)
    website: Mapped[str] = mapped_column(Text, nullable=True)
    phone: Mapped[str] = mapped_column(Text, nullable=True)
    facebook: Mapped[str] = mapped_column(Text, nullable=True)
    wikidata: Mapped[str] = mapped_column(Text, nullable=True)
    siret: Mapped[int] = mapped_column(BigInteger, nullable=True)
    city_insee: Mapped[str] = mapped_column("com_insee", Text)
    city_name: Mapped[str] = mapped_column("com_nom", Text, nullable=True)
    geometry: Mapped[WKBElement] = mapped_column(
        Geometry(srid=4326, spatial_index=False), index=False
    )
    accessibility: Mapped[Accessibility] = relationship(lazy="selectin")


Index("idx_wheel_screen", Theater.accessibility_id, Theater.nb_screens)


if __name__ == "__main__":

    import asyncio

    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    from eigakan.database.core import AsyncSessionFactory

    async def tr():
        async with AsyncSessionFactory() as sess:
            a = await sess.scalar(
            select(Theater).options(selectinload(Theater.accessibility))
        )
        return a
    b = asyncio.run(tr())
    # print(b.accessibility.name)

