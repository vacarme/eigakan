"""Read, Update and Delete operations for a given sqlalchemy model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from psycopg.errors import ForeignKeyViolation, UniqueViolation
from sqlalchemy.exc import IntegrityError

from .exc import (
    DuplicatedResource,
    ResourceNotFound,
)

if TYPE_CHECKING:
    from collections.abc import Mapping
    from typing import Any, Type

    from sqlalchemy.ext.asyncio import AsyncSession

    from eigakan.types import M


class CUD[Resource: M]:
    """Basic CUD operations for a given sqlalchemy model."""

    def __init__(self, model: Type[Resource]) -> None:
        """
        Initialize a CUD object for a given sqlalchemy model.

        Parameters
        ----------
        model : Type[Resource]
            SQLAlchemy model to use for CRUD operations.

        """
        self._model = model

    async def create(
        self,
        resource: Mapping[str, Any],
        session: AsyncSession,
    ) -> Resource:
        """
        Create a new resource.

        Parameters
        ----------
        resource : Mapping[str, Any]
            flat representation of the resource to create.
        session : AsyncSession
            SQLAlchemy session.

        Returns
        -------
        Resource
            the created resource.

        Raises
        ------
        DuplicatedResource
            if the resource already exists.
        ResourceNotFound
            if the resource contains a foreign key that does not exist.

        Examples
        --------
        Create a new theater:
        >>> from eigakan.theater.models import Theater
        >>> from eigakan.core.cud import CUD
        >>> from eigakan.database.core import AsyncSessionFactory
        >>> crud = CUD(Theater)
        >>> async with Session() as session:
        ...     await cud.create({"name": "Cinecool", ...}, session)
        Theater(id=1, name="Cinecool", ...)

        """
        transient_resource = self._model(**resource)
        session.add(transient_resource)
        try:
            await session.commit()
        except IntegrityError as exc:
            raise _handle_integrity_error(exc) from exc
        return transient_resource

    async def update(
        self,
        body: Mapping,
        resource: Resource,
        session: AsyncSession,
    ):
        """
        Update a resource.

        Parameters
        ----------
        body : Mapping
            mapping ot attributes to update.
        resource : Resource
            the persistent resource to be updated.
        session : AsyncSession
            SQLAlchemy session.


        Raises
        ------
        DuplicatedResource
            if one of the new values violates a unicity constraint.
        ResourceNotFound
            if one foreign key of the resource is updated to a value that does
            not exist.

        Examples
        --------
        Update a theater:
        >>> from eigakan.theater.models import Theater
        >>> from eigakan.core.cud import CUD
        >>> from eigakan.database.core import AsyncSessionFactory
        >>> crud = CUD(Theater)
        >>> async with AsyncSessionFactory() as session:
        ...     await cud.update(
        ...         {"name": "Cinecool 2.0"},
        ...         theater,
        ...         session,
        ...     )
        Theater(id=1, name="Cinecool 2.0", ...)

        """
        for k, v in body.items():
            setattr(resource, k, v)
        try:
            await session.commit()
        except IntegrityError as exc:
            raise _handle_integrity_error(exc) from exc

    async def delete(
        self,
        resource: Resource,
        session: AsyncSession,
    ):
        """
        Delete a resource.

        Parameters
        ----------
        resource : Resource
            the persistent resource to be deleted.
        session : AsyncSession
            SQLAlchemy session.

        Examples
        --------
        >>> from eigakan.theater.models import Theater
        >>> from eigakan.core.cud import CUD
        >>> from eigakan.database.core import AsyncSessionFactory
        >>> crud = CUD(Theater)
        >>> async with AsyncSessionFactory() as session:
        ...     await cud.delete(
        ...         theater,
        ...         session,
        ...     )
        """
        await session.delete(resource)
        await session.commit()


def _handle_integrity_error(exc: IntegrityError) -> Exception:
    """
    Dispatch the proper exception based on the received exception.

    Parameter
    ---------
    exc: Exception
        exception raised by sqlalchemy.

    Return
    ------
    Exception
        + `ResourceNotFound` if psycopg detected a foreign key violation,
        + `DuplicatedResource` if psycopg detected a unicity violation,
        + the input otherwise.

    """
    if isinstance(exc.orig, ForeignKeyViolation):
        return ResourceNotFound()
    elif isinstance(exc.orig, UniqueViolation):
        return DuplicatedResource()
    else:
        return exc
