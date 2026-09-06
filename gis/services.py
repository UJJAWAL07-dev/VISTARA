"""
Backend-facing service interface (section 16).

Backend should import this module instead of reaching into GIS loader,
processing, conversion, or layer internals. This module defines no HTTP
routes; it only provides stable callable GIS operations.

Return shapes are consistent:
- layer operations return a ``Layer``
- data operations return JSON-serializable dicts or strings
- failures use ``GISEngineError`` subclasses
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from shapely.geometry import Polygon

from gis.config import (
    BUILDINGS_DIR,
    DTM_DIR,
    DSM_DIR,
    IMAGERY_DIR,
    LANDUSE_DIR,
    PARCELS_DIR,
    ROADS_DIR,
    WGS84,
)
from gis.config.formats import (
    SUPPORTED_RASTER_FORMATS,
    SUPPORTED_VECTOR_FORMATS,
)
from gis.conversion.vector_convert import convert_to_geojson, vector_to_geojson_dict
from gis.exceptions import GISEngineError
from gis.layers.ai_adapter import ai_output_to_layer
from gis.layers.layer_factory import build_raster_layer
from gis.layers.layer_model import Layer
from gis.loaders.raster_loader import inspect_raster
from gis.loaders.vector_loader import load_vector
from gis.processing.pipeline import prepare_vector_layer

_SAMPLE_VECTOR_DIRS = {
    "parcels": PARCELS_DIR,
    "buildings": BUILDINGS_DIR,
    "roads": ROADS_DIR,
    "land-use": LANDUSE_DIR,
}
_SAMPLE_RASTER_DIRS = {
    "imagery": IMAGERY_DIR,
    "dsm": DSM_DIR,
    "dtm": DTM_DIR,
}


def _list_files(directory: Path, supported_extensions: set[str]) -> List[str]:
    if not directory.exists():
        return []
    return sorted(
        path.name
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in supported_extensions
    )


def list_sample_layers() -> Dict[str, Dict[str, List[str]]]:
    """List sample dataset files grouped by vector/raster category."""
    return {
        "vector": {
            name: _list_files(directory, set(SUPPORTED_VECTOR_FORMATS))
            for name, directory in _SAMPLE_VECTOR_DIRS.items()
        },
        "raster": {
            name: _list_files(directory, set(SUPPORTED_RASTER_FORMATS))
            for name, directory in _SAMPLE_RASTER_DIRS.items()
        },
    }


def load_and_prepare_vector_layer(
    path: Union[str, Path],
    layer_id: str,
    name: str,
    target_crs: Optional[str] = None,
    assume_crs: Optional[str] = None,
    repair: bool = False,
    aoi_bounds: Optional[Tuple[float, float, float, float]] = None,
    aoi_crs: Optional[str] = None,
) -> Layer:
    """Load a vector file and run it through the preparation pipeline."""
    gdf = load_vector(path)
    return prepare_vector_layer(
        gdf,
        layer_id=layer_id,
        name=name,
        source=path,
        target_crs=target_crs,
        assume_crs=assume_crs,
        repair=repair,
        aoi=aoi_bounds,
        aoi_crs=aoi_crs,
    )


def prepare_layer_bundle(
    layer_specs: List[Dict[str, Any]],
    target_crs: Optional[str] = None,
    aoi_bounds: Optional[Tuple[float, float, float, float]] = None,
    aoi_crs: Optional[str] = None,
) -> Dict[str, Layer]:
    """
    Load and prepare multiple related vector layers consistently.

    Each spec must contain ``path``, ``layer_id``, and ``name``. It may
    also contain ``assume_crs`` and ``repair``. The target CRS and AOI
    are applied uniformly to every layer in the bundle.
    """
    bundle: Dict[str, Layer] = {}

    for spec in layer_specs:
        layer = load_and_prepare_vector_layer(
            path=spec["path"],
            layer_id=spec["layer_id"],
            name=spec["name"],
            assume_crs=spec.get("assume_crs"),
            target_crs=target_crs,
            repair=spec.get("repair", False),
            aoi_bounds=aoi_bounds,
            aoi_crs=aoi_crs,
        )
        bundle[layer.id] = layer

    return bundle


def get_analysis_ready_bundle_summary(
    bundle: Dict[str, Layer],
) -> Dict[str, Any]:
    """Return serializable bundle metadata and CRS consistency details."""
    summaries = {
        layer_id: layer.summary()
        for layer_id, layer in bundle.items()
    }
    crs_values = {summary["crs"] for summary in summaries.values()}

    return {
        "layer_count": len(bundle),
        "layers": summaries,
        "consistent_crs": len(crs_values) <= 1,
        "crs_values_present": sorted(
            value for value in crs_values if value is not None
        ),
    }


def load_raster_layer(path: Union[str, Path], layer_id: str, name: str) -> Layer:
    """Build a raster Layer without retaining an open file handle."""
    return build_raster_layer(path, layer_id=layer_id, name=name)


def get_raster_metadata(path: Union[str, Path]) -> Dict[str, Any]:
    """Inspect a raster and return metadata without building a Layer."""
    return inspect_raster(path)


def get_layer_geojson(layer: Layer, target_crs: str = WGS84) -> Dict[str, Any]:
    """Return a vector Layer as a browser-facing GeoJSON dictionary."""
    if not layer.is_vector() or layer.data is None:
        raise GISEngineError(
            f"Layer '{layer.id}' is not a vector layer with loaded data; "
            "cannot produce GeoJSON."
        )
    return vector_to_geojson_dict(
        layer.data,
        layer_name=layer.name,
        target_crs=target_crs,
    )


def export_layer_geojson_file(
    layer: Layer,
    out_path: Union[str, Path],
    target_crs: str = WGS84,
) -> str:
    """Export a vector Layer to GeoJSON and return the output path string."""
    if not layer.is_vector() or layer.data is None:
        raise GISEngineError(
            f"Layer '{layer.id}' is not a vector layer with loaded data; "
            "cannot export GeoJSON."
        )
    output = convert_to_geojson(
        layer.data,
        out_path,
        layer_name=layer.name,
        target_crs=target_crs,
    )
    return str(output)


def ingest_ai_layer(
    ai_output: Any,
    layer_id: str,
    name: str,
    assume_crs: Optional[str] = None,
    target_crs: Optional[str] = None,
    repair: bool = True,
    aoi_bounds: Optional[Tuple[float, float, float, float]] = None,
    aoi_crs: Optional[str] = None,
) -> Layer:
    """Convert AI spatial output into a GIS-ready Layer."""
    return ai_output_to_layer(
        ai_output,
        layer_id=layer_id,
        name=name,
        assume_crs=assume_crs,
        target_crs=target_crs,
        repair=repair,
        aoi=aoi_bounds,
        aoi_crs=aoi_crs,
    )
