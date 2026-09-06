"""
Supported file format registry.

Keep this list intentionally small (section 6/41) — only what the
VISTARA prototype actually needs to demonstrate the workflow.
"""

from pathlib import Path
from typing import Union

SUPPORTED_VECTOR_FORMATS = {
    ".geojson": "GeoJSON",
    ".json": "GeoJSON",
    ".shp": "ESRI Shapefile",
    ".gpkg": "GPKG",
}

SUPPORTED_RASTER_FORMATS = {
    ".tif": "GTiff",
    ".tiff": "GTiff",
    ".jp2": "JP2OpenJPEG",
    ".img": "HFA",
}


def _suffix(path: Union[str, Path]) -> str:
    return Path(path).suffix.lower()


def is_vector_format(path: Union[str, Path]) -> bool:
    return _suffix(path) in SUPPORTED_VECTOR_FORMATS


def is_raster_format(path: Union[str, Path]) -> bool:
    return _suffix(path) in SUPPORTED_RASTER_FORMATS


def detect_format(path: Union[str, Path]) -> str:
    """
    Returns 'vector', 'raster', or raises UnsupportedFormatError.
    Deferred import to avoid a circular import with gis.exceptions.
    """
    from gis.exceptions import UnsupportedFormatError

    if is_vector_format(path):
        return "vector"
    if is_raster_format(path):
        return "raster"
    raise UnsupportedFormatError(
        path, list(SUPPORTED_VECTOR_FORMATS) + list(SUPPORTED_RASTER_FORMATS)
    )
