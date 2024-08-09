import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory

from eigakan.theater.models import Accessibility

from .database import AsyncScopedSession


class BaseFactory(AsyncSQLAlchemyFactory):
    """Base Factory."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = AsyncScopedSession
        sqlalchemy_session_persistence = None


class AccessibilityFactory(BaseFactory):
    class Meta:
        model = Accessibility

    id = factory.Sequence(lambda n: n)
    strength = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: "Accessibility %d" % n)
