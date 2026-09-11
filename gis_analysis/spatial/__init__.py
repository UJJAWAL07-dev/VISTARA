from .crs_check import assert_consistent_crs
from .geometry_metrics import area_of, centroid_distance, intersection_area, iou
from .relationships import find_contained, find_overlaps, spatial_match

__all__ = [
    "iou",
    "intersection_area",
    "area_of",
    "centroid_distance",
    "find_overlaps",
    "find_contained",
    "spatial_match",
    "assert_consistent_crs",
]