"""
Typed exception hierarchy for the GIS Analysis Engine.
Mirrors the pattern in gis.exceptions — wrap failures with context,
never let a raw shapely/numpy exception surface unexplained.
"""


class AnalysisError(Exception):
    """Base class for all GIS analysis errors."""


class InconsistentCRSError(AnalysisError):
    def __init__(self, detail):
        super().__init__(
            f"Layers passed to analysis do not share a consistent CRS: {detail}. "
            f"Use gis.services.prepare_layer_bundle() to guarantee a shared CRS "
            f"before running analysis."
        )


class EmptyLayerError(AnalysisError):
    def __init__(self, layer_name):
        self.layer_name = layer_name
        super().__init__(f"Layer '{layer_name}' has zero features — cannot run analysis on it.")


class LayerMismatchError(AnalysisError):
    def __init__(self, detail):
        super().__init__(f"Layer mismatch: {detail}")


class ValidationRuleError(AnalysisError):
    def __init__(self, rule_name, detail):
        self.rule_name = rule_name
        super().__init__(f"Validation rule '{rule_name}' failed to run: {detail}")


class ScoringError(AnalysisError):
    def __init__(self, detail):
        super().__init__(f"Scoring error: {detail}")