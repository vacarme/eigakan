"""Password hashing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from argon2 import PasswordHasher

from .exc import InvalidPassword

if TYPE_CHECKING:
    from .models import Owner


ph = PasswordHasher()


def verify(user: Owner, password: str) -> None:
    """
    Verify the user's password.

    Received password is checked against the hash stored in the database.

    Parameters
    ----------
    user : User
        user requesting logging.
    password : str
        password of the user requesting logging.

    Raises
    ------
    InvalidPassword
        provided password does not match the hash stored.

    """
    try:
        ph.verify(hash=user.password, password=password)
    except Exception as e:
        raise InvalidPassword() from e


def rehash_if_needed(user: Owner, password: str) -> str | None:
    """Rehash the password if needed."""
    return (
        ph.hash(password)
        if ph.check_needs_rehash(user.password.decode())
        else None
    )
