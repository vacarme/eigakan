# ruff: noqa: E402, I001
import pytest
from sqlalchemy.schema import CreateSchema, DropSchema
from starlette.config import environ
from starlette.testclient import TestClient

environ["DB_PORT"] = "5433"

from eigakan.database.core import Base
from eigakan.database.enums import CORE_SCHEMA
from eigakan.main import app
from eigakan.database.core import engine
from .factories import AccessibilityFactory
from .database import AsyncScopedSession


@pytest.fixture(scope="function")
async def db():
    async with engine.begin() as conn:
        await conn.execute(CreateSchema(CORE_SCHEMA, if_not_exists=True))
        await conn.run_sync(Base.metadata.create_all)
        AsyncScopedSession.configure(bind=engine)
    yield
    async with engine.begin() as conn:
        await conn.execute(
            DropSchema(CORE_SCHEMA, if_exists=True, cascade=True)
        )


@pytest.fixture()
async def session(db):
    """
    Creates a new database session with (with working transaction)
    for test duration.
    """
    session = AsyncScopedSession()
    await session.begin_nested()
    yield session
    await session.rollback()
    await AsyncScopedSession.remove()


@pytest.fixture()
def client():
    """
    Make a 'client' fixture available to test cases.
    """
    # Our fixture is created within a context manager. This ensures that
    # application lifespan runs for every test case.
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
async def accessibility(session):
    return await AccessibilityFactory.create()


@pytest.fixture()
async def accessibilities(session):
    return (
        await AccessibilityFactory.create(),
        await AccessibilityFactory.create(),
    )
