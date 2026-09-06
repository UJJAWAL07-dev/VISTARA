"""
Vector data loading and inspection.

Supports GeoJSON, ESRI Shapefile, and GeoPackage (section 9).
Never assumes CRS or geometry type: always inspect first (section 40).
"""

from pathlib import Path
from typing import Union

import geopandas as gpd

from gis.config.formats import SUPPORTED_VECTOR_FORMATS, is_vector_format
from gis.exceptions import (
    FileNotFoundInGISError,
    UnsupportedFormatError,
    VectorLoadError,
)


def load_vector(path: Union[str, Path]) -> gpd.GeoDataFrame:
    """
    Load a vector dataset into a GeoDataFrame.

    This raw load step does not reproject, validate, or clean geometry.
    Use ``gis.processing`` for CRS handling and geometry preparation.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundInGISError(path)

    if not is_vector_format(path):
        raise UnsupportedFormatError(path, list(SUPPORTED_VECTOR_FORMATS))

    try:
        return gpd.read_file(path)
    except Exception as error:
        raise VectorLoadError(path, original_error=error) from error


def inspect_vector(gdf: gpd.GeoDataFrame) -> dict:
    """Return basic metadata about a loaded vector layer without mutation."""
    geom_types = sorted(gdf.geom_type.dropna().unique().tolist())

    return {
        "feature_count": len(gdf),
        "crs": str(gdf.crs) if gdf.crs else None,
        "geometry_types": geom_types,
        "bounds": tuple(gdf.total_bounds) if len(gdf) > 0 else None,
        "columns": [column for column in gdf.columns if column != "geometry"],
    }
