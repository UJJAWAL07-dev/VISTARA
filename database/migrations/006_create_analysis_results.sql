-- VISTARA Database
-- Migration 006: Create analysis_results table

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