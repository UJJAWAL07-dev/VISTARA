"""
CRS constants and helpers.

Per section 8: do NOT blindly reproject everything to EPSG:4326.
- Use WGS84 (EPSG:4326) for browser-facing GeoJSON output.
- Use an appropriate local UTM (metric, projected) CRS for area/
  distance/buffer operations.
- Never assume a dataset's CRS — always inspect it first (section 40).
"""

import os
import math

WGS84 = "EPSG:4326"
WEB_MERCATOR = "EPSG:3857"  # only for tile/web-map visualization contexts

# Optional override: if the team agrees on one fixed projected CRS for
# the demo AOI (e.g. a specific UTM zone for the sample site), set this
# via env var. Otherwise callers should compute it per-dataset with
# get_utm_epsg() instead of assuming a single zone for all of India.
DEFAULT_PROJECTED_CRS = os.environ.get("VISTARA_DEFAULT_PROJECTED_CRS", None)


def get_utm_epsg(lon: float, lat: float) -> str:
    """
    Return the EPSG code (as 'EPSG:XXXXX') for the UTM zone containing
    the given WGS84 longitude/latitude. Use this instead of hardcoding
    a UTM zone, since the sample AOI's location determines the correct
    zone.

    Example: lon=77.2, lat=28.6 (Delhi) -> 'EPSG:32643'
    """
    zone_number = int(math.floor((lon + 180) / 6) % 60) + 1
    is_northern = lat >= 0
    base = 32600 if is_northern else 32700
    return f"EPSG:{base + zone_number}"
