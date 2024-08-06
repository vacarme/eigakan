"""Pydantic schemas used in the authentication router."""

from pydantic import BaseModel


class Token(BaseModel):
    """Schema for Token."""

    access_token: bytes
    token_type: str = "bearer"
