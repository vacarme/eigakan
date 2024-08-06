"""Environment parser."""

# ruff: noqa: RUF009
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy.engine.url import URL as DB_URL
from starlette.config import Config
from starlette.datastructures import Secret

try:
    config = Config(".env")
except FileNotFoundError:
    config = Config()


@dataclass(repr=False, eq=False, frozen=True)
class DATABASE:
    """Database configuration."""

    USER: str = config("DB_USER", cast=str)
    PASSWORD: Secret = config("DB_PASSWORD", cast=Secret)
    HOST: str = config("DB_HOST", cast=str)
    PORT: int = config("DB_PORT", cast=int)
    NAME: str = config("DB_NAME", cast=str)
    DRIVER: str = "postgresql+psycopg"
    URL = DB_URL.create(
        drivername=DRIVER,
        username=USER,
        password=str(PASSWORD),
        host=HOST,
        port=PORT,
        database=NAME,
    )


@dataclass(repr=False, eq=False, frozen=True)
class APP:
    """Application level configuration."""

    LOG_LEVEL: str = config("LOG_LEVEL", cast=str, default="INFO")
    STATIC_DIR: Path = config("STATIC_DIR", cast=Path)


@dataclass(repr=False, eq=False, frozen=True)
class JWT:
    """JWT configuration."""

    SECRET: Secret = config("JWT_SECRET", cast=Secret)
    HOURS_TO_EXPIRE: int = config("JWT_HOURS_TO_EXPIRE", cast=int, default=24)
