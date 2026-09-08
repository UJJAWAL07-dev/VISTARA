from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import numpy as np
from PIL import Image

try:
    import rasterio
    from rasterio.transform import Affine
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False


class ImageLoader:
    """Handles raster and imagery loading, format normalization, and geospatial metadata extraction."""

    def __init__(self, target_size: Optional[Tuple[int, int]] = None):
        self.target_size = target_size

    def load(self, file_path: str) -> Tuple[np.ndarray, Dict[str, Any]]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {file_path}")

        metadata: Dict[str, Any] = {
            "file_name": path.name,
            "original_shape": None,
            "transform": None,
            "crs": None,
            "is_geotiff": False
        }

        # Attempt GeoTIFF loading via rasterio
        if RASTERIO_AVAILABLE and path.suffix.lower() in [".tif", ".tiff"]:
            try:
                with rasterio.open(path) as src:
                    # Read RGB/multispectral bands
                    count = min(3, src.count)
                    bands = [src.read(i) for i in range(1, count + 1)]
                    image = np.stack(bands, axis=-1)
                    
                    metadata["transform"] = src.transform
                    metadata["crs"] = str(src.crs) if src.crs else "EPSG:4326"
                    metadata["is_geotiff"] = True
                    metadata["original_shape"] = (src.height, src.width)
                    return self._standardize_dtype(image), metadata
            except Exception:
                pass  # Fall back to standard image reading

        # Standard RGB loading
        with Image.open(path) as img:
            img = img.convert("RGB")
            arr = np.array(img)
            metadata["original_shape"] = (arr.shape[0], arr.shape[1])
            metadata["transform"] = None
            metadata["crs"] = "EPSG:4326"
            return self._standardize_dtype(arr), metadata

    @staticmethod
    def _standardize_dtype(image: np.ndarray) -> np.ndarray:
        if image.dtype != np.uint8:
            image = ((image - image.min()) / (image.max() - image.min() + 1e-8) * 255).astype(np.uint8)
        return image