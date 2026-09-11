"""Geometry-to-geometry metrics used throughout GIS analysis."""

from shapely.geometry.base import BaseGeometry


def intersection_area(geom_a: BaseGeometry, geom_b: BaseGeometry) -> float:
    """Return the area shared by two geometries."""
    if geom_a is None or geom_b is None or geom_a.is_empty or geom_b.is_empty:
        return 0.0
    if not geom_a.intersects(geom_b):
        return 0.0
    return geom_a.intersection(geom_b).area


def area_of(geom: BaseGeometry) -> float:
    """Return the area of a geometry."""
    return 0.0 if geom is None or geom.is_empty else geom.area


def iou(geom_a: BaseGeometry, geom_b: BaseGeometry) -> float:
    """Return intersection-over-union for two geometries in [0, 1]."""
    if geom_a is None or geom_b is None or geom_a.is_empty or geom_b.is_empty:
        return 0.0

    inter = intersection_area(geom_a, geom_b)
    if inter == 0.0:
        return 0.0

    union = geom_a.union(geom_b).area
    return 0.0 if union == 0.0 else inter / union


def centroid_distance(geom_a: BaseGeometry, geom_b: BaseGeometry) -> float:
    """Return centroid distance in the geometries' CRS units."""
    return geom_a.centroid.distance(geom_b.centroid)