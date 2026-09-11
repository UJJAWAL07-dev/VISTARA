"""
CRS consistency guard for analysis functions.

Analysis code verifies that layers already share a CRS. Reprojection is
owned by /gis and is intentionally not performed here.
"""

import geopandas as gpd

from gis_analysis.exceptions import InconsistentCRSError


def assert_consistent_crs(*gdfs: gpd.GeoDataFrame, context: str = "operation") -> str:
    """Verify all provided GeoDataFrames have the same non-null CRS."""
    crs_values = set()
    for gdf in gdfs:
        if gdf.crs is None:
            raise InconsistentCRSError(f"a layer passed to '{context}' has no CRS set")
        crs_values.add(str(gdf.crs))

    if len(crs_values) > 1:
        raise InconsistentCRSError(
            f"layers passed to '{context}' have differing CRS values: {sorted(crs_values)}"
        )

    return crs_values.pop()