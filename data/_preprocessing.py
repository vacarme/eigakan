"""
Included for the record only.

Here are the pre-processing steps applied to the original data.geojson.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from uuid import uuid4

from geopandas import read_file

if TYPE_CHECKING:
    from geopandas import GeoDataFrame

STEPS = []

_DATA_FILE = Path(__file__).resolve().parent


def step(func):
    STEPS.append(func)
    return func


@step
def convert_to_boolean_inplace(gdf: GeoDataFrame) -> None:
    boolean_mapper = {"yes": True, "no": False}
    gdf["open_air"] = gdf.open_air.map(boolean_mapper)
    gdf["cinema3d"] = gdf.cinema3d.map(boolean_mapper)
    gdf["drive_in"] = gdf.drive_in.map(boolean_mapper)


@step
def create_id_column(gdf: GeoDataFrame) -> None:
    gdf["id"] = gdf.index.map(lambda _: uuid4())
    gdf.loc[gdf.siret == "50763357600016", ["id"]] = (
        "20e4a4c1-74a9-4fbd-a088-4220a5c709f8"
    )


@step
def ref_cnc(gdf: GeoDataFrame):
    gdf.drop(
        gdf.loc[gdf.ref_cnc.str.contains("-|;") & gdf.ref_cnc.notna()].index,
        inplace=True,
    )
    gdf["ref_cnc"] = gdf["ref_cnc"].replace("no", None)


@step
def siret(gdf: GeoDataFrame):
    gdf.drop(
        gdf.loc[gdf.siret.str.contains(";") & gdf.siret.notna()].index,
        inplace=True,
    )
    gdf["siret"] = gdf.siret.str.replace(" ", "")
    gdf.loc[gdf.siret == "334962289RCSCHAMBERY", ["siret"]] = "334962289"


@step
def acoustic(gdf: GeoDataFrame):
    gdf["voice_desc"] = gdf.acoustic.map(
        {"voice_description": True, None: False}
    )


@step
def wheelchair(gdf: GeoDataFrame):
    gdf["accessibility_id"] = gdf.wheelchair.map(
        {None: 0, "no": 1, "designated": 3, "limited": 2, "yes": 4}
    )


@step
def lowerized_text(gdf: GeoDataFrame):
    for col in ("name", "marque", "com_nom", "opening_hours"):
        gdf[col] = gdf[col].str.lower()


def preprocess(gdf: GeoDataFrame) -> None:
    for step in STEPS:
        step(gdf)


if __name__ == "__main__":
    gdf: GeoDataFrame = read_file(_DATA_FILE / "data.geojson")
    preprocess(gdf)
    gdf.drop(columns=["acoustic", "wheelchair"]).to_file(  # type: ignore
        _DATA_FILE / "data-clean.geojson", driver="GeoJSON"
    )
