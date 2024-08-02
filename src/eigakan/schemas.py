"""API level schemas."""

from pydantic import BaseModel, Field


class Page(BaseModel):
    """Page schema."""

    current: int = Field(
        ...,
        examples=[1],
        ge=1,
        description="current page's number.",
    )
    total: int = Field(
        ..., examples=[4], description="total number of pages available."
    )


class _Paginated(BaseModel):
    """Paginated base pydantic model."""

    pagination: Page
