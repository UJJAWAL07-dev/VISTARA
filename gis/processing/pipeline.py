"""
Light processing pipeline for vector layers (sections 22/23).

When both are requested, clipping occurs before reprojection so the AOI
is matched against the layer's native CRS and only the clipped subset is
reprojected afterward. This is intentionally not a workflow engine.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from shapely.geometry import Polygon

from gis.conversion.reproject import ensure_crs, reproject_vector
from gis.layers.layer_factory import build_vector_layer
from gis.layers.layer_model import Layer
from gis.processing.clip import clip_to_aoi
from gis.processing.geometry_ops import check_validity, repair_geometry


def prepare_vector_layer(
    gdf,
    layer_id: str,
    name: str,
    source: Union[str, Path],
    target_crs: Optional[str] = None,
    assume_crs: Optional[str] = None,
    repair: bool = False,
    aoi: Optional[Union[Polygon, Tuple[float, float, float, float]]] = None,
    aoi_crs: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Layer:
    """
    Prepare a raw GeoDataFrame and return a GIS-ready vector Layer.

    Steps are explicit and ordered as ensure CRS, clip, reproject,
    optional repair, then wrap with metadata.
    """
    working = gdf

    if working.crs is None and assume_crs is not None:
        working = ensure_crs(working, layer_name=name, assume_crs=assume_crs)

    if aoi is not None:
        working = clip_to_aoi(
            working,
            aoi,
            aoi_crs=aoi_crs,
            layer_name=name,
        )

    if target_crs is not None:
        working = reproject_vector(working, target_crs, layer_name=name)

    validity_before = check_validity(working, layer_name=name)

    if repair and not validity_before["is_all_valid"]:
        working = repair_geometry(working, layer_name=name, strict=False)

    layer_metadata = dict(metadata or {})
    layer_metadata["validity_before_processing"] = validity_before
    layer_metadata["repaired"] = bool(repair)
    layer_metadata["clipped_to_aoi"] = aoi is not None

    return build_vector_layer(
        working,
        layer_id=layer_id,
        name=name,
        source=source,
        metadata=layer_metadata,
    )
