"""
Raster data loading and inspection.

Supports GeoTIFF and related formats (section 10).
Handles orthorectified imagery, drone imagery, DSM, and DTM inputs.
"""

from pathlib import Path
from typing import Union

import rasterio

from gis.config.formats import SUPPORTED_RASTER_FORMATS, is_raster_format
from gis.exceptions import (
    FileNotFoundInGISError,
    RasterLoadError,
    UnsupportedFormatError,
)


def load_raster(path: Union[str, Path]):
    """
    Open a raster and return its open rasterio dataset handle.

    The caller is responsible for closing it, either with a context
    manager or by calling ``close``.
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundInGISError(path)

    if not is_raster_format(path):
        raise UnsupportedFormatError(path, list(SUPPORTED_RASTER_FORMATS))

    try:
        return rasterio.open(path)
    except Exception as error:
        raise RasterLoadError(path, original_error=error) from error


def inspect_raster(path: Union[str, Path]) -> dict:
    """Return basic raster metadata while safely closing the file handle."""
    with load_raster(path) as dataset:
        return {
            "width": dataset.width,
            "height": dataset.height,
            "crs": str(dataset.crs) if dataset.crs else None,
            "bounds": tuple(dataset.bounds),
            "resolution": dataset.res,
            "band_count": dataset.count,
            "dtype": dataset.dtypes[0] if dataset.dtypes else None,
            "driver": dataset.driver,
        }
