from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response

from eigakan.auth.dependencies import CurrentUser
from eigakan.core.cud import CUD
from eigakan.core.statement import ReadAllLines, ReadOneBy, RealAll
from eigakan.database.core import Session
from eigakan.dependencies import Pagination, ResourceInjecter
from eigakan.logger import logger

from . import dependencies as dps
from . import schemas as sch
from .models import Theater

router = APIRouter()
Resource = Annotated[ReadOneBy[Theater], Depends(ResourceInjecter(Theater))]
cud = CUD(Theater)


@router.get("/{id}", response_model=sch.TheaterRead, status_code=HTTPStatus.OK)
async def get_one_by(resource: Resource, session: Session) -> Theater:
    return await resource(session)


@router.get("", response_model=sch.Theaters, status_code=HTTPStatus.OK)
async def read_resource(
    position: dps.Position,
    accessibility: dps.Accessibility,
    screens_number: dps.ScreensNumber,
    department: dps.DepartmentCode,
    pagination: Pagination,
    session: Session,
):
    """Read all nearest theaters."""
    stmt = RealAll(
        Theater,
        accessibility,
        screens_number,
        department,
        position,
        pagination,
    )
    liner = ReadAllLines(Theater, accessibility, screens_number, department)
    return {
        "content": await stmt(session),
        "pagination": {
            "current": pagination.page,
            "total": pagination.get_total_number_of_pages(
                await liner(session)
            ),
        },
    }


@router.post("", response_model=None, status_code=HTTPStatus.CREATED)
async def create_resource(
    body: sch.TheaterCreate,
    session: Session,
    response: Response,
    user: CurrentUser,
) -> None:
    theater = body.model_dump(exclude={"latitude", "longitude"})
    theater["siret"] = user.siret
    _ = await cud.create(theater, session)
    response.headers["Location"] = str(_.id)


@router.patch("/{id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
async def update_resource(
    body: sch.TheaterUpdate,
    resource: Resource,
    session: Session,
    owner: CurrentUser,
):
    persistent_resource = await resource(session)
    if persistent_resource not in await owner.awaitable_attrs.theaters:
        logger.exception("User tried to update a resource he does not own.")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    await cud.update(
        body.model_dump(exclude_unset=True, exclude_none=True),
        persistent_resource,
        session,
    )


@router.delete("/{id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
async def delete_resource_by_id(
    resource: Resource,
    session: Session,
    owner: CurrentUser,
) -> None:
    persistent_resource = await resource(session)
    if persistent_resource not in await owner.awaitable_attrs.theaters:
        logger.exception("User tried to update a resource he does not own.")
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
    await cud.delete(persistent_resource, session)
