"""
Request/response schemas for the Datasets API.

dataset_type is a free-form string for now (e.g. "shapefile",
"geojson", "csv", "raster") rather than a strict enum, since the
GIS/GIS-analysis members may need to register formats we haven't
anticipated yet. Tightening this to an enum can happen once the
supported format list is finalized with them.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DatasetCreate(BaseModel):
    project_id: str = Field(..., description="ID of the project this dataset belongs to")
    name: str = Field(..., min_length=1, max_length=200, examples=["Shoreline 2024 Survey"])
    dataset_type: str = Field(..., min_length=1, max_length=50, examples=["geojson"])
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="registered")


class DatasetUpdate(BaseModel):
    """All fields optional - only provided fields are changed (partial update)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    dataset_type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None)


class DatasetResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    project_id: str
    name: str
    dataset_type: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
