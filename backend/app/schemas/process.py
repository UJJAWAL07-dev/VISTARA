"""
Request/response schemas for the Processing (job) API.

SUPPORTED_FEATURES is the single source of truth for valid feature
names - both the Pydantic validator here and any future service-layer
logic should reference this constant rather than hardcoding the list
twice.

Phase 4 adds typed schemas for the AI/GIS/Analysis result shape so
completed jobs return structured data rather than an untyped dict.
Geometry/properties inside GeoJSON features stay as flexible
Dict[str, Any] deliberately - fully modeling every GeoJSON geometry
type here would be over-engineering for what is currently mock data.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

SUPPORTED_FEATURES = {"parcels", "buildings", "roads", "land_use"}


class ProcessRequest(BaseModel):
    project_id: str = Field(..., min_length=1, examples=["project-001"])
    dataset_id: str = Field(..., min_length=1, examples=["dataset-001"])
    features: List[str] = Field(..., min_length=1, examples=[["parcels", "buildings"]])

    @field_validator("features")
    @classmethod
    def validate_features(cls, value: List[str]) -> List[str]:
        unsupported = [f for f in value if f not in SUPPORTED_FEATURES]
        if unsupported:
            raise ValueError(
                f"Unsupported feature(s): {unsupported}. "
                f"Supported features are: {sorted(SUPPORTED_FEATURES)}"
            )
        return value


class ProcessResponse(BaseModel):
    job_id: str
    status: str


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    id: Optional[str] = None
    geometry: Dict[str, Any]
    properties: Dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: List[GeoJSONFeature]


class GISResult(BaseModel):
    layer_id: str
    name: str
    crs: str
    feature_count: int
    geojson: GeoJSONFeatureCollection


class AnalysisIssue(BaseModel):
    issue_id: str
    type: str
    severity: str


class AnalysisValidation(BaseModel):
    status: str
    confidence: float


class AnalysisResult(BaseModel):
    statistics: Dict[str, int]
    issues: List[AnalysisIssue]
    validation: AnalysisValidation


class ProcessResult(BaseModel):
    ai: GeoJSONFeatureCollection
    gis: GISResult
    analysis: AnalysisResult


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[ProcessResult] = None
    error: Optional[str] = None
