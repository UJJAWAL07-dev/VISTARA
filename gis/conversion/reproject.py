"""
CRS transformation for vector layers.

Per section 8/40: never assume a CRS, never silently mix CRS.
This module only transforms; it never guesses a missing CRS on its
own. If a layer has no CRS, the caller must explicitly assign one via
``ensure_crs(..., assume_crs=...)`` with a documented reason.
"""

from typing import Optional

import geopandas as gpd

from gis.exceptions import MissingCRSError, ReprojectionError


def ensure_crs(
    gdf: gpd.GeoDataFrame,
    layer_name: str = "layer",
    assume_crs: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """
    Guarantee that the GeoDataFrame has a CRS set.

    If a CRS is already set, return the GeoDataFrame unchanged. If not,
    an explicitly supplied ``assume_crs`` labels the existing coordinates;
    it does not reproject them.
    """
    if gdf.crs is not None:
        return gdf

    if assume_crs is None:
        raise MissingCRSError(layer_name)

    return gdf.set_crs(assume_crs, allow_override=False)


def reproject_vector(
    gdf: gpd.GeoDataFrame,
    target_crs: str,
    layer_name: str = "layer",
) -> gpd.GeoDataFrame:
    """
    Reproject a GeoDataFrame to ``target_crs`` without mutating the input.

    The input must already have a CRS. Call ``ensure_crs`` first when the
    source CRS is known out-of-band but missing from the data.
    """
    if gdf.crs is None:
        raise MissingCRSError(layer_name)

    if str(gdf.crs) == str(target_crs):
        return gdf.copy()

    try:
        return gdf.to_crs(target_crs)
    except Exception as error:
        raise ReprojectionError(
            layer_name=layer_name,
            source_crs=str(gdf.crs),
            target_crs=target_crs,
            original_error=error,
        ) from error
