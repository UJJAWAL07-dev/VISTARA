"""
Request/response schemas for the Projects API.

Kept separate from app/models/project.py: schemas define the API
contract (what clients send/receive), while the model defines the
internal domain shape. This split is what lets the storage backend
change in Phase 5 without changing the API contract.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, examples=["Coastal Erosion Survey"])
    description: Optional[str] = Field(default=None, max_length=2000)
    status: str = Field(default="active", examples=["active"])


class ProjectUpdate(BaseModel):
    """All fields optional - only provided fields are changed (partial update)."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[str] = Field(default=None)


class ProjectResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    description: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
