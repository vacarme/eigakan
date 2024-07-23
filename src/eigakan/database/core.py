"""
Database dependency.

SQLAlchemy engine configuration:
+ `pool_size` = 10 (default),
+ `maxoverflow` = 10 (default),
+ `pool_recycle` = -1 (default),
+ `pool_pre_ping` = True

pool pre ping:
A strategy of pessimistic disconnection handling.
Implemented to handle db restart fucking up idle connections.
--> https://docs.sqlalchemy.org/en/20/core/pooling.html#disconnect-handling-pessimistic

"""

from __future__ import annotations

from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from eigakan.env import DATABASE
from eigakan.logger import logger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

engine = create_async_engine(
    url=DATABASE.URL,
    pool_pre_ping=True,
    pool_size=10,
)
AsyncSessionFactory = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all relations fo the 'api' schema."""

    ...

    def dict(self):
        """Returns a dict representation of a model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


async def db() -> AsyncGenerator[AsyncSession, None]:
    """Inject db connection into fastapi endpoint."""
    async with AsyncSessionFactory() as session:
        try:
            yield session
        except OperationalError:
            logger.exception("Unable to connect to Database.")
            raise HTTPException(
                HTTPStatus.SERVICE_UNAVAILABLE,
                "Unable to reach the underlying database.",
            ) from None
        finally:
            await session.close()


Session = Annotated[AsyncSession, Depends(db)]
