"""
Clip vector data to a project Area of Interest (AOI) (section 26).

Clipping across mismatched CRS is never performed silently. The caller
must ensure both the data and AOI share a CRS before clipping.
"""

from typing import Tuple, Union

import geopandas as gpd
from shapely.geometry import Polygon, box

from gis.exceptions import AOIError


def _aoi_to_geometry(
    aoi: Union[Polygon, Tuple[float, float, float, float]],
) -> Polygon:
    if isinstance(aoi, Polygon):
        return aoi
    if isinstance(aoi, (tuple, list)) and len(aoi) == 4:
        return box(*aoi)
    raise AOIError(
        "AOI must be a shapely Polygon or a (minx, miny, maxx, maxy) "
        f"bounds tuple, got: {type(aoi)}"
    )


def clip_to_aoi(
    gdf: gpd.GeoDataFrame,
    aoi: Union[Polygon, Tuple[float, float, float, float]],
    aoi_crs: str = None,
    layer_name: str = "layer",
) -> gpd.GeoDataFrame:
    """Clip a vector layer to a CRS-aligned polygon or bounds tuple."""
    if gdf.crs is None:
        raise AOIError(f"Cannot clip '{layer_name}': layer has no CRS set.")

    if aoi_crs is not None and str(aoi_crs) != str(gdf.crs):
        raise AOIError(
            f"AOI CRS ({aoi_crs}) does not match layer '{layer_name}' CRS "
            f"({gdf.crs}). Reproject one to match the other before clipping "
            "- clipping across mismatched CRS is not performed silently."
        )

    aoi_geom = _aoi_to_geometry(aoi)
    aoi_gdf = gpd.GeoDataFrame(geometry=[aoi_geom], crs=gdf.crs)
    clipped = gpd.clip(gdf, aoi_gdf)

    if len(clipped) == 0:
        raise AOIError(
            f"Clipping '{layer_name}' to the given AOI produced zero features. "
            "Check that the AOI actually overlaps the layer's bounds "
            f"({tuple(gdf.total_bounds)})."
        )

    return clipped
