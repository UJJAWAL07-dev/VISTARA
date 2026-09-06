"""
GIS engine exception hierarchy (section 28).

Wraps low-level library errors (GDAL/Fiona/Rasterio/PyProj) with
clear, actionable context so failures don't surface as obscure
library tracebacks to backend/AI/analysis integrators.
"""


class GISEngineError(Exception):
    """Base class for all GIS engine errors."""


class UnsupportedFormatError(GISEngineError):
    def __init__(self, path, supported_formats):
        self.path = str(path)
        self.supported_formats = supported_formats
        super().__init__(
            f"Unsupported file format for '{self.path}'. "
            f"Supported extensions: {sorted(supported_formats)}"
        )


class FileNotFoundInGISError(GISEngineError):
    def __init__(self, path):
        self.path = str(path)
        super().__init__(f"GIS input file not found: '{self.path}'")


class MissingCRSError(GISEngineError):
    def __init__(self, layer_name):
        self.layer_name = layer_name
        super().__init__(
            f"Layer '{layer_name}' has no CRS defined. "
            f"Inspect and assign a CRS before running spatial operations."
        )


class ReprojectionError(GISEngineError):
    def __init__(self, layer_name, source_crs, target_crs, original_error=None):
        self.layer_name = layer_name
        self.source_crs = source_crs
        self.target_crs = target_crs
        msg = f"Unable to transform layer '{layer_name}' from {source_crs} to {target_crs}."
        if original_error:
            msg += f" Cause: {original_error}"
        super().__init__(msg)


class GeometryValidationError(GISEngineError):
    def __init__(self, layer_name, detail):
        self.layer_name = layer_name
        super().__init__(f"Invalid geometry in layer '{layer_name}': {detail}")


class VectorLoadError(GISEngineError):
    def __init__(self, path, original_error=None):
        self.path = str(path)
        msg = f"Failed to load vector data from '{self.path}'."
        if original_error:
            msg += f" Cause: {original_error}"
        super().__init__(msg)


class RasterLoadError(GISEngineError):
    def __init__(self, path, original_error=None):
        self.path = str(path)
        msg = f"Failed to load raster data from '{self.path}'."
        if original_error:
            msg += f" Cause: {original_error}"
        super().__init__(msg)


class LayerNotFoundError(GISEngineError):
    def __init__(self, layer_name):
        self.layer_name = layer_name
        super().__init__(f"Layer '{layer_name}' was not found.")


class AOIError(GISEngineError):
    def __init__(self, detail):
        super().__init__(f"Area of Interest (AOI) error: {detail}")
