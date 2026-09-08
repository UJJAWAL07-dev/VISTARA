"""
Request/response schemas for the Processing (job) API.

SUPPORTED_FEATURES is the single source of truth for valid feature
names - both the Pydantic validator here and any future service-layer
logic should reference this constant rather than hardcoding the list
twice.
"""

from typing import List

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


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
