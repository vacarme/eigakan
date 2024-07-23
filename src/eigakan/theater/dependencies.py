from typing import Annotated

from fastapi import Depends, Query
from geoalchemy2.elements import WKTElement
from pydantic.json_schema import SkipJsonSchema

from eigakan.core.updaters.commons import (
    ScalarUpdater,
    StartsWithUpdater,
)

from .models import Theater
from .schemas import Wheelchair as WheelchairEnum
from .updaters import ClosestUpdater

LongParameter = Annotated[
    float,
    Query(
        description="position longitude *WGS84*",
        examples=[2.2646354, 4.2838956],
        openapi_examples={
            "Paris": {
                "value": 2.2646354,
            },
            "Saint-Etienne": {
                "value": 4.2838956,
            },
        },
        ge=0,
        le=90,
    ),
]
LatParameter = Annotated[
    float,
    Query(
        description="position latitude *WGS84*",
        examples=[48.8589384, 45.4240741],
        openapi_examples={
            "Paris": {
                "value": 48.8589384,
            },
            "Saint-Etienne": {
                "value": 45.4240741,
            },
        },
        ge=0,
        le=90,
    ),
]


async def _parse_coordinates(longitude: LongParameter, latitude: LatParameter):
    _ = f"POINT({longitude} {latitude})"
    return ClosestUpdater(Theater, WKTElement(_, srid=4326))


Position = Annotated[ClosestUpdater, Depends(_parse_coordinates)]


def _parse_accessibility(
    accessibility: Annotated[
        WheelchairEnum | SkipJsonSchema[None],
        Query(alias="wheelchairFriendly"),
    ] = None,
):
    return (
        ScalarUpdater(Theater, "accessibility.name", accessibility.value)
        if accessibility
        else None
    )


Accessibility = Annotated[ScalarUpdater | None, Depends(_parse_accessibility)]


def _parse_screen(
    nb_screens: Annotated[
        int | SkipJsonSchema[None],
        Query(
            alias="numberOfRooms",
            examples=[3, 7],
            gt=0,
        ),
    ] = None,
):
    return (
        ScalarUpdater(Theater, "nb_screens", nb_screens)
        if nb_screens
        else None
    )


ScreensNumber = Annotated[ScalarUpdater | None, Depends(_parse_screen)]


def _parse_zip(
    zip: Annotated[
        str | SkipJsonSchema[None],
        Query(
            alias="departmentCode",
            examples=["94", "2A"],
            min_length=2,
            max_length=2,
            # pattern=r"\b([013-8]\d?|2[aAbB1-9]?|9[0-59]?|97[1-6])\b/gm",
        ),
    ] = None,
):
    return StartsWithUpdater(Theater, "city_insee", zip) if zip else None


DepartmentCode = Annotated[StartsWithUpdater | None, Depends(_parse_zip)]
