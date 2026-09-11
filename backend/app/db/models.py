from sqlalchemy import Column, DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from geoalchemy2 import Geometry
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class ProjectDB(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class DatasetDB(Base):
    __tablename__ = "datasets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    name = Column(String(255), nullable=False)
    dataset_type = Column(String(50), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="pending")

    file_path = Column(Text)
    format = Column(String(50))
    crs = Column(String(50))

    bounds = Column(Geometry("POLYGON", srid=4326))

    # Python attribute is dataset_metadata,
    # PostgreSQL column remains "metadata".
    dataset_metadata = Column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)


class ProcessingJobDB(Base):
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True)

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )

    dataset_id = Column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )

    features = Column(JSONB, nullable=False, default=list)
    status = Column(String(50), nullable=False, default="queued")
    result = Column(JSONB)
    error = Column(Text)

    created_at = Column(DateTime(timezone=True), nullable=False)
    updated_at = Column(DateTime(timezone=True), nullable=False)
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))