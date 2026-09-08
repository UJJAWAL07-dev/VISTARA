"""
Dataset domain model.

Metadata-only for Phase 3 - no actual file storage/upload handling
yet (that's a later phase once the AI/GIS pipeline needs real files).
Every dataset belongs to exactly one project.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class Dataset:
    project_id: str
    name: str
    dataset_type: str
    description: Optional[str] = None
    status: str = "registered"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
