"""
Project domain model.

This is a plain in-memory representation of "what a project is" -
deliberately NOT a SQLAlchemy model. It exists so the service layer
has a concrete object to work with regardless of what's storing it.
When Phase 5 introduces PostgreSQL/PostGIS, the database member's
ORM model becomes the source of truth and this class can be retired
or kept as a lightweight DTO - the service/route layers above it
won't need to change either way.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4


@dataclass
class Project:
    name: str
    description: Optional[str] = None
    status: str = "active"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
