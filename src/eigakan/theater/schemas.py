from datetime import datetime
from enum import StrEnum, auto

from pydantic import BaseModel

from eigakan.schemas import _Paginated


class Wheelchair(StrEnum):
    NO = auto()
    LIMITED = auto()
    DESIGNATED = auto()
    YES = auto()

class Accessibility(BaseModel):
    id: int
    strength: int
    name: str

class TheaterRead(BaseModel):
    """Serialization Schema."""

    osm_id: str
    cnc_id: int | None
    name: str | None
    org: str | None
    opening_hours: str | None
    open_air: bool | None
    drive_in: bool | None
    cinema_3d: bool | None
    nb_screens: int | None
    capacity: int | None
    voice_desc: bool | None
    website: str | None
    phone: str | None
    facebook: str | None
    wikidata: str | None
    siret: int | None
    city_insee: str | None
    city_name: str | None
    accessibility: Accessibility


class Theaters(_Paginated):
    content: list[TheaterRead]


class ProgPost(BaseModel):
    movie: str
    start_time: datetime
    end_time: datetime
