-- VISTARA Database
-- Migration 004: Create processing_jobs table

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