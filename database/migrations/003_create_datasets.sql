-- VISTARA Database
-- Migration 003: Create datasets table

CREATE TABLE IF NOT EXISTS datasets (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    dataset_type VARCHAR(50) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',

    file_path TEXT,
    format VARCHAR(50),
    crs VARCHAR(50),
    bounds GEOMETRY(Polygon, 4326),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT datasets_project_fk
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT datasets_status_check
        CHECK (status IN ('pending', 'processing', 'completed', 'failed')),

    CONSTRAINT datasets_type_check
        CHECK (dataset_type IN ('raster', 'vector', 'mixed'))
);

CREATE INDEX IF NOT EXISTS idx_datasets_project_id
    ON datasets(project_id);

CREATE INDEX IF NOT EXISTS idx_datasets_status
    ON datasets(status);

CREATE INDEX IF NOT EXISTS idx_datasets_type
    ON datasets(dataset_type);

CREATE INDEX IF NOT EXISTS idx_datasets_bounds
    ON datasets
    USING GIST(bounds);