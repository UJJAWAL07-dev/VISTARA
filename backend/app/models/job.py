"""
Job domain model.

Represents one processing request accepted by the orchestrator.
project_id and dataset_id are stored as opaque strings here - this
phase does not cross-validate them against the real Projects/Datasets
stores (see process_service.py docstring for why).
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List
from uuid import uuid4

JOB_STATUSES = {"queued", "processing", "completed", "failed"}


@dataclass
class Job:
    project_id: str
    dataset_id: str
    features: List[str]
    status: str = "queued"
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
