"""
Vector format conversion, with GeoJSON as the primary browser-facing
output format (section 20).

Conversion here is purely a format/CRS operation; it does not perform
geometry validation, repair, or clipping. See ``gis.processing`` for that.
"""

import json
from pathlib import Path
from typing import Union

import geopandas as gpd

from gis.config import WGS84, ensure_dir
from gis.conversion.reproject import reproject_vector
from gis.exceptions import MissingCRSError


def convert_to_geojson(
    gdf: gpd.GeoDataFrame,
    out_path: Union[str, Path],
    layer_name: str = "layer",
    target_crs: str = WGS84,
) -> Path:
    """Export a GeoDataFrame to GeoJSON, preserving its attributes."""
    if gdf.crs is None:
        raise MissingCRSError(layer_name)

    gdf_out = reproject_vector(gdf, target_crs, layer_name=layer_name)
    out_path = Path(out_path)
    ensure_dir(out_path.parent)
    gdf_out.to_file(out_path, driver="GeoJSON")
    return out_path


def vector_to_geojson_dict(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "layer",
    target_crs: str = WGS84,
) -> dict:
    """Convert a GeoDataFrame to an in-memory GeoJSON FeatureCollection."""
    if gdf.crs is None:
        raise MissingCRSError(layer_name)

    gdf_out = reproject_vector(gdf, target_crs, layer_name=layer_name)
    return json.loads(gdf_out.to_json())
