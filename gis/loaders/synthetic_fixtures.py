"""
SYNTHETIC / TEST DATA ONLY.

Generates small, clearly labeled fake datasets for testing loaders
before real sample data is available in /datasets/sample (section 11).
Do not use this as a substitute for the official sample dataset.
Output is written only to the GIS engine's own output directory.
"""

from pathlib import Path
from typing import Optional

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Polygon

from gis.config import OUTPUT_ROOT, WGS84, ensure_dir


def make_synthetic_parcels(out_dir: Optional[Path] = None) -> Path:
    """Create three synthetic WGS84 parcel polygons for loader tests."""
    out_dir = ensure_dir(Path(out_dir or OUTPUT_ROOT / "synthetic"))
    out_path = out_dir / "synthetic_parcels.geojson"

    polygons = [
        Polygon([(77.20, 28.60), (77.201, 28.60), (77.201, 28.601), (77.20, 28.601)]),
        Polygon([(77.202, 28.60), (77.203, 28.60), (77.203, 28.601), (77.202, 28.601)]),
        Polygon([(77.20, 28.602), (77.201, 28.602), (77.201, 28.603), (77.20, 28.603)]),
    ]
    gdf = gpd.GeoDataFrame(
        {
            "parcel_id": ["SYN-001", "SYN-002", "SYN-003"],
            "land_use": ["residential", "commercial", "residential"],
            "source": ["synthetic_test_data"] * 3,
        },
        geometry=polygons,
        crs=WGS84,
    )
    gdf.to_file(out_path, driver="GeoJSON")
    return out_path


def make_synthetic_raster(out_dir: Optional[Path] = None) -> Path:
    """Create a tiny synthetic WGS84 single-band raster for loader tests."""
    out_dir = ensure_dir(Path(out_dir or OUTPUT_ROOT / "synthetic"))
    out_path = out_dir / "synthetic_raster.tif"

    data = np.random.randint(0, 255, size=(10, 10), dtype=np.uint8)
    transform = from_origin(77.20, 28.61, 0.0001, 0.0001)

    with rasterio.open(
        out_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=1,
        dtype=data.dtype,
        crs=WGS84,
        transform=transform,
    ) as dataset:
        dataset.write(data, 1)

    return out_path
