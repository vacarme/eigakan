from http import HTTPStatus

from fastapi import APIRouter

from eigakan.core.statement import ReadAllLines, RealAll
from eigakan.database.core import Session
from eigakan.dependencies import Pagination

from . import dependencies as dps
from . import schemas as sch
from .models import Theater

router = APIRouter()


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
