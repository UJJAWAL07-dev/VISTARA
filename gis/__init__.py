"""
VISTARA GIS Engine
==================

The geospatial processing backbone for VISTARA. Converts, prepares,
loads, and manages spatial data (vector + raster) so it can be
consumed by the backend, frontend WebGIS, AI/ML system, and the
GIS Analysis Engine.

This package does NOT contain:
- HTTP/API routes        (owned by /backend)
- ML training code       (owned by /ai)
- Analysis/scoring logic (owned by /gis-analysis)
- Database schema        (owned by /database)

See README.md for the full data-flow and integration contract.
"""

__version__ = "0.1.0"
