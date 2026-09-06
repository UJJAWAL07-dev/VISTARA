"""
Build Layer objects from loaded vector/raster data.

This bridges the raw loaders and the metadata-rich Layer model used by
backend, AI, analysis, and frontend integrations.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import geopandas as gpd

from gis.layers.layer_model import Layer, LayerType
from gis.loaders.raster_loader import inspect_raster
from gis.loaders.vector_loader import inspect_vector


def build_vector_layer(
    gdf: gpd.GeoDataFrame,
    layer_id: str,
    name: str,
    source: Union[str, Path],
    metadata: Optional[Dict[str, Any]] = None,
) -> Layer:
    """Wrap an already-loaded GeoDataFrame without modifying its data."""
    info = inspect_vector(gdf)

    return Layer(
        id=layer_id,
        name=name,
        type=LayerType.VECTOR,
        source=str(source),
        crs=info["crs"],
        bounds=info["bounds"],
        geometry_type=info["geometry_types"],
        feature_count=info["feature_count"],
        metadata=metadata or {},
        data=gdf,
    )


def build_raster_layer(
    path: Union[str, Path],
    layer_id: str,
    name: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Layer:
    """Build a Layer from a raster path without retaining an open handle."""
    path = Path(path)
    info = inspect_raster(path)

    return Layer(
        id=layer_id,
        name=name,
        type=LayerType.RASTER,
        source=str(path),
        crs=info["crs"],
        bounds=info["bounds"],
        geometry_type=None,
        feature_count=None,
        raster_meta={
            "width": info["width"],
            "height": info["height"],
            "resolution": info["resolution"],
            "band_count": info["band_count"],
            "dtype": info["dtype"],
            "driver": info["driver"],
        },
        metadata=metadata or {},
        data=None,
    )
