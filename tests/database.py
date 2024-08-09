from asyncio import current_task

from sqlalchemy.ext.asyncio import (
    async_scoped_session,
    async_sessionmaker,
)

AsyncScopedSession = async_scoped_session(
    async_sessionmaker(expire_on_commit=False, autoflush=False),
    scopefunc=current_task,
)
