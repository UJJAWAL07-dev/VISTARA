-- ============================================================
-- VISTARA DATABASE SCHEMA
-- ============================================================
-- PostgreSQL + PostGIS
--
-- This file represents the complete VISTARA database schema.
-- Migrations remain the authoritative incremental setup.
-- ============================================================


-- ============================================================
-- EXTENSIONS
-- ============================================================

CREATE EXTENSION IF NOT EXISTS postgis;


-- ============================================================
-- PROJECTS
-- ============================================================

CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,

    status VARCHAR(50) NOT NULL DEFAULT 'draft',

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT projects_status_check
        CHECK (
            status IN (
                'draft',
                'processing',
                'completed',
                'failed'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_projects_created_at
    ON projects(created_at);

CREATE INDEX IF NOT EXISTS idx_projects_status
    ON projects(status);


-- ============================================================
-- DATASETS
-- ============================================================

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
        CHECK (
            status IN (
                'pending',
                'processing',
                'completed',
                'failed'
            )
        ),

    CONSTRAINT datasets_type_check
        CHECK (
            dataset_type IN (
                'raster',
                'vector',
                'mixed'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_datasets_project_id
    ON datasets(project_id);

CREATE INDEX IF NOT EXISTS idx_datasets_status
    ON datasets(status);

CREATE INDEX IF NOT EXISTS idx_datasets_type
    ON datasets(dataset_type);

CREATE INDEX IF NOT EXISTS idx_datasets_bounds
    ON datasets USING GIST(bounds);


-- ============================================================
-- PROCESSING JOBS
-- ============================================================

CREATE TABLE IF NOT EXISTS processing_jobs (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL,

    dataset_id UUID NOT NULL,

    features JSONB NOT NULL DEFAULT '[]'::jsonb,

    status VARCHAR(50) NOT NULL DEFAULT 'queued',

    result JSONB,

    error TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,

    CONSTRAINT processing_jobs_project_fk
        FOREIGN KEY (project_id)
        REFERENCES projects(id)
        ON DELETE CASCADE,

    CONSTRAINT processing_jobs_dataset_fk
        FOREIGN KEY (dataset_id)
        REFERENCES datasets(id)
        ON DELETE CASCADE,

    CONSTRAINT processing_jobs_status_check
        CHECK (
            status IN (
                'queued',
                'processing',
                'completed',
                'failed'
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_project_id
    ON processing_jobs(project_id);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_dataset_id
    ON processing_jobs(dataset_id);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_status
    ON processing_jobs(status);

CREATE INDEX IF NOT EXISTS idx_processing_jobs_created_at
    ON processing_jobs(created_at);


-- ============================================================
-- SPATIAL FEATURES
-- ============================================================

CREATE TABLE IF NOT EXISTS spatial_features (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL,

    dataset_id UUID NOT NULL,

    job_id UUID NOT NULL,

    feature_class VARCHAR(100) NOT NULL,

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
        ON DELETE CASCADE
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
    ON spatial_features USING GIST(geometry);


-- ============================================================
-- ANALYSIS RESULTS
-- ============================================================

CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY,

    job_id UUID NOT NULL,

    statistics JSONB NOT NULL DEFAULT '{}'::jsonb,

    issues JSONB NOT NULL DEFAULT '[]'::jsonb,

    validation_status VARCHAR(50),

    validation_confidence DOUBLE PRECISION,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT analysis_results_job_fk
        FOREIGN KEY (job_id)
        REFERENCES processing_jobs(id)
        ON DELETE CASCADE,

    CONSTRAINT analysis_results_validation_status_check
        CHECK (
            validation_status IS NULL
            OR validation_status IN (
                'valid',
                'invalid',
                'partial',
                'pending'
            )
        ),

    CONSTRAINT analysis_results_confidence_check
        CHECK (
            validation_confidence IS NULL
            OR (
                validation_confidence >= 0
                AND validation_confidence <= 1
            )
        )
);

CREATE INDEX IF NOT EXISTS idx_analysis_results_job_id
    ON analysis_results(job_id);

CREATE INDEX IF NOT EXISTS idx_analysis_results_validation_status
    ON analysis_results(validation_status);

CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at
    ON analysis_results(created_at);