"""
VISTARA GIS Analysis Engine
===========================

Consumes GIS-ready Layer objects and bundles produced by /gis
(gis.services) and computes:
- spatial relationships (overlay, containment, IoU)
- validation (business rules + AI-vs-ground-truth matching)
- statistics (comparative accuracy metrics)
- composite quality/confidence scoring
- land-use specific analysis
- assembled reports for backend/frontend consumption

This package does NOT:
- perform CRS transformation, geometry repair, or clipping
  (owned by /gis — request additions there instead of duplicating)
- define HTTP routes (owned by /backend)
- train or run ML models (owned by /ai)
"""

__version__ = "0.1.0"