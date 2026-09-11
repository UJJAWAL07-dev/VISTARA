-- VISTARA Database
-- Migration 005: Create spatial_features table

CREATE TABLE IF NOT EXISTS spatial_features (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL,
    dataset_id UUID NOT NULL,
    job_id UUID,

    feature_class VARCHAR(50) NOT NULL,

    geometry GEOMETRY(Geometry, 4326) NOT NULL,

    confidence DOUBLE PRECISION,

    source VARCHAR(100),

    properties JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT spatial_features_project_fk
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT spatial_features_dataset_fk
        FOREIGN KEY (dataset_id)
        REFERENCES datasets(id)
        ON DELETE CASCADE,

    CONSTRAINT spatial_features_job_fk
        FOREIGN KEY (job_id)
        REFERENCES processing_jobs(id)
        ON DELETE SET NULL,

    CONSTRAINT spatial_features_class_check
        CHECK (
            feature_class IN (
                'building',
                'parcel',
                'road',
                'land_use'
            )
        ),

    CONSTRAINT spatial_features_confidence_check
        CHECK (
            confidence IS NULL
            OR (confidence >= 0 AND confidence <= 1)
        )
);

CREATE INDEX IF NOT EXISTS idx_spatial_features_project_id
    ON spatial_features(project_id);

CREATE INDEX IF NOT EXISTS idx_spatial_features_dataset_id
    ON spatial_features(dataset_id);

CREATE INDEX IF NOT EXISTS idx_spatial_features_job_id
    ON spatial_features(job_id);

CREATE INDEX IF NOT EXISTS idx_spatial_features_class
    ON spatial_features(feature_class);

CREATE INDEX IF NOT EXISTS idx_spatial_features_geometry
    ON spatial_features
    USING GIST(geometry);