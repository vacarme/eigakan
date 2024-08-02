from pathlib import Path
from time import time
from typing import TYPE_CHECKING

from geopandas import read_file
from pandas import read_csv
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import CreateSchema, DropSchema

from eigakan.env import DATABASE

from .core import Base
from .enums import CORE_SCHEMA

if TYPE_CHECKING:
    from geopandas import GeoDataFrame

_DATA_FILE = Path(__file__).resolve().parent.parent.parent.parent / "data"


def get_core_tables():
    """Fetches tables that belong to the 'dispatch_core' schema."""
    core_tables = []
    for _, table in Base.metadata.tables.items():
        if table.schema == CORE_SCHEMA:
            core_tables.append(table)
    return core_tables


def seed():
    start = time()
    cine: GeoDataFrame = read_file(_DATA_FILE / "data-clean.geojson")
    owner = read_csv(_DATA_FILE / "owner.csv")
    access = read_csv(_DATA_FILE / "accessibility.csv")

    engine = create_engine(
        DATABASE.URL,
        poolclass=NullPool,
    )

    with engine.begin() as conn:
        conn.execute(CreateSchema(CORE_SCHEMA, if_not_exists=True))

        Base.metadata.create_all(conn, tables=get_core_tables())
        access.to_sql(
            "accessibility",
            conn,
            schema=CORE_SCHEMA,
            if_exists="append",
            index=False,
        )
        cine.to_postgis(
            "theater", conn, schema=CORE_SCHEMA, if_exists="append"
        )
        owner.to_sql(
            "owner",
            conn,
            schema=CORE_SCHEMA,
            if_exists="append",
            index=False,
            dtype={"id": UUID},
        )

        elapsed_time = int(1000 * (time() - start))
        print(
            "Tables created and seeded to",
            f"{DATABASE.NAME} in {elapsed_time} ms:",
        )

        for table in get_core_tables():
            count = conn.execute(  # type: ignore
                text(f"SELECT count(*) FROM {CORE_SCHEMA}.{table.name}")  # noqa: S608
            ).fetchone()[0]
            print(f"・{table.name}: {count} row{"s" if count > 1 else ""}")


def drop():
    start = time()
    engine = create_engine(
        DATABASE.URL,
        poolclass=NullPool,
    )
    with engine.begin() as conn:
        conn.execute(DropSchema(CORE_SCHEMA, cascade=True, if_exists=True))
    elapsed_time = int(1000 * (time() - start))
    print(f"Tables dropped from {CORE_SCHEMA} in {elapsed_time} ms:", end="")
    print(" ", *Base.metadata.tables, sep="\n ")
