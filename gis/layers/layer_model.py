"""
The GIS layer model (sections 12/13).

Every spatial dataset flowing through the engine, vector or raster, is
represented as a Layer with consistent metadata. Downstream consumers
can inspect a Layer without knowing whether its payload is a
GeoDataFrame or a raster file.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import geopandas as gpd


class LayerType(str, Enum):
    VECTOR = "vector"
    RASTER = "raster"


@dataclass
class Layer:
    """A single spatial layer with a consistent metadata contract."""

    id: str
    name: str
    type: LayerType
    source: str
    crs: Optional[str] = None
    bounds: Optional[Tuple[float, float, float, float]] = None
    geometry_type: Optional[List[str]] = None
    feature_count: Optional[int] = None
    raster_meta: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    data: Optional[gpd.GeoDataFrame] = None

    def is_vector(self) -> bool:
        return self.type == LayerType.VECTOR

    def is_raster(self) -> bool:
        return self.type == LayerType.RASTER

    def summary(self) -> Dict[str, Any]:
        """Return a plain-dict summary safe for downstream consumers."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type.value,
            "source": self.source,
            "crs": self.crs,
            "bounds": self.bounds,
            "geometry_type": self.geometry_type,
            "feature_count": self.feature_count,
            "raster_meta": self.raster_meta,
            "metadata": self.metadata,
        }
