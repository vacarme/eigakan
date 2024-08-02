from enum import StrEnum, auto

from geoalchemy2.elements import WKTElement
from pydantic import BaseModel, ConfigDict, Field, computed_field

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
    city_insee: str
    city_name: str | None
    accessibility: Accessibility


class TheaterCreate(BaseModel):
    """Serialization Schema."""

    osm_id: str
    cnc_id: int
    name: str
    org: str = Field(..., examples=["Gaumont"])
    opening_hours: str
    open_air: bool
    drive_in: bool
    cinema_3d: bool
    nb_screens: int
    capacity: int
    voice_desc: bool
    website: str
    phone: str
    facebook: str | None
    wikidata: str | None
    siret: int
    accessibility_id: int
    city_insee: str
    city_name: str | None
    latitude: int = Field(..., ge=0, le=90)
    longitude: int = Field(..., ge=0, le=90)

    @computed_field
    @property
    def geometry(self) -> WKTElement | None:
        return (
            WKTElement(f"POINT({self.longitude} {self.latitude})", srid=4326)
            if self.latitude and self.latitude
            else None
        )

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TheaterUpdate(TheaterCreate):
    osm_id: str | None = None
    cnc_id: int | None = None
    name: str | None = None
    org: str = Field(None, examples=["Gaumont"])
    opening_hours: str | None = None
    open_air: bool | None = None
    drive_in: bool | None = None
    cinema_3d: bool | None = None
    nb_screens: int | None = None
    capacity: int | None = None
    voice_desc: bool | None = None
    website: str | None = None
    phone: str | None = None
    facebook: str | None = None
    wikidata: str | None = None
    siret: int | None = None
    accessibility_id: int | None = None
    city_insee: str | None = None
    city_name: str | None = None
    latitude: int | None = Field(None, ge=0, le=90)
    longitude: int | None = Field(None, ge=0, le=90)


class Theaters(_Paginated):
    content: list[TheaterRead]
