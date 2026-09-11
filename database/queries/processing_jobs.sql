-- VISTARA Database
-- Processing job queries

-- Get jobs for a project
SELECT
    id,
    project_id,
    dataset_id,
    status,
    features,
    result,
    error,
    created_at,
    updated_at,
    started_at,
    completed_at
FROM processing_jobs
WHERE project_id = $1
ORDER BY created_at DESC;


-- Get job by ID
SELECT
    id,
    project_id,
    dataset_id,
    status,
    features,
    result,
    error,
    created_at,
    updated_at,
    started_at,
    completed_at
FROM processing_jobs
WHERE id = $1;


-- Create processing job
INSERT INTO processing_jobs (
    id,
    project_id,
    dataset_id,
    features,
    status
)
VALUES (
    $1,
    $2,
    $3,
    COALESCE($4, '[]'::jsonb),
    COALESCE($5, 'queued')
)
RETURNING
    id,
    project_id,
    dataset_id,
    status,
    created_at;


-- Mark job as processing
UPDATE processing_jobs
SET
    status = 'processing',
    started_at = COALESCE(started_at, NOW()),
    updated_at = NOW()
WHERE id = $1
RETURNING
    id,
    status,
    started_at,
    updated_at;


-- Mark job as completed
UPDATE processing_jobs
SET
    status = 'completed',
    result = $2,
    completed_at = NOW(),
    updated_at = NOW()
WHERE id = $1
RETURNING
    id,
    status,
    result,
    completed_at;


-- Mark job as failed
UPDATE processing_jobs
SET
    status = 'failed',
    error = $2,
    completed_at = NOW(),
    updated_at = NOW()
WHERE id = $1
RETURNING
    id,
    status,
    error,
    completed_at;