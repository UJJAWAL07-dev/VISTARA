from typing import List, Dict, Any
import geojson
from shapely.geometry import mapping


class GeoConverter:
    """Transforms pixel-space geometries into standard GeoJSON FeatureCollections."""

    @staticmethod
    def to_geojson(features: List[Dict[str, Any]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        geo_features = []
        transform = metadata.get("transform")

        for feat in features:
            poly = feat["polygon"]

            # Map pixel coordinates to geospatial CRS if an Affine transform is available
            if transform is not None:
                exterior_coords = [
                    list(transform * (x, y)) for x, y in poly.exterior.coords
                ]
            else:
                exterior_coords = [list(pt) for pt in poly.exterior.coords]

            geojson_geom = {
                "type": "Polygon",
                "coordinates": [exterior_coords]
            }

            feature_obj = geojson.Feature(
                geometry=geojson_geom,
                properties={
                    "id": feat["id"],
                    "class": feat["class"],
                    "confidence": feat["confidence"],
                    "area_px": feat["area_px"]
                }
            )
            geo_features.append(feature_obj)

        feature_collection = geojson.FeatureCollection(
            features=geo_features,
            properties={
                "image_name": metadata.get("file_name", "unknown"),
                "crs": metadata.get("crs", "EPSG:4326"),
                "total_features": len(geo_features)
            }
        )
        return feature_collection