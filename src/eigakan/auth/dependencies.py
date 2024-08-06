from http import HTTPStatus
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from eigakan.core.statement import ReadOneBy
from eigakan.database.core import Session
from eigakan.logger import logger

from .models import Owner
from .token import decode_jwt_token

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


async def current_user(
    session: Session, token: Annotated[str, Depends(_oauth2_scheme)]
) -> Owner:
    """
    Inject the current user.

    Try to fetch a user from the database matching
    the id found in the bearer token.
    If the retrieval failed for any reasons
    will raise immediatly.

    Parameters
    ----------
    session : AsyncSession
        SQLAlchemy session tied to the database.
    token : str, optional
        jwt token injected by the `fastapi.OAuth2PasswordBearer`

    Returns
    -------
    User
        user matching the id found in the token.

    Designed to be used as a fastapi dependency.

    """
    try:
        id = int(decode_jwt_token(token)["sub"])
        user = await ReadOneBy("id", id, Owner)(session)
    except Exception:
        logger.exception("Authentication Failed.")
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
        ) from None
    return user


CurrentUser = Annotated[Owner, Depends(current_user)]
