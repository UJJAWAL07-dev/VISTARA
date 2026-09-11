"""
AI output ingestion (sections 14/15).

Normalizes common AI spatial output shapes into a GeoDataFrame, then
routes the result through the standard vector preparation pipeline.
This module contains no ML logic and never guesses a missing CRS.

Supported inputs:
- GeoJSON-like FeatureCollection dictionaries
- GeoPandas GeoDataFrames
- Lists of records with ``geometry`` and optional ``properties``
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import geopandas as gpd
from shapely.geometry import Polygon, shape

from gis.exceptions import GISEngineError, MissingCRSError
from gis.layers.layer_model import Layer
from gis.processing.pipeline import prepare_vector_layer


class UnsupportedAIOutputError(GISEngineError):
    """Raised when an AI result does not match a supported input shape."""

    def __init__(self, detail: str):
        super().__init__(f"Unrecognized AI output format: {detail}")


def _from_geojson_dict(data: Dict[str, Any]) -> gpd.GeoDataFrame:
    features = data.get("features")
    if features is None:
        raise UnsupportedAIOutputError(
            "dict provided but missing a 'features' key; expected a "
            "GeoJSON FeatureCollection."
        )

    try:
        return gpd.GeoDataFrame.from_features(features)
    except Exception as error:
        raise UnsupportedAIOutputError(
            f"invalid GeoJSON FeatureCollection: {error}"
        ) from error


def _from_records(records: List[Dict[str, Any]]) -> gpd.GeoDataFrame:
    geometries = []
    properties = []

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise UnsupportedAIOutputError(
                f"record at index {index} must be a dict, got {type(record)}"
            )

        geometry = record.get("geometry")
        if geometry is None:
            raise UnsupportedAIOutputError(
                f"record at index {index} is missing a 'geometry' key."
            )

        try:
            if not hasattr(geometry, "geom_type"):
                geometry = shape(geometry)
        except Exception as error:
            raise UnsupportedAIOutputError(
                f"record at index {index} has invalid geometry: {error}"
            ) from error

        geometries.append(geometry)
        properties.append(record.get("properties", {}))

    return gpd.GeoDataFrame(properties, geometry=geometries)


def normalize_ai_output(
    ai_output: Union[Dict[str, Any], gpd.GeoDataFrame, List[Dict[str, Any]]],
    assume_crs: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """
    Normalize a supported AI output shape into a CRS-aware GeoDataFrame.

    ``assume_crs`` labels coordinates whose CRS is known out-of-band; it
    does not transform coordinates. A missing CRS without that explicit
    argument raises ``MissingCRSError`` rather than being guessed.
    """
    if isinstance(ai_output, gpd.GeoDataFrame):
        gdf = ai_output.copy()
    elif isinstance(ai_output, dict):
        gdf = _from_geojson_dict(ai_output)
    elif isinstance(ai_output, list):
        gdf = _from_records(ai_output)
    else:
        raise UnsupportedAIOutputError(f"unsupported type {type(ai_output)}")

    if gdf.crs is None:
        if assume_crs is None:
            raise MissingCRSError("AI output")
        gdf = gdf.set_crs(assume_crs, allow_override=False)

    return gdf


def ai_output_to_layer(
    ai_output: Union[Dict[str, Any], gpd.GeoDataFrame, List[Dict[str, Any]]],
    layer_id: str,
    name: str,
    assume_crs: Optional[str] = None,
    target_crs: Optional[str] = None,
    repair: bool = True,
    aoi: Optional[Union[Polygon, Tuple[float, float, float, float]]] = None,
    aoi_crs: Optional[str] = None,
    source: str = "AI",
) -> Layer:
    """
    Convert an AI prediction into a prepared GIS Layer.

    Geometry repair defaults to enabled for AI-generated geometry, while
    remaining explicit and recorded by the processing pipeline metadata.
    """
    gdf = normalize_ai_output(ai_output, assume_crs=assume_crs)

    return prepare_vector_layer(
        gdf,
        layer_id=layer_id,
        name=name,
        source=source,
        target_crs=target_crs,
        repair=repair,
        aoi=aoi,
        aoi_crs=aoi_crs,
        metadata={"source": "AI", "ai_generated": True},
    )
