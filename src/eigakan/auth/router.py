from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from eigakan.core.statement import ReadOneBy
from eigakan.database.core import Session
from eigakan.logger import logger

from . import password
from .models import Owner
from .schemas import Token
from .token import create_jwt_token

router = APIRouter()


@router.post(
    "/token",
    response_model=Token,
)
async def login(
    session: Session,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> dict[str, str | bytes]:
    """
    Generate the bearer token.

    Route receiving user credential (must be a form) and
    creating the bearer token upon successful credential verification.

    Parameters
    ----------
    form_data : fastapi.OAuth2PasswordRequestForm
        payload submited from an html form,
        containing at least `username`and `password` field.
    session : AsyncSession
        SQLAlchemy session tied to the database.

    Returns
    -------
    dict[str, str | bytes]
        dict with token type and the JWT (bytes).

    """
    owner = await ReadOneBy("email", form_data.username, Owner)(session)
    password.verify(owner, form_data.password)
    if new_hash := password.rehash_if_needed(owner, form_data.password):
        owner.password = bytes(new_hash, "utf-8")
        await session.commit()

    access_token = create_jwt_token(sub=str(owner.id))
    logger.exception("fuck")
    return {"access_token": access_token, "token_type": "bearer"}
